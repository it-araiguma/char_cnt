#!/usr/bin/env python3
"""Read and update the char_cnt Project status of an issue.

複数のエージェントが並行して作業するため、着手中のIssueは
Project(project 6: char_cnt)のStatusフィールドで判別する。着手時に「対応中」へ、
完了時に「完了」へ、中断時に「やること」へ戻す運用の実体。
Project 6 の Status は「やること」「対応中」「完了」「検討中」の4つ。「未対応」は
後方互換のために受け付け、Project 側に「未対応」が無い場合は「やること」へ解決する。
起票したIssueは add で Project に追加し、Status「やること」と重要度を入れる（No Status で残さない）。
"""

from __future__ import annotations

import argparse
import json
import subprocess

PROJECT_ID = "PVT_kwHOAxJSE84Brsfe"
STATUS_FIELD = "Status"
BACKLOG = "未対応"
TODO = "やること"
IN_PROGRESS = "対応中"
DONE = "完了"
UNDER_REVIEW = "検討中"
DEFAULT_STATUS = TODO
STATUS_FALLBACKS = {
    BACKLOG: TODO,
    TODO: BACKLOG,
}
STATUSES = (TODO, BACKLOG, IN_PROGRESS, DONE, UNDER_REVIEW)
PRIORITY_FIELD = "重要度"
PRIORITIES = ("高", "中", "低")
DEFAULT_OWNER = "it-araiguma"
DEFAULT_REPO = "char_cnt"

LOOKUP = """
query($owner:String!,$repo:String!,$number:Int!,$project:ID!){
  repository(owner:$owner,name:$repo){
    issue(number:$number){
      projectItems(first:20){nodes{
        id
        project{id}
        status: fieldValueByName(name:"%s"){
          ... on ProjectV2ItemFieldSingleSelectValue{name}
        }
      }}
    }
  }
  node(id:$project){
    ... on ProjectV2{
      field(name:"%s"){
        ... on ProjectV2SingleSelectField{id options{id name}}
      }
    }
  }
}
""" % (STATUS_FIELD, STATUS_FIELD)

MUTATION = """
mutation($project:ID!,$item:ID!,$field:ID!,$option:String!){
  updateProjectV2ItemFieldValue(input:{
    projectId:$project itemId:$item fieldId:$field
    value:{singleSelectOptionId:$option}
  }){projectV2Item{id}}
}
"""

