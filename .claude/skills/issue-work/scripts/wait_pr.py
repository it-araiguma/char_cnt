#!/usr/bin/env python3
"""issue-work Step 8: PRのチェック完了・コンフリクト確認・指摘取得を1コマンドで行う。

使い方:
    wait_pr.py --pr <PR番号> [--repo <owner/repo>] [--interval 秒] [--max-wait 秒]

終了コード:
    0: 成功（全チェックPASS、コンフリクトなし）
    1: 失敗（チェック失敗またはコンフリクトあり）
    2: タイムアウト（時間内にチェックが完了しなかった）
    4: 対象外（PRがOPENでない、ドラフトである等）
    5: システムエラー（ghコマンド失敗・タイムアウト等）
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from typing import Any

DEFAULT_REPO = "it-araiguma/char_cnt"
DEFAULT_INTERVAL_SEC = 10
DEFAULT_MAX_WAIT_SEC = 900
DEFAULT_REQUIRED_CHECKS: tuple[str, ...] = ()
AI_REVIEW_MARKER = "<!-- char-cnt-ai-review -->"
REVIEWED_SHA_PATTERN = re.compile(r"<!--\s*reviewed-sha:\s*([0-9a-f]{40})\s*-->")
COMMIT_SHA_PATTERN = re.compile(r"対象コミット:\s*([0-9a-f]{40})")
BOT_LOGINS = {"github-actions", "github-actions[bot]"}
REQUIRED_OK_CONCLUSIONS = {"SUCCESS"}
OPTIONAL_OK_CONCLUSIONS = {"SUCCESS", "SKIPPED", "NEUTRAL"}
PENDING_STATUSES = {"IN_PROGRESS", "QUEUED", "PENDING", "EXPECTED"}


class WaitPrError(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code


def run_cmd(cmd: list[str], timeout: int = 60) -> tuple[int, str, str]:
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=timeout)
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except subprocess.TimeoutExpired as error:
        raise WaitPrError(5, f"コマンドがタイムアウトしました ({timeout}秒): {' '.join(cmd[:3])}") from error


def gh_json(args: list[str], repo: str = DEFAULT_REPO) -> Any:
    full_cmd = ["gh", *args, "--repo", repo]
    code, out, err = run_cmd(full_cmd)
    if code != 0:
        raise WaitPrError(5, f"gh コマンドに失敗しました ({' '.join(args[:3])}): {err}")
    try:
        return json.loads(out)
    except json.JSONDecodeError as error:
        raise WaitPrError(5, f"gh の JSON 応答を解釈できません: {error}") from error


def get_pr_status(pr: int, repo: str = DEFAULT_REPO) -> dict[str, Any]:
    fields = "state,mergeable,mergeStateStatus,statusCheckRollup,isDraft,headRefOid"
    data = gh_json(["pr", "view", str(pr), "--json", fields], repo=repo)
    if not isinstance(data, dict):
        raise WaitPrError(5, f"PR #{pr} の応答が想定外です")
    return data


def extract_reviewed_sha(body: str) -> str | None:
    match = REVIEWED_SHA_PATTERN.search(body) or COMMIT_SHA_PATTERN.search(body)
    return match.group(1) if match else None


def get_ai_review_comment(pr: int, repo: str = DEFAULT_REPO, head_sha: str | None = None) -> str | None:
    try:
        data = gh_json(["pr", "view", str(pr), "--json", "comments"], repo=repo)
    except WaitPrError:
        return None

    comments = data.get("comments") if isinstance(data, dict) else None
    if not isinstance(comments, list):
        return None

    for comment in reversed(comments):
        if not isinstance(comment, dict):
            continue
        author = comment.get("author")
        login = author.get("login") if isinstance(author, dict) else ""
        if login not in BOT_LOGINS:
            continue
        body = (comment.get("body") or "").strip()
        if not body.startswith(AI_REVIEW_MARKER):
            continue
        if head_sha is not None and extract_reviewed_sha(body) != head_sha:
            continue
        return body

    return None


def parse_check_item(item: dict[str, Any]) -> tuple[str, bool, str]:
    name = item.get("name") or item.get("context") or "(名称不明)"
    status = (item.get("status") or "").upper()
    state = (item.get("state") or "").upper()
    conclusion = (item.get("conclusion") or "").upper()

    if status:
        is_completed = status == "COMPLETED"
    elif state:
        is_completed = state not in PENDING_STATUSES
    else:
        is_completed = True

    result = conclusion if conclusion else (state if state else "(不明)")
    return name, is_completed, result


def evaluate_checks(
    pr_data: dict[str, Any],
    required_checks: tuple[str, ...] = DEFAULT_REQUIRED_CHECKS,
) -> tuple[bool, list[dict[str, Any]]]:
    rollup = pr_data.get("statusCheckRollup") or []
    if not isinstance(rollup, list):
        rollup = []

    existing_check_names = {
        item.get("name") or item.get("context")
        for item in rollup
        if isinstance(item, dict)
    }
    if required_checks and not all(name in existing_check_names for name in required_checks):
        return False, rollup

    for item in rollup:
        if not isinstance(item, dict):
            continue
        _, is_completed, _ = parse_check_item(item)
        if not is_completed:
            return False, rollup

    return True, rollup


def wait_for_pr(
    pr: int,
    repo: str = DEFAULT_REPO,
    interval: int = DEFAULT_INTERVAL_SEC,
    max_wait: int = DEFAULT_MAX_WAIT_SEC,
    required_checks: tuple[str, ...] = DEFAULT_REQUIRED_CHECKS,
) -> int:
    req_desc = ", ".join(required_checks) if required_checks else "登録済みチェック"
    print(
        f"[wait_pr] PR #{pr} のチェック完了を待機中 "
        f"(最大 {max_wait} 秒, 間隔 {interval} 秒, 対象: {req_desc})...",
        flush=True,
    )

    start_time = time.time()
    last_pr_data: dict[str, Any] = {}

    while True:
        elapsed = time.time() - start_time
        if elapsed > max_wait:
            print(f"[wait_pr] タイムアウト: {max_wait} 秒以内にチェックが完了しませんでした", flush=True)
            return 2

        try:
            pr_data = get_pr_status(pr, repo=repo)
        except WaitPrError as e:
            print(f"[wait_pr] エラー: {e.args[0]}", file=sys.stderr, flush=True)
            return e.code

        last_pr_data = pr_data

        state = pr_data.get("state")
        if state != "OPEN":
            print(f"[wait_pr] PR #{pr} は OPEN ではありません (state={state})", flush=True)
            return 4

        if pr_data.get("isDraft"):
            print(f"[wait_pr] PR #{pr} はドラフトです", flush=True)
            return 4

        completed, _ = evaluate_checks(pr_data, required_checks=required_checks)
        mergeable = (pr_data.get("mergeable") or "").upper()
        if completed and mergeable != "UNKNOWN":
            break

        time.sleep(interval)

    rollup = last_pr_data.get("statusCheckRollup") or []
    mergeable = (last_pr_data.get("mergeable") or "").upper()
    merge_status = (last_pr_data.get("mergeStateStatus") or "").upper()

    problems: list[str] = []
    if mergeable != "MERGEABLE" or merge_status == "DIRTY":
        problems.append(
            f"マージ可能ではありません (mergeable={mergeable or '(空)'}, mergeStateStatus={merge_status or '(空)'})"
        )

    check_results: list[tuple[str, str, bool]] = []
    has_ai_review_failure = False

    for item in rollup:
        if not isinstance(item, dict):
            continue
        name, _, result = parse_check_item(item)
        if name in required_checks:
            is_ok = result in REQUIRED_OK_CONCLUSIONS
        else:
            is_ok = result in OPTIONAL_OK_CONCLUSIONS

        check_results.append((name, result, is_ok))
        if not is_ok:
            problems.append(f"チェック '{name}' が成功していません (result={result})")
            if "AI Code Review" in name:
                has_ai_review_failure = True

    if not problems:
        print(f"[wait_pr] 成功: 全チェックが通過し、マージ可能です (mergeable={mergeable}, status={merge_status})", flush=True)
        for name, result, _ in check_results:
            print(f"  - {name}: {result}", flush=True)
        return 0

    print("[wait_pr] 失敗: チェックの失敗またはコンフリクトが検出されました", flush=True)
    for p in problems:
        print(f"  - {p}", flush=True)

    if check_results:
        print("\n[チェック結果一覧]", flush=True)
        for name, result, is_ok in check_results:
            mark = "PASS" if is_ok else "FAIL"
            print(f"  [{mark}] {name}: {result}", flush=True)

    head_sha = last_pr_data.get("headRefOid") or None
    ai_comment = get_ai_review_comment(pr, repo=repo, head_sha=head_sha)
    if ai_comment:
        print("\n" + "=" * 50, flush=True)
        print("[AIコードレビュー サマリコメント]", flush=True)
        print("=" * 50, flush=True)
        print(ai_comment, flush=True)
        print("=" * 50, flush=True)
    elif has_ai_review_failure:
        print(f"\n[wait_pr] AI Code Review の現行HEAD ({(head_sha or '不明')[:7]}) のサマリコメントを取得できませんでした", flush=True)

    return 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr", type=int, required=True, help="対象のPR番号")
    parser.add_argument("--repo", default=DEFAULT_REPO, help=f"対象リポジトリ (既定: {DEFAULT_REPO})")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_SEC, help=f"チェック間隔(秒) (既定: {DEFAULT_INTERVAL_SEC})")
    parser.add_argument("--max-wait", type=int, default=DEFAULT_MAX_WAIT_SEC, help=f"最大待機時間(秒) (既定: {DEFAULT_MAX_WAIT_SEC})")
    args = parser.parse_args()

    code = wait_for_pr(
        pr=args.pr,
        repo=args.repo,
        interval=args.interval,
        max_wait=args.max_wait,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
