#!/usr/bin/env python3
"""issue-work Step 10〜12（マージ〜片付け〜本番デプロイ・外形確認〜Issueクローズ・「完了」更新）を1回で行う。

使い方:
    finish.py --pr <PR番号> --issue <Issue番号> [--worktree <path>] [--branch <name>]
              [--skip-deploy] [--max-wait 秒] [--interval 秒]

段階（各段の結果を1行ずつ出力し、失敗した段で止まる）:
  1. precheck : PRがOPEN・コンフリクトなし・必須チェック失敗/実行中なし・
                worktreeに未コミット/未pushの変更が無いことを確認する
                （満たさなければ何も変更せず終了コード4）
  2. merge    : squashマージしてリモートブランチを削除する（マージ済みならスキップ）
  3. cleanup  : worktree除去・リモート/ローカルの作業ブランチ削除・メインのfast-forward
  4. main-ci  : GitHub Actions ワークフローが存在する場合のみ、マージコミットに対するpush CIを待つ
  5. deploy   : ローカルで PWA ビルドを実行し、成果物を VPS（/home/appuser/public_html/char_cnt）へ転送。
                VPS 側では flock 排他制御下で git リポジトリ同期と dist/pwa のアトミック置換を行い、
                https://count.it-araiguma.com/ の HTTP 200 外形確認を行う（--skip-deploy 指定時はスキップ）
  6. issue    : Issueがcloseされていなければcloseする
  7. status   : Project 6のStatusを「完了」にして読み戻す

再実行しても二重マージ・二重更新にならない（各段は現在の状態を見て冪等に動く）。

終了コード:
  0: 完了
  1: mainのCIまたは本番デプロイ・外形確認が失敗した（Statusは「対応中」のまま）
  2: mainのCIが制限時間内に終わらなかった（再実行で続きから）
  4: マージ前の条件を満たさない（何も変更していない）
  5: マージ・片付け・Issue/Status更新に失敗した
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any

REPO = "it-araiguma/char_cnt"
DONE = "完了"
IN_PROGRESS = "対応中"
OK_CONCLUSIONS = {"SUCCESS", "SKIPPED", "NEUTRAL"}
PROD_URL = "https://count.it-araiguma.com/"
VPS_HOST = "vps"
VPS_REPO_DIR = "/home/appuser/public_html/char_cnt"

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import issue_status  # noqa: E402


class Stop(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code


def run(cmd: list[str], cwd: str | Path | None = None, timeout: int = 300) -> tuple[int, str, str]:
    res = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        cwd=cwd,
        timeout=timeout,
        stdin=subprocess.DEVNULL,
    )
    return res.returncode, res.stdout.strip(), res.stderr.strip()


def say(stage: str, message: str) -> None:
    print(f"[finish:{stage}] {message}", flush=True)


def gh_json(args: list[str]) -> Any:
    code, out, err = run(["gh", *args])
    if code != 0:
        raise Stop(5, f"gh {' '.join(args[:3])} に失敗しました: {err}")
    try:
        return json.loads(out)
    except json.JSONDecodeError as error:
        raise Stop(5, f"gh の応答を解釈できません: {error}") from error


def repo_root() -> str:
    code, out, err = run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"])
    if code != 0 or not out:
        raise Stop(5, f"git のルートを特定できません: {err}")
    return str(Path(out).parent)


def detect_worktree(root: str, issue: int, branch: str | None = None) -> str | None:
    code, out, _ = run(["git", "-C", root, "worktree", "list", "--porcelain"])
    entries: list[dict[str, str]] = []
    if code == 0:
        current_entry: dict[str, str] = {}
        for line in out.splitlines():
            if line.startswith("worktree "):
                if current_entry:
                    entries.append(current_entry)
                current_entry = {"worktree": line.removeprefix("worktree ").strip()}
            elif line.startswith("branch "):
                current_entry["branch"] = line.removeprefix("branch ").strip()
        if current_entry:
            entries.append(current_entry)

    root_resolved = Path(root).resolve()

    if branch:
        norm_branch = branch if branch.startswith("refs/heads/") else f"refs/heads/{branch}"
        for e in entries:
            if e.get("branch") == norm_branch:
                wt_path = Path(e["worktree"])
                if wt_path.resolve() != root_resolved:
                    return str(wt_path.resolve())

    prefix = f"issue-{issue}-"
    for e in entries:
        wt_path = Path(e["worktree"])
        if (wt_path.name.startswith(prefix) or f"issue-{issue}" in wt_path.name) and wt_path.resolve() != root_resolved:
            return str(wt_path.resolve())

    pattern = str(Path(root) / ".claude" / "worktrees" / f"issue-{issue}-*")
    matches = glob.glob(pattern)
    for m in matches:
        p = Path(m)
        if p.is_dir() and p.resolve() != root_resolved:
            return str(p.resolve())

    return None


def view_pr(pr: int) -> dict[str, Any]:
    fields = "state,mergeable,mergeStateStatus,statusCheckRollup,headRefName,headRefOid,mergeCommit,isDraft"
    data = gh_json(["pr", "view", str(pr), "--repo", REPO, "--json", fields])
    if not isinstance(data, dict):
        raise Stop(5, f"PR #{pr} の応答が想定外です")
    return data


def check_problems(pr: dict[str, Any], worktree: str | None = None) -> list[str]:
    problems: list[str] = []
    if pr.get("state") != "OPEN":
        problems.append(f"PRがOPENではありません（state={pr.get('state')}）")
    if pr.get("isDraft"):
        problems.append("PRがドラフトです")
    if pr.get("mergeable") == "CONFLICTING" or pr.get("mergeStateStatus") == "DIRTY":
        problems.append(
            f"コンフリクトがあります（mergeable={pr.get('mergeable')}, mergeStateStatus={pr.get('mergeStateStatus')}）"
        )
    for item in pr.get("statusCheckRollup") or []:
        if not isinstance(item, dict):
            continue
        name = item.get("name") or item.get("context") or "(名称不明)"
        status = (item.get("status") or "").upper()
        conclusion = (item.get("conclusion") or "").upper()
        if status in {"IN_PROGRESS", "QUEUED", "PENDING", "EXPECTED"}:
            problems.append(f"チェック {name} が完了していません（status={status}）")
        elif conclusion and conclusion not in OK_CONCLUSIONS:
            problems.append(f"チェック {name} が {conclusion} です")

    if worktree and Path(worktree).exists():
        code, out, _ = run(["git", "-C", worktree, "status", "--porcelain"])
        if code != 0:
            problems.append(f"worktree の git status 取得に失敗しました: {worktree}")
        elif out.strip():
            problems.append("worktree に未コミットの変更が残っています")

    return problems


def merge(pr: int, data: dict[str, Any], worktree: str | None) -> dict[str, Any]:
    if data.get("state") == "MERGED":
        say("precheck", f"PR #{pr} は既にマージ済み")
        return data

    problems = check_problems(data, worktree)
    if problems:
        for p in problems:
            say("precheck", f"NG: {p}")
        raise Stop(4, "マージ前の条件を満たしません")
    say("precheck", "OK: マージ条件充足（コンフリクトなし、未コミット変更なし）")

    code, out, err = run(["gh", "pr", "merge", str(pr), "--repo", REPO, "--squash", "--delete-branch"])
    if code != 0:
        raise Stop(5, f"PR #{pr} のマージに失敗しました: {err or out}")
    say("merge", f"PR #{pr} を squash マージしました")
    return view_pr(pr)


def cleanup(root: str, branch: str, worktree: str | None) -> None:
    if worktree:
        resolved = str(Path(worktree).resolve())
        code, out, _ = run(["git", "-C", root, "worktree", "list", "--porcelain"])
        if code == 0 and any(line.removeprefix("worktree ") == resolved for line in out.splitlines() if line.startswith("worktree ")):
            code, _, err = run(["git", "-C", root, "worktree", "remove", "--force", resolved])
            if code != 0:
                raise Stop(5, f"worktree {resolved} を削除できません: {err}")
            say("cleanup", f"worktree削除: {resolved}")
        elif Path(resolved).exists():
            shutil.rmtree(resolved, ignore_errors=True)
            say("cleanup", f"worktreeディレクトリ削除: {resolved}")
        run(["git", "-C", root, "worktree", "prune"])

    code, _, err = run(["git", "-C", root, "fetch", "origin", "main"])
    if code != 0:
        say("cleanup", f"警告: origin/main の fetch に失敗しました: {err}")

    code, current, _ = run(["git", "-C", root, "branch", "--show-current"])
    if code == 0 and current == "main":
        code, _, err = run(["git", "-C", root, "merge", "--ff-only", "origin/main"])
        say("cleanup", "メインを origin/main へfast-forward" if code == 0 else f"警告: fast-forwardできません: {err}")
    else:
        say("cleanup", f"メインは {current or '(detached)'} のため更新しません")

    if branch and run(["git", "-C", root, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"])[0] == 0:
        code, _, err = run(["git", "-C", root, "branch", "-D", branch])
        if code != 0:
            say("cleanup", f"警告: ローカルブランチを削除できません: {err}")
        else:
            say("cleanup", f"ローカルブランチ削除: {branch}")


def is_run_completed(r: dict[str, Any]) -> bool:
    return (r.get("status") or "").upper() == "COMPLETED"


def is_run_success(r: dict[str, Any]) -> bool:
    return (r.get("conclusion") or "").upper() in OK_CONCLUSIONS


def wait_main_ci(root: str, sha: str, max_wait: int, interval: int) -> None:
    workflows_dir = Path(root) / ".github" / "workflows"
    if not workflows_dir.is_dir() or (not any(workflows_dir.glob("*.yml")) and not any(workflows_dir.glob("*.yaml"))):
        say("main-ci", "CIワークフローが存在しないためCI待機をスキップします")
        return

    deadline = time.monotonic() + max_wait
    while True:
        runs = gh_json([
            "run", "list", "--repo", REPO, "--event", "push",
            "--commit", sha, "--json", "databaseId,status,conclusion,url",
        ])
        if runs:
            latest = max(runs, key=lambda r: r.get("databaseId") or 0)
            if is_run_completed(latest):
                if is_run_success(latest):
                    say("main-ci", f"成功: {latest.get('url')}")
                    return
                raise Stop(1, f"mainのCIが {latest.get('conclusion')} です: {latest.get('url')}")
            state = f"{latest.get('status')}（{latest.get('url')}）"
        else:
            state = "未作成"
        if time.monotonic() >= deadline:
            raise Stop(2, f"mainのCIが {max_wait} 秒以内に完了しませんでした: {state}")
        say("main-ci", f"待機中: {state}")
        time.sleep(interval)


def deploy_and_verify(root: str, sha: str | None = None) -> None:
    say("deploy", "手元環境で PWA ビルドを実行中...")
    code, out, err = run(["npx", "--yes", "quasar", "build", "-m", "pwa"], cwd=root, timeout=300)
    if code != 0:
        raise Stop(1, f"手元環境での PWA ビルドに失敗しました: {err or out}")
    say("deploy", "手元環境での PWA ビルドが完了しました")

    local_pwa_dir = Path(root) / "dist" / "pwa"
    if not (local_pwa_dir / "index.html").is_file():
        raise Stop(1, f"ビルド成果物が見つかりません: {local_pwa_dir / 'index.html'}")

    if sha:
        (local_pwa_dir / ".deployed_commit").write_text(sha.strip() + "\n", encoding="utf-8")

    say("deploy", f"ビルド成果物を VPS ({VPS_HOST}:{VPS_REPO_DIR}) へ転送・配置中...")
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp_archive:
        tmp_archive_path = tmp_archive.name

    remote_archive = f"/tmp/char_cnt_pwa_{int(time.time())}_{os.getpid()}.tar.gz"
    lock_file = "/tmp/char_cnt_deploy.lock"

    try:
        code, out, err = run(["tar", "-czf", tmp_archive_path, "-C", str(local_pwa_dir), "."])
        if code != 0:
            raise Stop(1, f"アーカイブ作成に失敗しました: {err or out}")

        code, out, err = run(["scp", "-o", "BatchMode=yes", tmp_archive_path, f"{VPS_HOST}:{remote_archive}"])
        if code != 0:
            raise Stop(1, f"アーカイブの VPS 転送に失敗しました: {err or out}")

        deploy_script = (
            f"set -euo pipefail; "
            f"su - appuser -c '"
            f"cd {VPS_REPO_DIR} && "
            f"git fetch origin main && "
            f"git checkout main && "
            f"git reset --hard origin/main && "
            f"mkdir -p dist/pwa_new && "
            f"tar -xzf {remote_archive} -C dist/pwa_new && "
            f"rm -rf dist/pwa_old && "
            f"( [ -d dist/pwa ] && mv dist/pwa dist/pwa_old || true ) && "
            f"mv dist/pwa_new dist/pwa && "
            f"rm -rf dist/pwa_old"
            f"' && "
            f"rm -f {remote_archive}"
        )
        remote_cmd = f"flock -x -w 300 {lock_file} bash -c {shlex.quote(deploy_script)}"
        code, out, err = run(["ssh", "-o", "BatchMode=yes", VPS_HOST, remote_cmd], timeout=300)
        if code != 0:
            run(["ssh", "-o", "BatchMode=yes", VPS_HOST, f"rm -f {remote_archive}"])
            raise Stop(1, f"VPS での成果物展開・デプロイに失敗しました: {err or out}")
        say("deploy", "VPS への成果物配置とリポジトリ同期が完了しました")
    finally:
        if os.path.exists(tmp_archive_path):
            os.remove(tmp_archive_path)

    req = urllib.request.Request(PROD_URL, headers={"User-Agent": "char_cnt-finish-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            status_code = resp.status
            body = resp.read().decode("utf-8", errors="ignore")
    except Exception as exc:
        raise Stop(1, f"本番 URL ({PROD_URL}) の外形確認に失敗しました: {exc}") from exc

    if status_code != 200 or "<div id=q-app>" not in body and '<div id="q-app">' not in body:
        raise Stop(1, f"本番 URL ({PROD_URL}) の応答が不正です (HTTP {status_code})")
    say("deploy", f"本番外形確認 OK: {PROD_URL} (HTTP {status_code})")


def close_issue(issue: int, pr: int) -> None:
    data = gh_json(["issue", "view", str(issue), "--repo", REPO, "--json", "state"])
    if data.get("state") == "CLOSED":
        say("issue", f"#{issue} はclose済み")
        return
    code, _, err = run(["gh", "issue", "close", str(issue), "--repo", REPO, "--comment", f"#{pr} でmainへ反映・本番デプロイしました。"])
    if code != 0:
        raise Stop(5, f"Issue #{issue} をcloseできません: {err}")
    say("issue", f"#{issue} をcloseしました")


def set_done(issue: int) -> None:
    owner, repo = REPO.split("/")
    try:
        _, current, _, _ = issue_status.lookup(owner, repo, issue)
        if current == DONE:
            say("status", f"#{issue} は既に「{DONE}」")
            return
        issue_status.set_status(argparse.Namespace(owner=owner, repo=repo, issue=issue, status=DONE, force=False))
    except SystemExit as error:
        raise Stop(5, f"Statusを「{DONE}」へ更新できません: {error}") from error


def finish(args: argparse.Namespace) -> int:
    root = repo_root()
    os.chdir(root)
    pr_data = view_pr(args.pr)
    branch = args.branch or pr_data.get("headRefName") or ""
    worktree = str(Path(args.worktree).resolve()) if args.worktree else None

    if not worktree and not getattr(args, "main", False):
        detected = detect_worktree(root, args.issue, branch)
        if detected:
            worktree = str(Path(detected).resolve())
            say("precheck", f"worktree を自動検出しました: {worktree}")

    data = merge(args.pr, pr_data, worktree)
    sha = (data.get("mergeCommit") or {}).get("oid")
    cleanup(root, branch, worktree)
    if sha:
        wait_main_ci(root, sha, args.max_wait, args.interval)
    if args.skip_deploy:
        say("deploy", "--skip-deploy 指定のため本番デプロイをスキップします")
    else:
        deploy_and_verify(root, sha)
    close_issue(args.issue, args.pr)
    set_done(args.issue)
    print(f"FINISH pr={args.pr} issue={args.issue} merge={(sha or '')[:7]} status={DONE}", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--issue", type=int, required=True)
    parser.add_argument("--worktree", help="作業したworktreeのパス（--mainで作業した場合は付けない）")
    parser.add_argument("--main", action="store_true", help="メイン作業ディレクトリで作業した場合に指定（worktree自動検出をスキップ）")
    parser.add_argument("--branch", help="作業ブランチ名（省略時はPRのheadRefName）")
    parser.add_argument("--skip-deploy", action="store_true", help="本番VPSへのデプロイをスキップする（ドキュメント・Skill変更のみの場合など）")
    parser.add_argument("--max-wait", type=int, default=1500, help="mainのCIを待つ上限秒数")
    parser.add_argument("--interval", type=int, default=10)
    args = parser.parse_args(argv)
    try:
        return finish(args)
    except Stop as stop:
        say("stop", str(stop))
        return stop.code


if __name__ == "__main__":
    sys.exit(main())
