#!/usr/bin/env python3
"""Batch and single Issue creation, Project 6 registration, and priority/status verification.

Issueの起票、Project 6（char_cnt）への追加、Status（「やること」）および重要度（高・中・低）
の設定と読み戻し検証を一括で行います。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_OWNER = "it-araiguma"
DEFAULT_REPO = "char_cnt"
DEFAULT_PROJECT_ID = "PVT_kwHOAxJSE84Brsfe"  # Project 6: char_cnt

STATUS_FIELD = "Status"
TODO = "やること"
DEFAULT_STATUS = TODO

PRIORITY_FIELD = "重要度"
PRIORITIES = ("高", "中", "低")

PRIORITY_TO_LABEL: dict[str, str] = {
    "高": "priority: high",
    "中": "priority: medium",
    "低": "priority: low",
}

LABEL_TO_PRIORITY: dict[str, str] = {
    "priority: high": "高",
    "priority: medium": "中",
    "priority: low": "低",
}

FORBIDDEN_DUE_DATE_PATTERN = re.compile(
    r"【(?:\d{4}[-/年]\d{1,2}[-/月]\d{1,2}(?:日)?(?:\s*\d{1,2}:\d{2})?)(?:以降[にへ]?(?:実施|対応)?)?】"
)

ISSUE_URL_PATTERN = re.compile(r"^https://github\.com/([^/]+)/([^/]+)/issues/(\d+)/?$")


class CreateIssuesError(Exception):
    """Base exception for create_issues script."""


class ValidationError(CreateIssuesError):
    """Input validation error."""


class ExecutionError(CreateIssuesError):
    """API or subprocess execution error."""


@dataclass
class CandidateItem:
    title: str
    priority: str
    body: str | None = None
    body_file: str | None = None
    labels: list[str] = field(default_factory=list)
    status: str = "pending"
    url: str | None = None
    issue_number: int | None = None
    project_item_id: str | None = None
    verified_status: str | None = None
    verified_priority: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CandidateItem:
        labels = data.get("labels", [])
        if isinstance(labels, str):
            labels = [lbl.strip() for lbl in labels.split(",") if lbl.strip()]
        return cls(
            title=str(data.get("title", "")).strip(),
            priority=str(data.get("priority", "")).strip(),
            body=data.get("body"),
            body_file=data.get("body_file"),
            labels=labels,
            status=data.get("status", "pending"),
            url=data.get("url"),
            issue_number=data.get("issue_number"),
            project_item_id=data.get("project_item_id"),
            verified_status=data.get("verified_status"),
            verified_priority=data.get("verified_priority"),
            error=data.get("error"),
        )


def validate_candidate(candidate: CandidateItem, base_dir: Path | None = None) -> str:
    if not candidate.title:
        raise ValidationError("Issue title is required and cannot be empty")

    if FORBIDDEN_DUE_DATE_PATTERN.search(candidate.title):
        raise ValidationError(
            f"未来日付を含むタイトル '{candidate.title}' の起票は禁止されています。"
            "日付指定を外し、直ちに着手可能な課題として起票してください。"
        )

    if candidate.priority not in PRIORITIES:
        valid_priorities = ", ".join(PRIORITIES)
        raise ValidationError(
            f"Invalid priority '{candidate.priority}' for issue '{candidate.title}'. Must be one of: {valid_priorities}"
        )

    expected_label = PRIORITY_TO_LABEL[candidate.priority]
    has_matching_label = False
    for label in candidate.labels:
        normalized_label = label.strip().lower()
        if normalized_label in LABEL_TO_PRIORITY:
            label_priority = LABEL_TO_PRIORITY[normalized_label]
            if label_priority != candidate.priority:
                raise ValidationError(
                    f"重要度ラベルの不一致 '{label}' (優先度: {label_priority}) != 指定重要度 '{candidate.priority}' "
                    f"for issue '{candidate.title}'"
                )
            has_matching_label = True

    if not has_matching_label:
        candidate.labels.append(expected_label)

    body_content: str | None = None
    if candidate.body_file:
        file_path = Path(candidate.body_file)
        if not file_path.is_absolute() and base_dir is not None:
            resolved_path = (base_dir / file_path).resolve()
        else:
            resolved_path = file_path.resolve()

        if not resolved_path.exists():
            raise ValidationError(
                f"body_file '{candidate.body_file}' for issue '{candidate.title}' does not exist (resolved: {resolved_path})"
            )
        try:
            body_content = resolved_path.read_text(encoding="utf-8")
        except OSError as err:
            raise ValidationError(
                f"Failed to read body_file '{resolved_path}' for issue '{candidate.title}': {err}"
            ) from err
    elif candidate.body:
        body_content = candidate.body

    if not body_content or not body_content.strip():
        raise ValidationError(
            f"Issue body is required for '{candidate.title}' (provide body or body_file)"
        )

    return body_content


def run_gh_command(cmd: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def parse_issue_url(url: str) -> tuple[str, str, int] | None:
    match = ISSUE_URL_PATTERN.match(url.strip())
    if match:
        owner, repo, number_str = match.groups()
        return owner, repo, int(number_str)
    return None


ADD_LOOKUP_QUERY = """
query($owner:String!,$repo:String!,$number:Int!,$project:ID!){
  repository(owner:$owner,name:$repo){
    issue(number:$number){
      id
      projectItems(first:20){nodes{
        id
        project{id}
        status: fieldValueByName(name:"%s"){
          ... on ProjectV2ItemFieldSingleSelectValue{name}
        }
        priority: fieldValueByName(name:"%s"){
          ... on ProjectV2ItemFieldSingleSelectValue{name}
        }
      }}
    }
  }
  node(id:$project){
    ... on ProjectV2{
      status: field(name:"%s"){
        ... on ProjectV2SingleSelectField{id options{id name}}
      }
      priority: field(name:"%s"){
        ... on ProjectV2SingleSelectField{id options{id name}}
      }
    }
  }
}
""" % (STATUS_FIELD, PRIORITY_FIELD, STATUS_FIELD, PRIORITY_FIELD)

ADD_ITEM_MUTATION = """
mutation($project:ID!,$content:ID!){
  addProjectV2ItemById(input:{projectId:$project contentId:$content}){item{id}}
}
"""

UPDATE_FIELD_MUTATION = """
mutation($project:ID!,$item:ID!,$field:ID!,$option:String!){
  updateProjectV2ItemFieldValue(input:{
    projectId:$project itemId:$item fieldId:$field
    value:{singleSelectOptionId:$option}
  }){projectV2Item{id}}
}
"""


def gh_graphql(query: str, **variables: Any) -> dict:
    command = ["gh", "api", "graphql", "-f", f"query={query}"]
    for name, value in variables.items():
        flag = "-F" if name == "number" else "-f"
        command += [flag, f"{name}={value}"]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise ExecutionError(f"GitHub GraphQL request failed: {result.stderr.strip()}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ExecutionError(f"GitHub GraphQL response was invalid: {error}") from error
    if payload.get("errors"):
        messages = "; ".join(e.get("message", "") for e in payload["errors"])
        raise ExecutionError(f"GitHub GraphQL returned errors: {messages}")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise ExecutionError("GitHub GraphQL response had no data")
    return data


def fetch_open_issues(owner: str, repo: str) -> list[dict[str, Any]]:
    cmd = [
        "gh",
        "issue",
        "list",
        "--repo",
        f"{owner}/{repo}",
        "--state",
        "open",
        "--limit",
        "200",
        "--json",
        "number,title,url",
    ]
    code, stdout, stderr = run_gh_command(cmd)
    if code != 0:
        raise ExecutionError(f"Failed to fetch open issues for duplicate checking: {stderr or stdout}")
    try:
        items = json.loads(stdout)
        if isinstance(items, list):
            return items
        return []
    except json.JSONDecodeError as err:
        raise ExecutionError(f"Failed to parse open issues JSON: {err}") from err


def normalize_title(title: str) -> str:
    t = re.sub(r"\s+", " ", title).strip().lower()
    return t


def check_duplicates(
    candidates: list[CandidateItem],
    existing_items: list[dict[str, Any]],
) -> list[str]:
    warnings: list[str] = []
    existing_map: dict[str, dict[str, Any]] = {}
    for item in existing_items:
        raw_title = str(item.get("title", "")).strip()
        norm = normalize_title(raw_title)
        if norm:
            existing_map[norm] = item

    seen_batch: dict[str, str] = {}
    for c in candidates:
        if c.status in ("completed", "issue_created") or c.url or c.issue_number:
            continue

        norm = normalize_title(c.title)
        if norm in seen_batch:
            warnings.append(
                f"Candidate duplicate: '{c.title}' appears multiple times in input batch."
            )
        seen_batch[norm] = c.title

        if norm in existing_map:
            matched = existing_map[norm]
            matched_num = matched.get("number")
            matched_title = matched.get("title", "")
            matched_url = matched.get("url", "")
            warnings.append(
                f"Potential duplicate: Candidate '{c.title}' matches open issue "
                f"#{matched_num} '{matched_title}' ({matched_url})"
            )

    return warnings


def save_state(state_file: Path, candidates: list[CandidateItem]) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    temp_file = state_file.with_suffix(".tmp")
    data = [c.to_dict() for c in candidates]
    temp_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temp_file.replace(state_file)


def _single_select_options(field_data: dict | None, name: str) -> tuple[str, dict[str, str]]:
    if not field_data or not field_data.get("id"):
        raise ExecutionError(f"Projectに '{name}' シングルセレクトフィールドがありません")
    options = {o["name"]: o["id"] for o in field_data.get("options") or []}
    if not options:
        raise ExecutionError(f"'{name}' フィールドに選択肢がありません")
    return field_data["id"], options


def register_project_and_verify(
    owner: str,
    repo: str,
    issue_number: int,
    project_id: str,
    target_status: str,
    priority: str,
) -> tuple[str, str, str]:
    data = gh_graphql(
        ADD_LOOKUP_QUERY,
        owner=owner,
        repo=repo,
        number=issue_number,
        project=project_id,
    )
    try:
        issue = data["repository"]["issue"]
        nodes = issue["projectItems"]["nodes"]
        content_id = issue["id"]
    except (KeyError, TypeError) as error:
        raise ExecutionError(f"GitHub GraphQL response was unexpected: {error}") from error

    node_project = data.get("node") or {}
    status_field_id, status_options = _single_select_options(node_project.get("status"), STATUS_FIELD)
    priority_field_id, priority_options = _single_select_options(node_project.get("priority"), PRIORITY_FIELD)

    if priority not in priority_options:
        raise ExecutionError(
            f"不正な{PRIORITY_FIELD} {priority!r}: 利用可能={', '.join(sorted(priority_options))}"
        )

    item = next((n for n in nodes if (n.get("project") or {}).get("id") == project_id), None)
    if item is None:
        added = gh_graphql(ADD_ITEM_MUTATION, project=project_id, content=content_id)
        try:
            item_id = added["addProjectV2ItemById"]["item"]["id"]
        except (KeyError, TypeError) as error:
            raise ExecutionError(f"Projectへの追加結果が不正です: {error}") from error
        current_status = None
    else:
        item_id = item["id"]
        current_status = (item.get("status") or {}).get("name")

    resolved_status = current_status or target_status
    if resolved_status not in status_options:
        raise ExecutionError(f"不正な{STATUS_FIELD} {resolved_status!r}")

    if current_status is None:
        gh_graphql(
            UPDATE_FIELD_MUTATION,
            project=project_id,
            item=item_id,
            field=status_field_id,
            option=status_options[resolved_status],
        )

    gh_graphql(
        UPDATE_FIELD_MUTATION,
        project=project_id,
        item=item_id,
        field=priority_field_id,
        option=priority_options[priority],
    )

    verify_data = gh_graphql(
        ADD_LOOKUP_QUERY,
        owner=owner,
        repo=repo,
        number=issue_number,
        project=project_id,
    )
    try:
        v_nodes = verify_data["repository"]["issue"]["projectItems"]["nodes"]
        v_item = next((n for n in v_nodes if (n.get("project") or {}).get("id") == project_id), None)
    except (KeyError, TypeError) as error:
        raise ExecutionError(f"読み戻し検証のレスポンスが不正です: {error}") from error

    if v_item is None:
        raise ExecutionError(f"Project item not found after registration for Issue #{issue_number}")

    verified_st = (v_item.get("status") or {}).get("name")
    verified_pr = (v_item.get("priority") or {}).get("name")

    if verified_st != resolved_status or verified_pr != priority:
        raise ExecutionError(
            f"Project登録の検証に失敗しました: expected(Status={resolved_status}, 重要度={priority}) "
            f"actual(Status={verified_st}, 重要度={verified_pr})"
        )

    return item_id, verified_st, verified_pr


def process_candidates(
    candidates: list[CandidateItem],
    *,
    owner: str = DEFAULT_OWNER,
    repo: str = DEFAULT_REPO,
    project_id: str = DEFAULT_PROJECT_ID,
    state_file: Path | None = None,
    dry_run: bool = False,
    allow_duplicates: bool = False,
    base_dir: Path | None = None,
) -> list[CandidateItem]:
    validated_bodies: list[str] = []
    for c in candidates:
        if c.status == "completed" or c.url:
            validated_bodies.append("")
            continue
        body = validate_candidate(c, base_dir=base_dir)
        validated_bodies.append(body)

    existing_items = fetch_open_issues(owner, repo)
    duplicate_warnings = check_duplicates(candidates, existing_items)
    if duplicate_warnings:
        print("=== 重複検知の警告 ===", file=sys.stderr)
        for w in duplicate_warnings:
            print(f"- {w}", file=sys.stderr)
        if not allow_duplicates and not dry_run:
            raise ValidationError(
                "重複する可能性のあるIssueが検出されました。続行するには --allow-duplicates を指定してください。"
            )

    if dry_run:
        print("=== Dry-Run 計画 ===")
        for idx, (c, body) in enumerate(zip(candidates, validated_bodies), start=1):
            print(f"[{idx}/{len(candidates)}] タイトル: {c.title}")
            print(f"    重要度: {c.priority} / 初期Status: {DEFAULT_STATUS}")
            print(f"    ラベル: {', '.join(c.labels) if c.labels else '(なし)'}")
            print(f"    本文サイズ: {len(body.encode('utf-8'))} bytes")
        print("\nDry-run 完了。変更は行われていません。")
        return candidates

    for idx, (c, body) in enumerate(zip(candidates, validated_bodies), start=1):
        if c.status == "completed":
            print(
                f"[{idx}/{len(candidates)}] 既に完了済みのためスキップ: #{c.issue_number} {c.title} -> {c.url}"
            )
            continue

        target_status = DEFAULT_STATUS
        print(f"[{idx}/{len(candidates)}] 処理中: {c.title}...")

        if not c.url:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".md") as tmp:
                tmp.write(body)
                tmp_path = Path(tmp.name)
            try:
                cmd = [
                    "gh",
                    "issue",
                    "create",
                    "--repo",
                    f"{owner}/{repo}",
                    "--title",
                    c.title,
                    "--body-file",
                    str(tmp_path),
                ]
                for lbl in c.labels:
                    cmd.extend(["--label", lbl])

                code, stdout, stderr = run_gh_command(cmd)
                if code != 0:
                    c.error = f"gh issue create failed: {stderr or stdout}"
                    c.status = "failed"
                    if state_file:
                        save_state(state_file, candidates)
                    raise ExecutionError(c.error)

                created_url = stdout.strip()
                parsed = parse_issue_url(created_url)
                if not parsed:
                    c.error = f"Unexpected issue create output: {created_url}"
                    c.status = "failed"
                    if state_file:
                        save_state(state_file, candidates)
                    raise ExecutionError(c.error)

                c.url = created_url
                c.issue_number = parsed[2]
                c.status = "issue_created"
                if state_file:
                    save_state(state_file, candidates)
                print(f"    Issue作成完了: {c.url} (#{c.issue_number})")
            finally:
                if tmp_path.exists():
                    tmp_path.unlink()
        else:
            if not c.issue_number:
                parsed = parse_issue_url(c.url)
                if parsed:
                    c.issue_number = parsed[2]

        if not c.issue_number:
            raise ExecutionError(f"Issue number could not be determined for URL: {c.url}")

        try:
            item_id, verified_st, verified_pr = register_project_and_verify(
                owner=owner,
                repo=repo,
                issue_number=c.issue_number,
                project_id=project_id,
                target_status=target_status,
                priority=c.priority,
            )
            c.project_item_id = item_id
            c.verified_status = verified_st
            c.verified_priority = verified_pr
            c.status = "completed"
            c.error = None
            if state_file:
                save_state(state_file, candidates)
            print(
                f"    Project 6登録・検証完了: #{c.issue_number} Status={verified_st} 重要度={verified_pr}"
            )
        except Exception as err:
            c.error = f"Project registration failed: {err}"
            c.status = "failed"
            if state_file:
                save_state(state_file, candidates)
            raise ExecutionError(c.error) from err

    print("\n=== すべてのIssueの処理が完了しました ===")
    for c in candidates:
        print(f"#{c.issue_number} ({c.verified_status}, 重要度:{c.verified_priority}): {c.url} - {c.title}")

    return candidates


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Issueの起票、Project 6への登録、Status・重要度設定を一括実行するCLI",
    )
    parser.add_argument("--title", help="Issueタイトル（単体作成時）")
    parser.add_argument("--body", help="Issue本文（単体作成時）")
    parser.add_argument("--body-file", help="Issue本文ファイルパス（単体作成時）")
    parser.add_argument("--priority", choices=PRIORITIES, help="重要度（高／中／低）")
    parser.add_argument("--labels", help="カンマ区切りのラベル（例: bug,enhancement）")
    parser.add_argument("--file", "-f", help="候補JSONファイルのパス")
    parser.add_argument("--state-file", help="進捗追跡用状態JSONファイルのパス（再開時に使用）")
    parser.add_argument("--dry-run", action="store_true", help="作成・更新を行わず計画のみ出力")
    parser.add_argument("--allow-duplicates", action="store_true", help="重複警告があっても処理を続行")
    parser.add_argument("--owner", default=DEFAULT_OWNER, help=f"リポジトリ所有者（既定: {DEFAULT_OWNER}）")
    parser.add_argument("--repo", default=DEFAULT_REPO, help=f"リポジトリ名（既定: {DEFAULT_REPO}）")
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID, help=f"Project ID（既定: {DEFAULT_PROJECT_ID}）")

    args = parser.parse_args(argv)

    if not args.file and not args.title:
        parser.error("--file または --title のいずれかを指定してください。")

    if args.title and not args.priority:
        parser.error("--title を指定した場合、--priority は必須です。")

    return args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    candidates: list[CandidateItem] = []
    base_dir: Path | None = None
    state_path: Path | None = None

    if args.file:
        base_dir = Path(args.file).resolve().parent
    else:
        base_dir = Path.cwd()

    if args.state_file:
        state_path = Path(args.state_file).resolve()
    elif args.file:
        default_state = Path(args.file).with_suffix(".state.json").resolve()
        state_path = default_state

    if state_path and state_path.exists():
        try:
            raw_data = json.loads(state_path.read_text(encoding="utf-8"))
            if isinstance(raw_data, list):
                candidates = [CandidateItem.from_dict(item) for item in raw_data]
                print(f"状態ファイルから {len(candidates)} 件の候補を復元しました: {state_path}")
        except Exception as err:
            print(f"状態ファイルの読み込みに失敗しました: {err}", file=sys.stderr)

    if not candidates:
        if args.file:
            input_file = Path(args.file).resolve()
            if not input_file.exists():
                print(f"指定されたファイルが存在しません: {input_file}", file=sys.stderr)
                sys.exit(1)
            try:
                raw_data = json.loads(input_file.read_text(encoding="utf-8"))
                if not isinstance(raw_data, list):
                    raw_data = [raw_data]
                candidates = [CandidateItem.from_dict(item) for item in raw_data]
            except Exception as err:
                print(f"候補JSONファイルの解析に失敗しました: {err}", file=sys.stderr)
                sys.exit(1)
        else:
            labels = [lbl.strip() for lbl in (args.labels or "").split(",") if lbl.strip()]
            candidates = [
                CandidateItem(
                    title=args.title,
                    priority=args.priority,
                    body=args.body,
                    body_file=args.body_file,
                    labels=labels,
                )
            ]

    try:
        process_candidates(
            candidates,
            owner=args.owner,
            repo=args.repo,
            project_id=args.project_id,
            state_file=state_path,
            dry_run=args.dry_run,
            allow_duplicates=args.allow_duplicates,
            base_dir=base_dir,
        )
    except ValidationError as err:
        print(f"入力検証エラー: {err}", file=sys.stderr)
        sys.exit(1)
    except ExecutionError as err:
        print(f"実行エラー: {err}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
