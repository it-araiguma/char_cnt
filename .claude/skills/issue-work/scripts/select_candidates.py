#!/usr/bin/env python3
"""issue-work Step 1〜2（対応するIssueの選定）の取得・絞り込みを機械的に行う。

open Issue全件をGitHub GraphQL APIでページネーションしながら辿り、
Statusおよび重要度（ラベル priority: high / medium / low またはProjectフィールド）
の絞り込みとソートを行って候補一覧を出力する。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

JST = timezone(timedelta(hours=9))
DUE_PATTERN = re.compile(r"^【\s*(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}:\d{2}))?.*?】\s*(.*)$")

PROJECT_NUMBER = 6
DEFAULT_OWNER = "it-araiguma"
DEFAULT_REPO = "char_cnt"
DEFAULT_READY_STATUSES = frozenset({"やること", "未対応"})
STATUS_PRIORITY = {"やること": 0, "未対応": 1}
PRIORITY_ORDER = {"高": 0, "中": 1, "低": 2}
LABEL_PRIORITY_MAP = {
    "priority: high": "高",
    "priority: medium": "中",
    "priority: low": "低",
    "重要度: 高": "高",
    "重要度: 中": "中",
    "重要度: 低": "低",
}

QUERY = """
query($owner:String!,$repo:String!,$pageSize:Int!,$items:Int!,$after:String){
  repository(owner:$owner,name:$repo){
    issues(states:OPEN,first:$pageSize,after:$after,orderBy:{field:CREATED_AT,direction:DESC}){
      pageInfo{hasNextPage endCursor}
      nodes{
        number title createdAt
        labels(first:20){nodes{name}}
        projectItems(first:$items){nodes{
          project{number}
          priority: fieldValueByName(name:"重要度"){
            ... on ProjectV2ItemFieldSingleSelectValue{name}
          }
          status: fieldValueByName(name:"Status"){
            ... on ProjectV2ItemFieldSingleSelectValue{name}
          }
        }}
      }
    }
  }
}
"""


class FetchError(RuntimeError):
    """GraphQL呼び出しの失敗。候補0件と区別するために専用の例外にする。"""


@dataclass
class Issue:
    number: int
    title: str
    created_at: str
    labels: list[str]
    status: str | None
    priority: str | None
    registered: bool


@dataclass
class Result:
    candidates: list[Issue] = field(default_factory=list)
    unregistered: list[int] = field(default_factory=list)
    priority_missing: list[int] = field(default_factory=list)
    excluded_status: Counter = field(default_factory=Counter)
    total_open: int = 0


def gh_graphql(owner: str, repo: str, page_size: int, after: str | None) -> dict:
    command = [
        "gh", "api", "graphql",
        "-f", f"query={QUERY}",
        "-f", f"owner={owner}",
        "-f", f"repo={repo}",
        "-F", f"pageSize={page_size}",
        "-F", "items=20",
    ]
    if after:
        command += ["-f", f"after={after}"]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode:
        raise FetchError(f"GitHub GraphQL request failed: {result.stderr.strip()}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise FetchError(f"GitHub GraphQL response was invalid: {error}") from error
    if payload.get("errors"):
        messages = "; ".join(e.get("message", "") for e in payload["errors"])
        raise FetchError(f"GitHub GraphQL returned errors: {messages}")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise FetchError("GitHub GraphQL response had no data")
    return data


def resolve_priority(project_priority: str | None, labels: list[str]) -> str | None:
    if project_priority in PRIORITY_ORDER:
        return project_priority
    for label in labels:
        if label in LABEL_PRIORITY_MAP:
            return LABEL_PRIORITY_MAP[label]
    return None


def parse_issue(node: dict) -> Issue:
    labels = [l["name"] for l in (node.get("labels") or {}).get("nodes") or [] if "name" in l]
    project_items = (node.get("projectItems") or {}).get("nodes") or []
    target_item = next(
        (i for i in project_items if (i.get("project") or {}).get("number") == PROJECT_NUMBER),
        None,
    )
    registered = target_item is not None
    status = (target_item.get("status") or {}).get("name") if registered else None
    field_priority = (target_item.get("priority") or {}).get("name") if registered else None
    priority = resolve_priority(field_priority, labels)
    return Issue(
        number=node["number"],
        title=node["title"],
        created_at=node["createdAt"],
        labels=labels,
        status=status,
        priority=priority,
        registered=registered,
    )


def fetch_all(owner: str, repo: str, page_size: int, max_pages: int) -> tuple[list[Issue], int]:
    if max_pages < 1:
        raise FetchError(f"max_pagesは1以上にする必要がある: {max_pages}")
    if not 1 <= page_size <= 100:
        raise FetchError(f"page_sizeは1〜100にする必要がある（GitHub GraphQLの上限）: {page_size}")
    issues: list[Issue] = []
    after: str | None = None
    pages = 0
    while True:
        data = gh_graphql(owner, repo, page_size, after)
        try:
            connection = data["repository"]["issues"]
            nodes = connection["nodes"]
            page_info = connection["pageInfo"]
        except (KeyError, TypeError) as error:
            raise FetchError(f"GitHub GraphQL response was unexpected: {error}") from error
        for node in nodes:
            issues.append(parse_issue(node))
        pages += 1
        if not page_info["hasNextPage"]:
            break
        if pages >= max_pages:
            raise FetchError(
                f"max_pages({max_pages})に到達したが、まだ次ページがある"
                "（取得漏れ。--max-pagesを上げて再実行する）"
            )
        after = page_info["endCursor"]
    return issues, pages


def classify(issues: list[Issue], include_statuses: set[str]) -> Result:
    allowed_statuses = set(DEFAULT_READY_STATUSES) | include_statuses
    result = Result(total_open=len(issues))
    for issue in issues:
        if not issue.registered:
            result.unregistered.append(issue.number)
            continue
        if issue.priority not in PRIORITY_ORDER:
            result.priority_missing.append(issue.number)
            continue
        if issue.status not in allowed_statuses:
            result.excluded_status[issue.status or "(未設定)"] += 1
            continue
        result.candidates.append(issue)

    result.candidates.sort(
        key=lambda i: (
            STATUS_PRIORITY.get(i.status, 99),
            PRIORITY_ORDER[i.priority],
            i.created_at,
        )
    )
    return result


def parse_due_datetime(title: str) -> tuple[datetime | None, str]:
    match = DUE_PATTERN.match(title)
    if not match:
        return None, title
    date_part, time_part, clean_title = match.groups()
    time_part = time_part or "00:00"
    try:
        dt = datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H:%M")
        return dt.replace(tzinfo=JST), clean_title
    except ValueError:
        return None, title


def is_due(title: str, now: datetime | None = None) -> tuple[bool, str]:
    if now is None:
        now = datetime.now(JST)
    due_dt, clean_title = parse_due_datetime(title)
    if due_dt is None:
        return False, title
    return now >= due_dt, clean_title


def promote_issue(issue: Issue, clean_title: str, owner: str, repo: str) -> bool:
    script_path = Path(__file__).resolve().parent / "issue_status.py"
    cmd_status = [
        sys.executable,
        str(script_path),
        "--owner",
        owner,
        "--repo",
        repo,
        "set",
        "--issue",
        str(issue.number),
        "--status",
        "やること",
    ]
    res_status = subprocess.run(cmd_status, capture_output=True, text=True, check=False)
    if res_status.returncode != 0:
        print(f"WARN: Failed to set status for #{issue.number}: {res_status.stderr.strip()}", file=sys.stderr)
        return False

    cmd_title = [
        "gh",
        "issue",
        "edit",
        str(issue.number),
        "--repo",
        f"{owner}/{repo}",
        "--title",
        clean_title,
    ]
    res_title = subprocess.run(cmd_title, capture_output=True, text=True, check=False)
    if res_title.returncode != 0:
        print(f"WARN: Failed to edit title for #{issue.number}: {res_title.stderr.strip()}", file=sys.stderr)
        return False

    return True


def promote_due_issues(
    issues: list[Issue],
    owner: str,
    repo: str,
    now: datetime | None = None,
    promoter: callable = promote_issue,
) -> list[Issue]:
    promoted: list[Issue] = []
    for issue in issues:
        if issue.status != "検討中":
            continue
        due, clean_title = is_due(issue.title, now=now)
        if not due:
            continue
        if promoter(issue, clean_title, owner, repo):
            issue.status = "やること"
            issue.title = clean_title
            promoted.append(issue)
    return promoted


def format_issue_line(issue: Issue) -> str:
    return f"#{issue.number} {issue.priority} {issue.status} {issue.title}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", default=DEFAULT_OWNER)
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument(
        "--promote-due", action="store_true",
        help="期限が過ぎた「検討中」IssueのStatusを「やること」へ昇格しタイトルから日時を除去する",
    )
    parser.add_argument(
        "--include-status", action="append", default=[], metavar="NAME",
        help="指定したStatus（例: 対応中）も候補に含める。繰り返し指定可",
    )
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument(
        "--max-pages", type=int, default=20,
        help="取得上限ページ数（既定20ページ=最大2000件）",
    )
    args = parser.parse_args(argv)

    try:
        issues, pages = fetch_all(args.owner, args.repo, args.page_size, args.max_pages)
    except FetchError as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1

    if args.promote_due:
        promoted = promote_due_issues(issues, args.owner, args.repo)
        for issue in promoted:
            print(f"PROMOTED #{issue.number} {issue.title}")

    result = classify(issues, set(args.include_status))

    for issue in result.candidates:
        print(format_issue_line(issue))

    if result.unregistered:
        print(f"UNREGISTERED count={len(result.unregistered)} issues={result.unregistered}")
    if result.priority_missing:
        print(f"PRIORITY_MISSING count={len(result.priority_missing)} issues={result.priority_missing}")
    if result.excluded_status:
        breakdown = ", ".join(f"{name}={count}" for name, count in result.excluded_status.most_common())
        print(f"EXCLUDED_STATUS {breakdown}")
    print(
        f"SUMMARY total_open={result.total_open} candidates={len(result.candidates)} pages={pages}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