ADD_LOOKUP = """
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

ADD_ITEM = """
mutation($project:ID!,$content:ID!){
  addProjectV2ItemById(input:{projectId:$project contentId:$content}){item{id}}
}
"""

INT_VARIABLES = frozenset({"number"})


def gh_graphql(query: str, **variables: str) -> dict:
    command = ["gh", "api", "graphql", "-f", f"query={query}"]
    for name, value in variables.items():
        flag = "-F" if name in INT_VARIABLES else "-f"
        command += [flag, f"{name}={value}"]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode:
        raise SystemExit(result.stderr.strip() or "GitHub GraphQL request failed")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise SystemExit(f"GitHub GraphQL response was invalid: {error}") from error
    if payload.get("errors"):
        messages = "; ".join(e.get("message", "") for e in payload["errors"])
        raise SystemExit(f"GitHub GraphQL returned errors: {messages}")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise SystemExit("GitHub GraphQL response had no data")
    return data


def lookup(owner: str, repo: str, number: int) -> tuple[str, str | None, str, dict[str, str]]:
    """(item id, 現在のStatus, StatusフィールドのID, 選択肢名->ID) を返す。"""
    data = gh_graphql(LOOKUP, owner=owner, repo=repo, number=str(number), project=PROJECT_ID)
    try:
        nodes = data["repository"]["issue"]["projectItems"]["nodes"]
    except (KeyError, TypeError) as error:
        raise SystemExit(f"GitHub GraphQL response was unexpected: {error}") from error
    item = next((n for n in nodes if (n.get("project") or {}).get("id") == PROJECT_ID), None)
    if item is None:
        raise SystemExit(
            f"Issue #{number} は char_cnt Project(project 6)に登録されていません。"
        )
    field = (data.get("node") or {}).get("field")
    if not field or not field.get("id"):
        raise SystemExit(f"Projectに '{STATUS_FIELD}' シングルセレクトフィールドがありません")
    options = {o["name"]: o["id"] for o in field.get("options") or []}
    if not options:
        raise SystemExit(f"'{STATUS_FIELD}' フィールドに選択肢がありません")
    return item["id"], (item.get("status") or {}).get("name"), field["id"], options


def show(args: argparse.Namespace) -> None:
    _, current, _, _ = lookup(args.owner, args.repo, args.issue)
    print(current or "")


def resolve_status_option(requested: str, options: dict[str, str]) -> str:
    if requested in options:
        return requested
    fallback = STATUS_FALLBACKS.get(requested)
    if fallback and fallback in options:
        return fallback
    raise SystemExit(
        f"不正な{STATUS_FIELD} {requested!r}: 利用可能={', '.join(sorted(options))}"
    )


def set_status(args: argparse.Namespace) -> None:
    item, current, field, options = lookup(args.owner, args.repo, args.issue)
    target_status = resolve_status_option(args.status, options)
    if target_status == IN_PROGRESS and current == IN_PROGRESS and not args.force:
        raise SystemExit(
            f"Issue #{args.issue} は既に対応中です: "
            "別のエージェントが着手中の可能性があります。別のIssueを選ぶか、"
            "自分の作業だと確認できたときだけ --force を付けてください"
        )
    gh_graphql(
        MUTATION, project=PROJECT_ID, item=item, field=field, option=options[target_status]
    )
    _, verified, _, _ = lookup(args.owner, args.repo, args.issue)
    if verified != target_status:
        raise SystemExit(
            f"Project statusが更新されませんでした: expected={target_status} actual={verified}"
        )
    print(f"#{args.issue}: {current or '(未設定)'} -> {verified}")


def _single_select(field: dict | None, name: str) -> tuple[str, dict[str, str]]:
    if not field or not field.get("id"):
        raise SystemExit(f"Projectに '{name}' シングルセレクトフィールドがありません")
    options = {o["name"]: o["id"] for o in field.get("options") or []}
    if not options:
        raise SystemExit(f"'{name}' フィールドに選択肢がありません")
    return field["id"], options


def _add_lookup(owner: str, repo: str, number: int) -> tuple[str, dict | None, dict]:
    data = gh_graphql(ADD_LOOKUP, owner=owner, repo=repo, number=str(number), project=PROJECT_ID)
    try:
        issue = data["repository"]["issue"]
        nodes = issue["projectItems"]["nodes"]
        content_id = issue["id"]
    except (KeyError, TypeError) as error:
        raise SystemExit(f"GitHub GraphQL response was unexpected: {error}") from error
    item = next((n for n in nodes if (n.get("project") or {}).get("id") == PROJECT_ID), None)
    return content_id, item, data.get("node") or {}


def _value(item: dict, key: str) -> str | None:
    return (item.get(key) or {}).get("name")


def add(args: argparse.Namespace) -> None:
    content_id, item, project = _add_lookup(args.owner, args.repo, args.issue)
    status_field, status_options = _single_select(project.get("status"), STATUS_FIELD)
    priority_field, priority_options = _single_select(project.get("priority"), PRIORITY_FIELD)
    target_status = resolve_status_option(args.status, status_options)
    if args.priority not in priority_options:
        raise SystemExit(
            f"不正な{PRIORITY_FIELD} {args.priority!r}: 利用可能={', '.join(sorted(priority_options))}"
        )

    if item is None:
        added = gh_graphql(ADD_ITEM, project=PROJECT_ID, content=content_id)
        try:
            item_id = added["addProjectV2ItemById"]["item"]["id"]
        except (KeyError, TypeError) as error:
            raise SystemExit(f"Projectへの追加結果が不正です: {error}") from error
        current_status = None
    else:
        item_id = item["id"]
        current_status = _value(item, "status")

    status = current_status or target_status
    if current_status is None:
        gh_graphql(
            MUTATION, project=PROJECT_ID, item=item_id, field=status_field,
            option=status_options[status],
        )
    gh_graphql(
        MUTATION, project=PROJECT_ID, item=item_id, field=priority_field,
        option=priority_options[args.priority],
    )

    _, verified, _ = _add_lookup(args.owner, args.repo, args.issue)
    if (
        verified is None
        or _value(verified, "status") != status
        or _value(verified, "priority") != args.priority
    ):
        actual = (
            "(未登録)" if verified is None
            else f"Status={_value(verified, 'status')} 重要度={_value(verified, 'priority')}"
        )
        raise SystemExit(
            f"Projectへの登録を確認できませんでした: "
            f"expected=Status={status} 重要度={args.priority} actual={actual}"
        )
    print(f"#{args.issue}: Project 6 に登録 Status={status} 重要度={args.priority}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", default=DEFAULT_OWNER)
    parser.add_argument("--repo", default=DEFAULT_REPO)
    sub = parser.add_subparsers(dest="command", required=True)

    show_parser = sub.add_parser("show", help="現在のStatusを表示する")
    show_parser.add_argument("--issue", type=int, required=True)
    show_parser.set_defaults(func=show)

    set_parser = sub.add_parser("set", help="Statusを更新し、更新後の値を検証する")
    set_parser.add_argument("--issue", type=int, required=True)
    set_parser.add_argument("--status", required=True, choices=STATUSES)
    set_parser.add_argument(
        "--force", action="store_true", help="既に対応中のIssueへ上書きする"
    )
    set_parser.set_defaults(func=set_status)

    add_parser = sub.add_parser(
        "add", help="Projectに追加し、Status（未設定のときだけ）と重要度を入れて検証する"
    )
    add_parser.add_argument("--issue", type=int, required=True)
    add_parser.add_argument("--priority", required=True, choices=PRIORITIES)
    add_parser.add_argument("--status", default=DEFAULT_STATUS, choices=STATUSES)
    add_parser.set_defaults(func=add)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
