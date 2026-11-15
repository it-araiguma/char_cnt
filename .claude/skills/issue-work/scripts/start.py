#!/usr/bin/env python3
"""issue-work Step 3（「対応中」化〜作業場所と環境の準備）を1回で行う。

使い方:
    start.py --issue <Issue番号> --slug <短いslug> [--type fix|feat|perf|test|docs|refactor|chore]
             [--main] [--resume] [--min-free-gb N]

段階（各段の結果を1行ずつ出力し、失敗した段で止まる）:
  1. precheck : 引数・メイン側の状態・空き容量を確認する（副作用なし）
  2. status   : ProjectのStatusを「対応中」にして読み戻す（既に対応中なら止める）
  3. workdir  : worktreeを作る（--main ならメインでブランチを切る）。既存は --resume のときだけ再利用
  4. deps     : node_modules（ハードリンク）および .env（シンボリックリンク）を再利用

最終行に `START workdir=<path> branch=<name> ...` を出力する。

終了コード:
  0: 準備完了
  4: 着手できない（他のエージェントが対応中・引数不正・空き容量不足・未コミット変更あり等。変更なし）
  5: 準備に失敗した（Statusは今回更新した場合のみ元のStatusへ巻き戻す）
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

TODO = "やること"
IN_PROGRESS = "対応中"
BRANCH_TYPES = ("fix", "feat", "perf", "test", "docs", "refactor", "chore")
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,48}[a-z0-9]$|^[a-z0-9]$")
DEFAULT_MIN_FREE_GB = 5.0
SCRIPT_DIR = Path(__file__).resolve().parent
ISSUE_STATUS = SCRIPT_DIR / "issue_status.py"
GIB = 1024**3


class Refuse(Exception):
    """着手できない（何も変更していない）。終了コード4。"""


class Failed(Exception):
    """準備に失敗した。終了コード5。"""


def run(cmd: list[str], cwd: str | Path | None = None) -> tuple[int, str, str]:
    res = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=cwd)
    return res.returncode, res.stdout.strip(), res.stderr.strip()


def say(stage: str, message: str) -> None:
    print(f"[start:{stage}] {message}", flush=True)


def repo_root() -> Path:
    """worktree内から呼ばれても、メイン作業ディレクトリを返す。"""
    code, out, err = run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"]
    )
    if code != 0 or not out:
        raise Failed(f"git のルートを特定できません: {err}")
    return Path(out).parent


def branch_name(branch_type: str, issue: int, slug: str) -> str:
    return f"{branch_type}/{issue}-{slug}"


def validate_args(branch_type: str, issue: int, slug: str) -> None:
    if issue <= 0:
        raise Refuse(f"Issue番号が不正です: {issue}")
    if branch_type not in BRANCH_TYPES:
        raise Refuse(
            f"--type は {', '.join(BRANCH_TYPES)} のいずれかです: {branch_type!r}"
        )
    if not SLUG_PATTERN.match(slug):
        raise Refuse(
            f"--slug は英小文字・数字・ハイフンのみ（50文字以内）です: {slug!r}"
        )


def check_free_space(root: Path, min_free_gb: float) -> float:
    free_gb = shutil.disk_usage(root).free / GIB
    if free_gb < min_free_gb:
        raise Refuse(
            f"空き容量が不足しています: {free_gb:.1f} GiB 利用可能 "
            f"（必要: {min_free_gb:.1f} GiB）"
        )
    return free_gb


def check_main_allowed(root: Path, branch: str) -> None:
    code, out, _ = run(["git", "status", "--porcelain"], cwd=root)
    if code != 0 or out:
        raise Refuse("メイン作業ディレクトリに未コミットの変更があります")
    current = current_branch(root)
    if current == branch:
        return
    code, _, _ = run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], cwd=root
    )
    if code == 0:
        raise Refuse(f"ブランチ {branch} は既に存在します")


def current_branch(cwd: Path) -> str:
    code, out, _ = run(["git", "branch", "--show-current"], cwd=cwd)
    return out if code == 0 else ""


def list_worktrees(root: Path) -> list[tuple[Path, str, str]]:
    code, out, err = run(["git", "worktree", "list", "--porcelain"], cwd=root)
    if code != 0:
        raise Failed(f"worktree 一覧の取得に失敗しました: {err}")
    items: list[tuple[Path, str, str]] = []
    current_path: Path | None = None
    current_head = ""
    current_br = ""
    for line in out.splitlines():
        if line.startswith("worktree "):
            current_path = Path(line.removeprefix("worktree "))
        elif line.startswith("HEAD "):
            current_head = line.removeprefix("HEAD ")
        elif line.startswith("branch "):
            current_br = line.removeprefix("branch ").removeprefix("refs/heads/")
        elif not line.strip() and current_path is not None:
            items.append((current_path, current_head, current_br))
            current_path = None
            current_head = ""
            current_br = ""
    if current_path is not None:
        items.append((current_path, current_head, current_br))
    return items


def find_worktree(root: Path, issue: int, expected: Path) -> Path | None:
    prefix = f"issue-{issue}-"
    for path, _, _ in list_worktrees(root):
        if path == expected or path.name.startswith(prefix):
            return path
    return None


def check_existing_worktree(issue: int, existing: Path | None, resume: bool) -> None:
    if existing is None:
        return
    if not resume:
        raise Refuse(
            f"Issue #{issue} 用の worktree が既に存在します: {existing} "
            "（中断済み作業の再開なら --resume を指定してください）"
        )


def claim_issue(issue: int, resume: bool) -> tuple[bool, str]:
    """(今回対応中に更新したか, 更新前のStatus) を返す。"""
    code, current, err = run(
        [sys.executable, str(ISSUE_STATUS), "show", "--issue", str(issue)]
    )
    if code != 0:
        raise Failed(f"Statusの取得に失敗しました: {err or current}")
    if current == IN_PROGRESS and not resume:
        raise Refuse(
            f"Issue #{issue} は既に「{IN_PROGRESS}」です。"
            "別のIssueを選ぶか、中断済み作業の再開なら --resume を指定してください"
        )
    if current == IN_PROGRESS and resume:
        say("status", f"#{issue} は既に「{IN_PROGRESS}」（--resume により継続）")
        return False, current
    code, out, err = run(
        [
            sys.executable,
            str(ISSUE_STATUS),
            "set",
            "--issue",
            str(issue),
            "--status",
            IN_PROGRESS,
            "--force",
        ]
    )
    if code != 0:
        raise Failed(f"Statusを「{IN_PROGRESS}」へ更新できませんでした: {err or out}")
    say("status", out)
    return True, (current or TODO)


def release_issue(issue: int, fallback_status: str = TODO) -> None:
    say("status", f"ロールバック: #{issue} を「{fallback_status}」に戻します")
    run(
        [
            sys.executable,
            str(ISSUE_STATUS),
            "set",
            "--issue",
            str(issue),
            "--status",
            fallback_status,
            "--force",
        ]
    )


def ensure_branch_worktree(root: Path, branch: str, workdir: Path) -> None:
    code, _, _ = run(["git", "fetch", "origin", "main"], cwd=root)
    if code != 0:
        say("precheck", "警告: origin/main の fetch に失敗しました。ローカルの main を基点にします")
    base = "origin/main" if run(["git", "rev-parse", "--verify", "--quiet", "origin/main"], cwd=root)[0] == 0 else "main"

    code, _, _ = run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], cwd=root
    )
    branch_exists = code == 0

    if branch_exists:
        cmd = ["git", "worktree", "add", str(workdir), branch]
    else:
        cmd = ["git", "worktree", "add", "-b", branch, str(workdir), base]

    code, out, err = run(cmd, cwd=root)
    if code != 0:
        raise Failed(f"worktree の作成に失敗しました: {err or out}")


def prepare_main_branch(root: Path, branch: str) -> None:
    run(["git", "fetch", "origin", "main"], cwd=root)
    base = "origin/main" if run(["git", "rev-parse", "--verify", "--quiet", "origin/main"], cwd=root)[0] == 0 else "main"

    code, _, _ = run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], cwd=root
    )
    if code == 0:
        code, out, err = run(["git", "checkout", branch], cwd=root)
    else:
        code, out, err = run(["git", "checkout", "-b", branch, base], cwd=root)
    if code != 0:
        raise Failed(f"ブランチの切り替えに失敗しました: {err or out}")


def link_hardlink(source: Path, dest: Path) -> str:
    if dest.exists():
        return "ok"
    tmp = dest.with_name(f".{dest.name}.start-tmp")
    if tmp.is_symlink():
        tmp.unlink()
    elif tmp.exists():
        shutil.rmtree(tmp, ignore_errors=True)
    dest.parent.mkdir(parents=True, exist_ok=True)
    code, _, err = run(["cp", "-al", str(source), str(tmp)])
    if code != 0:
        if tmp.exists():
            shutil.rmtree(tmp, ignore_errors=True)
        raise Failed(f"{source} のハードリンク複製に失敗しました: {err}")
    tmp.rename(dest)
    return "ok"


def reuse_shared_files(root: Path, workdir: Path) -> dict[str, str]:
    """メインディレクトリの node_modules や設定ファイルを worktree へ共有する。"""
    results: dict[str, str] = {}

    # 1. node_modules (ハードリンク共有)
    nm_src = root / "node_modules"
    nm_dst = workdir / "node_modules"
    if nm_src.is_dir():
        try:
            link_hardlink(nm_src, nm_dst)
            results["node_modules"] = "ok"
            say("deps", "node_modules: ハードリンク共有完了")
        except Failed as e:
            say("deps", f"警告: node_modules の共有に失敗: {e}")
            results["node_modules"] = "missing"
    else:
        results["node_modules"] = "missing"

    # 2. .env (存在する場合のみ symlink)
    env_src = root / ".env"
    env_dst = workdir / ".env"
    if env_src.exists():
        if not env_dst.exists() and not env_dst.is_symlink():
            try:
                os.symlink(env_src, env_dst)
                results[".env"] = "ok"
                say("deps", ".env: symlink 作成完了")
            except OSError:
                results[".env"] = "missing"
        else:
            results[".env"] = "ok"

    return results


def start(args: argparse.Namespace) -> int:
    validate_args(args.type, args.issue, args.slug)
    root = repo_root()
    branch = branch_name(args.type, args.issue, args.slug)

    free_gb = check_free_space(root, args.min_free_gb)
    if args.main:
        check_main_allowed(root, branch)
    say("precheck", f"空き容量 {free_gb:.1f} GiB / ブランチ {branch}")

    worktree_dir = root / ".claude" / "worktrees"
    expected = worktree_dir / f"issue-{args.issue}-{args.slug}"
    existing = None if args.main else find_worktree(root, args.issue, expected)
    check_existing_worktree(args.issue, existing, args.resume)

    claimed, original_status = claim_issue(args.issue, args.resume)
    try:
        if args.main:
            prepare_main_branch(root, branch)
            workdir = root
            actual_branch = current_branch(workdir) or branch
            say("workdir", f"メイン作業ディレクトリでブランチ {actual_branch} を使用")
            deps: dict[str, str] = {}
        else:
            if existing is not None:
                workdir = existing
                say("workdir", f"既存のworktreeを再利用: {workdir}")
            else:
                worktree_dir.mkdir(parents=True, exist_ok=True)
                ensure_branch_worktree(root, branch, expected)
                workdir = expected
                say("workdir", f"worktreeを作成: {workdir}")
            actual_branch = current_branch(workdir) or branch
            deps = reuse_shared_files(root, workdir)
    except (Failed, Refuse) as error:
        if claimed:
            release_issue(args.issue, original_status)
        raise Failed(str(error)) from error

    missing = [label for label, state in deps.items() if state == "missing"]
    reusable = [label for label, state in deps.items() if state == "ok"]
    print(
        f"START workdir={workdir} branch={actual_branch} deps={','.join(reusable) or '-'} missing={','.join(missing) or '-'}",
        flush=True,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue", type=int, required=True)
    parser.add_argument("--slug", required=True, help="ブランチ名等に使う英小文字slug")
    parser.add_argument(
        "--type", default="fix", choices=BRANCH_TYPES, help="ブランチ接頭辞"
    )
    parser.add_argument(
        "--main", action="store_true", help="worktreeを使わずメイン作業ディレクトリで作業"
    )
    parser.add_argument(
        "--resume", action="store_true", help="中断済み作業の再開"
    )
    parser.add_argument("--min-free-gb", type=float, default=DEFAULT_MIN_FREE_GB)
    args = parser.parse_args(argv)
    try:
        return start(args)
    except Refuse as error:
        say("refuse", str(error))
        return 4
    except Failed as error:
        say("error", str(error))
        return 5


if __name__ == "__main__":
    sys.exit(main())
