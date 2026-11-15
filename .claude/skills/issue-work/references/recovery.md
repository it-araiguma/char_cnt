# issue-work 復旧・トラブルシューティング

`issue-work` スキルの各ステップで発生した問題に対処するための復旧手順です。

## 1. 着手時（Step 3 / `start.py`）

### 終了コード 4: 着手拒否
- **「既に『対応中』です」**:
  - 別のエージェントが着手中の可能性があります。別のIssueを選定してください。
  - 自身が中断した作業を再開する場合は `--resume` を付与して再実行してください。
- **「worktree が既に存在します」**:
  - 同一Issueの `.claude/worktrees/issue-<番号>-<slug>` が残っています。
  - 自身の中断作業なら `--resume` で再利用してください。
  - 不要になった孤立worktreeであれば、`git worktree remove --force .claude/worktrees/<名前>` で削除し、`git worktree prune` を実行してください。
- **「空き容量が不足しています」**:
  - ディスクの空き容量を確保するか、一時ファイルをクリーンアップしてください。
- **「メイン作業ディレクトリに未コミットの変更があります」** (`--main` 指定時):
  - 変更をコミットするか stash してください。

### 終了コード 5: 準備失敗
- worktree の作成や設定ファイルのリンクに失敗した場合、自動的に Status は元のステータス（通常は「やること」）へロールバックされます。
- 手動で Status を確認・変更したい場合は `issue_status.py` を使用してください:
  ```bash
  python3 "$(git rev-parse --show-toplevel)/.claude/skills/issue-work/scripts/issue_status.py" show --issue <番号>
  python3 "$(git rev-parse --show-toplevel)/.claude/skills/issue-work/scripts/issue_status.py" set --issue <番号> --status やること
  ```

## 2. マージ・デプロイ・完了時（Step 10〜12 / `finish.py`）

### 終了コード 4: マージ前条件不充足
- **「PRがOPENではありません」**: PRが既にクローズまたはマージされていないか確認してください。
- **「コンフリクトがあります」**:
  - 最新の `origin/main` を作業ブランチへマージしてコンフリクトを解消し、再pushしてください:
    ```bash
    git fetch origin main
    git merge origin/main
    # コンフリクト解消
    git push origin <ブランチ名>
    ```
- **「worktree に未コミットの変更が残っています」**:
  - 作業ディレクトリに残っている変更がないか `git status` で確認し、コミットまたは破棄してください。

### 終了コード 1 / 5: デプロイ・マージ・片付け失敗
- VPSへのSSH接続失敗やビルドエラー、GitHubのAPIエラーなどが発生した場合は、メッセージを確認して是正し、再度 `finish.py` を実行してください（既にマージ済みのPRに対しても冪等に続きから処理されます）。

## 3. 作業の中断（Step 13）

作業を途中で取りやめる、または保留にする場合:
1. worktree を残さない場合:
   ```bash
   python3 "$(git rev-parse --show-toplevel)/.claude/skills/issue-work/scripts/issue_status.py" set --issue <番号> --status やること
   git worktree remove --force .claude/worktrees/issue-<番号>-<slug>
   git worktree prune
   ```
2. 作業中の worktree を残して一時中断する場合:
   - Status を「対応中」のまま残し、再開時に `--resume` を使用します。
