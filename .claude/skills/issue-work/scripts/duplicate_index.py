#!/usr/bin/env python3
"""issue-workの重複確認で候補索引と必要本文を分離して提供する。"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_OWNER = "it-araiguma"
DEFAULT_REPO = "char_cnt"
CACHE_FILE_NAME = "issue-work-duplicate-cache.json"
MAX_BODY_BYTES_DEFAULT = 8192

OPEN_ISSUES_PRS_QUERY = """
query($owner:String!,$repo:String!,$pageSize:Int!,$issueCursor:String,$prCursor:String){
  repository(owner:$owner,name:$repo){
    issues(states:OPEN,first:$pageSize,after:$issueCursor,orderBy:{field:UPDATED_AT,direction:DESC}){
      totalCount
      pageInfo{hasNextPage endCursor}
      nodes{
        number title updatedAt createdAt url
        labels(first:10){nodes{name}}
      }
    }
    pullRequests(states:OPEN,first:$pageSize,after:$prCursor,orderBy:{field:UPDATED_AT,direction:DESC}){
      totalCount
      pageInfo{hasNextPage endCursor}
      nodes{
        number title updatedAt createdAt url
        labels(first:10){nodes{name}}
      }
    }
  }
}
"""

SEARCH_QUERY = """
query($searchQuery:String!,$pageSize:Int!,$cursor:String){
  search(query:$searchQuery,type:ISSUE,first:$pageSize,after:$cursor){
    issueCount
    pageInfo{hasNextPage endCursor}
    nodes{
      ... on Issue{
        number title state updatedAt createdAt url
        labels(first:10){nodes{name}}
      }
      ... on PullRequest{
        number title state updatedAt createdAt url
        labels(first:10){nodes{name}}
      }
    }
  }
}
"""


class DuplicateIndexError(Exception):
    """取得・処理失敗時の例外。"""


@dataclass
class ItemSummary:
    number: int
    kind: str  # "issue" | "pr"
    state: str  # "OPEN" | "CLOSED" | "MERGED"
    title: str
    updated_at: str
    url: str
    labels: list[str] = field(default_factory=list)

    def to_line(self, show_url: bool = False) -> str:
        date_str = self.updated_at[:10] if len(self.updated_at) >= 10 else self.updated_at
        label_str = f" [{', '.join(self.labels)}]" if self.labels else ""
        url_str = f" {self.url}" if show_url else ""
        return f"#{self.number} [{self.kind}/{self.state}] {date_str}{url_str} {self.title}{label_str}"


def get_git_head_sha() -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except subprocess.SubprocessError:
        return "UNKNOWN"


def get_cache_path() -> Path:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            check=True,
        )
        git_dir = Path(res.stdout.strip())
        return git_dir / CACHE_FILE_NAME
    except subprocess.SubprocessError:
        return Path(".git") / CACHE_FILE_NAME


def run_gh_graphql(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        if isinstance(v, int) or v is not None:
            cmd.extend(["-F", f"{k}={v}"])
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
        data = json.loads(proc.stdout)
        if not isinstance(data, dict) or data.get("errors"):
            raise DuplicateIndexError("API応答が不完全です")
        return data
    except (OSError, subprocess.TimeoutExpired) as e:
        raise DuplicateIndexError(f"GitHub API取得中断: {e}") from e
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.strip() or e.stdout.strip() or str(e)
        raise DuplicateIndexError(f"GitHub API呼び出し失敗: {err_msg}") from e
    except json.JSONDecodeError as e:
        raise DuplicateIndexError(f"API応答のJSON解析失敗: {e}") from e


def fetch_open_items(
    owner: str = DEFAULT_OWNER,
    repo: str = DEFAULT_REPO,
    page_size: int = 100,
    max_pages: int = 10,
) -> tuple[list[ItemSummary], bool, str | None]:
    items: list[ItemSummary] = []
    issue_cursor: str | None = None
    pr_cursor: str | None = None
    has_more_issues = True
    has_more_prs = True
    page_count = 0
    totals = {}

    while (has_more_issues or has_more_prs) and page_count < max_pages:
        page_count += 1
        variables: dict[str, Any] = {
            "owner": owner,
            "repo": repo,
            "pageSize": page_size,
        }
        if issue_cursor:
            variables["issueCursor"] = issue_cursor
        if pr_cursor:
            variables["prCursor"] = pr_cursor

        data = run_gh_graphql(OPEN_ISSUES_PRS_QUERY, variables)
        repo_data = data.get("data", {}).get("repository")
        if not repo_data:
            return items, False, "リポジトリデータが存在しません"

        issues_data = repo_data.get("issues", {})
        prs_data = repo_data.get("pullRequests", {})

        for kind, connection in (("issue", issues_data), ("pr", prs_data)):
            total = connection.get("totalCount")
            info = connection.get("pageInfo")
            if type(total) is not int or total < 0 or not isinstance(info, dict) or type(info.get("hasNextPage")) is not bool:
                return items, False, "総件数・ページ情報が不明です"
            if kind in totals and totals[kind] != total:
                return items, False, "取得中に総件数が変化しました"
            totals[kind] = total
            if info["hasNextPage"] and not info.get("endCursor"):
                return items, False, "次ページのcursorが不明です"

        if has_more_issues:
            for node in issues_data.get("nodes", []):
                labels = [l["name"] for l in node.get("labels", {}).get("nodes", [])]
                items.append(
                    ItemSummary(
                        number=node["number"],
                        kind="issue",
                        state="OPEN",
                        title=node["title"],
                        updated_at=node["updatedAt"],
                        url=node["url"],
                        labels=labels,
                    )
                )
            page_info = issues_data.get("pageInfo", {})
            has_more_issues = page_info.get("hasNextPage", False)
            issue_cursor = page_info.get("endCursor")

        if has_more_prs:
            for node in prs_data.get("nodes", []):
                labels = [l["name"] for l in node.get("labels", {}).get("nodes", [])]
                items.append(
                    ItemSummary(
                        number=node["number"],
                        kind="pr",
                        state="OPEN",
                        title=node["title"],
                        updated_at=node["updatedAt"],
                        url=node["url"],
                        labels=labels,
                    )
                )
            page_info = prs_data.get("pageInfo", {})
            has_more_prs = page_info.get("hasNextPage", False)
            pr_cursor = page_info.get("endCursor")

    if has_more_issues or has_more_prs:
        return items, False, f"最大ページ数（{max_pages}）に達しましたが、未取得のアイテムが残っています"

    for kind, total in totals.items():
        found = [item.number for item in items if item.kind == kind]
        if len(found) != total or len(set(found)) != total:
            return items, False, f"{kind} total={total} fetched={len(found)} 件数不一致"
    return items, True, None


def search_items(
    query_str: str,
    owner: str = DEFAULT_OWNER,
    repo: str = DEFAULT_REPO,
    include_closed: bool = True,
    page_size: int = 50,
    max_pages: int = 5,
) -> tuple[list[ItemSummary], bool, str | None]:
    items: list[ItemSummary] = []
    cursor: str | None = None
    page_count = 0
    has_more = True
    expected_total = None

    qualifiers = [f"repo:{owner}/{repo}"]
    if not include_closed:
        qualifiers.append("state:open")
    if query_str and query_str.strip():
        qualifiers.append(query_str.strip())
    full_search_query = " ".join(qualifiers)

    while has_more and page_count < max_pages:
        page_count += 1
        variables: dict[str, Any] = {
            "searchQuery": full_search_query,
            "pageSize": page_size,
        }
        if cursor:
            variables["cursor"] = cursor

        data = run_gh_graphql(SEARCH_QUERY, variables)
        search_data = data.get("data", {}).get("search")
        if not search_data:
            return items, False, "検索データが存在しません"

        total = search_data.get("issueCount")
        info = search_data.get("pageInfo")
        context = f"query={full_search_query!r} total={total} fetched={len(items)} page_limit={max_pages} api_cap=1000"
        if type(total) is not int or total < 0 or not isinstance(info, dict) or type(info.get("hasNextPage")) is not bool:
            return items, False, f"{context} 件数・ページ情報が不明"
        if total >= 1000:
            return items, False, f"{context} 検索上限到達"
        if expected_total is not None and expected_total != total:
            return items, False, f"{context} 取得中に総件数が変化"
        expected_total = total
        if info["hasNextPage"] and (not info.get("endCursor") or info.get("endCursor") == cursor):
            return items, False, f"{context} 次ページcursorが不正"

        for node in search_data.get("nodes", []):
            if not node:
                continue
            labels = [l["name"] for l in node.get("labels", {}).get("nodes", [])]
            url = node.get("url", "")
            kind = "pr" if "/pull/" in url else "issue"
            items.append(
                ItemSummary(
                    number=node["number"],
                    kind=kind,
                    state=node.get("state", "UNKNOWN"),
                    title=node["title"],
                    updated_at=node.get("updatedAt", ""),
                    url=url,
                    labels=labels,
                )
            )

        page_info = search_data.get("pageInfo", {})
        has_more = page_info.get("hasNextPage", False)
        cursor = page_info.get("endCursor")

    if has_more:
        return items, False, f"最大検索ページ数（{max_pages}）に達しましたが、未取得の検索結果が残っています"

    if len(items) != expected_total or len({(item.kind, item.number) for item in items}) != expected_total:
        return items, False, f"query={full_search_query!r} total={expected_total} fetched={len(items)} 件数不一致"
    return items, True, None


def load_cached_index(session_id: str | None, head_sha: str) -> list[ItemSummary] | None:
    if not session_id:
        return None
    cache_path = get_cache_path()
    if not cache_path.exists():
        return None
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("completeness_version") != 1:
            return None
        if data.get("session_id") != session_id:
            return None
        if data.get("head_sha") != head_sha:
            return None
        if time.time() - data.get("timestamp", 0) > 3600:
            return None
        return [ItemSummary(**item) for item in data.get("items", [])]
    except (OSError, json.JSONDecodeError, KeyError, TypeError, AttributeError):
        return None


def save_cached_index(session_id: str | None, head_sha: str, items: list[ItemSummary]) -> None:
    if not session_id:
        return
    cache_path = get_cache_path()
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "completeness_version": 1,
            "session_id": session_id,
            "head_sha": head_sha,
            "timestamp": time.time(),
            "items": [asdict(item) for item in items],
        }
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=cache_path.parent, delete=False) as f:
            temp_path = Path(f.name)
            try:
                json.dump(data, f, ensure_ascii=False)
                f.close()
                os.replace(temp_path, cache_path)
            finally:
                temp_path.unlink(missing_ok=True)
    except OSError:
        pass


def normalize_queries(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw.strip()] if raw.strip() else []
    if isinstance(raw, (list, tuple)):
        return [item.strip() for item in raw if isinstance(item, str) and item.strip()]
    return []


def item_matches_title_or_labels(item: ItemSummary, queries: list[str]) -> bool:
    if not queries:
        return False
    target_text = f"{item.number} {item.title} {' '.join(item.labels)}".lower()
    for q in queries:
        words = [w.lower() for w in q.split() if w.strip()]
        if words and all(word in target_text for word in words):
            return True
    return False


def filter_items_by_query(items: list[ItemSummary], query: str | list[str]) -> list[ItemSummary]:
    queries = normalize_queries(query)
    if not queries:
        return items
    return [item for item in items if item_matches_title_or_labels(item, queries)]


def fetch_body_for_number(
    number: int,
    owner: str = DEFAULT_OWNER,
    repo: str = DEFAULT_REPO,
    max_bytes: int = MAX_BODY_BYTES_DEFAULT,
) -> tuple[str, bool, str | None]:
    cmd = ["gh", "issue", "view", str(number), "--repo", f"{owner}/{repo}", "--json", "number,title,body,state,url"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(proc.stdout)
    except subprocess.CalledProcessError as e:
        err = e.stderr.strip() or e.stdout.strip()
        return "", False, f"取得失敗 (#{number}): {err}"
    except (OSError, json.JSONDecodeError, KeyError) as e:
        return "", False, f"予期せぬエラー (#{number}): {e}"

    body = data.get("body") or ""
    if not body:
        return "[BODY_EMPTY]", True, None

    body_bytes = len(body.encode("utf-8"))
    if body_bytes > max_bytes:
        truncated_body = body.encode("utf-8")[:max_bytes].decode("utf-8", errors="ignore")
        trunc_msg = f"[TRUNCATED: original {body_bytes} bytes, showing first {max_bytes} bytes]\n"
        return trunc_msg + truncated_body, True, None

    return body, True, None


def cmd_index(args: argparse.Namespace) -> int:
    head_sha = get_git_head_sha()
    session_id = args.session_id
    queries = normalize_queries(args.query)

    if args.include_closed:
        try:
            if not queries:
                items, is_complete, err = search_items(
                    query_str="",
                    owner=args.owner,
                    repo=args.repo,
                    include_closed=True,
                    page_size=args.page_size,
                    max_pages=args.max_pages,
                )
            else:
                items = []
                seen_keys: set[tuple[str, int]] = set()
                is_complete = True
                err = None
                for q in queries:
                    q_items, q_complete, q_err = search_items(
                        query_str=q,
                        owner=args.owner,
                        repo=args.repo,
                        include_closed=True,
                        page_size=args.page_size,
                        max_pages=args.max_pages,
                    )
                    if not q_complete:
                        is_complete = False
                        err = f"クエリ '{q}' の検索不完全: {q_err}"
                        break
                    for item in q_items:
                        key = (item.kind, item.number)
                        if key not in seen_keys:
                            seen_keys.add(key)
                            items.append(item)
        except (DuplicateIndexError, KeyError, TypeError, ValueError, AttributeError) as e:
            print(f"STATUS=INCOMPLETE (検索エラー: {e})", file=sys.stderr)
            return 1
    else:
        cached = (
            None
            if args.no_cache or (args.owner, args.repo) != (DEFAULT_OWNER, DEFAULT_REPO)
            else load_cached_index(session_id, head_sha)
        )
        if cached is not None:
            items = cached
            is_complete = True
            err = None
        else:
            try:
                items, is_complete, err = fetch_open_items(
                    owner=args.owner,
                    repo=args.repo,
                    page_size=args.page_size,
                    max_pages=args.max_pages,
                )
                if is_complete and (args.owner, args.repo) == (DEFAULT_OWNER, DEFAULT_REPO):
                    save_cached_index(session_id, head_sha, items)
            except (DuplicateIndexError, KeyError, TypeError, ValueError, AttributeError) as e:
                print(f"STATUS=INCOMPLETE (APIエラー: {e})", file=sys.stderr)
                return 1

        if queries:
            items = filter_items_by_query(items, queries)

    items.sort(key=lambda x: x.updated_at, reverse=True)

    if not is_complete:
        print(f"STATUS=INCOMPLETE (途中終了: {err})", file=sys.stderr)
        return 1

    if not items:
        print("NO_MATCHES: 検索結果は0件です。")
        print("SUMMARY total_items=0 matched=0 status=COMPLETE")
        return 0

    raw_limit = getattr(args, "limit", 50)
    limit = max(raw_limit if isinstance(raw_limit, int) else 50, 0)

    if queries:
        title_matches = [it for it in items if item_matches_title_or_labels(it, queries)]
        body_matches = [it for it in items if not item_matches_title_or_labels(it, queries)]
    else:
        title_matches = items
        body_matches = []

    if limit > 0 and len(body_matches) > limit:
        displayed_body_matches = body_matches[:limit]
        omitted_count = len(body_matches) - limit
    else:
        displayed_body_matches = body_matches
        omitted_count = 0

    displayed_items = title_matches + displayed_body_matches
    show_url = bool(getattr(args, "show_url", False))
    for item in displayed_items:
        print(item.to_line(show_url=show_url))

    if omitted_count > 0:
        print(
            f"SUMMARY matched={len(items)} displayed={len(displayed_items)} omitted={omitted_count} status=COMPLETE"
        )
    else:
        print(f"SUMMARY matched={len(items)} status=COMPLETE")
    return 0


def cmd_body(args: argparse.Namespace) -> int:
    has_error = False
    for num in args.numbers:
        body_text, ok, err = fetch_body_for_number(num, owner=args.owner, repo=args.repo, max_bytes=args.max_bytes)
        if not ok:
            print(f"=== #{num} ===")
            print(f"[NOT_FOUND / ERROR] {err}")
            print(f"=== END #{num} ===\n")
            has_error = True
            continue

        body_len = len(body_text.encode("utf-8"))
        print(f"=== #{num} ({body_len} bytes) ===")
        print(body_text)
        print(f"=== END #{num} ===\n")

    return 1 if has_error else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="issue-work用 重複確認インデックス・本文取得ツール"
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    parser_index = subparsers.add_parser("index", help="候補索引の取得・検索")
    parser_index.add_argument("--query", "-q", action="append", default=None, help="検索クエリ")
    parser_index.add_argument("--limit", type=int, default=50, help="表示上限件数")
    parser_index.add_argument("--show-url", action="store_true", help="各行にURLを含めて出力")
    parser_index.add_argument("--include-closed", action="store_true", help="close済みも含めて検索")
    parser_index.add_argument("--session-id", default=None, help="セッションID")
    parser_index.add_argument("--no-cache", action="store_true", help="キャッシュを使用しない")
    parser_index.add_argument("--owner", default=DEFAULT_OWNER, help="リポジトリオーナー")
    parser_index.add_argument("--repo", default=DEFAULT_REPO, help="リポジトリ名")
    parser_index.add_argument("--page-size", type=int, default=100, help="1ページあたりの取得件数")
    parser_index.add_argument("--max-pages", type=int, default=10, help="最大取得ページ数")

    parser_body = subparsers.add_parser("body", help="指定Issue/PRの本文取得")
    parser_body.add_argument("numbers", type=int, nargs="+", help="取得するIssue/PR番号")
    parser_body.add_argument("--owner", default=DEFAULT_OWNER, help="リポジトリオーナー")
    parser_body.add_argument("--repo", default=DEFAULT_REPO, help="リポジトリ名")
    parser_body.add_argument("--max-bytes", type=int, default=MAX_BODY_BYTES_DEFAULT, help="本文最大出力バイト数")

    args = parser.parse_args(argv)

    if args.subcommand == "index":
        return cmd_index(args)
    elif args.subcommand == "body":
        return cmd_body(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
