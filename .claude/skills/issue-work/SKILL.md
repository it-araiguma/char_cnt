---
name: issue-work
description: 「open issueを対応して」「#1を対応して」等、Issueの選定・実装・検証・PR・マージ・本番デプロイ・Project更新までを一気通貫で行う。
---

# open Issue対応の手順（char_cnt）

対象は `it-araiguma/char_cnt`（`https://count.it-araiguma.com/`）と `char_cnt` Project（Project 6）です。
`araiguma-blog` の `issue-work` と同じ自律実行フローを、このリポジトリの構成に合わせています。
このファイルを Claude Code・Codex・AGY 共通の正本とします。

**PRを作った時点でも、ローカル検証が通った時点でも完了ではありません。**
マージ・本番VPSへのデプロイと外形確認・Issueのclose・Project 6の「完了」ステータスへの更新・作業ブランチの削除まで自律的に完遂します。
また、**Issue番号の指定時や選定後は、ファイル調査や方針検討を先行させず、まず真っ先にステータスを「対応中」へ更新（`start.py`）します。**

ユーザーへ確認するのは、不可逆・外部影響のある操作だけです（データの削除、課金の発生など）。
Issueの選定、修正方針、作業中に見つけた課題の起票、PRのマージ、本番デプロイ、作業ブランチの削除は、確認せずに自分で決めて進めます。

## 引数

| 引数 | 意味 |
| --- | --- |
| なし | Issueを自分で選び、専用worktreeで作業する（既定） |
| `<Issue番号>` | 選定（Step 1〜2）を省略し、そのIssueを対象にする |
| `PR <PR番号>` / `<PR URL>` | 既存PRを引き継ぐ。作業ブランチをチェックアウトし、コンフリクトを先に解消してからStep 8以降へ進む |
| `--main` | worktreeを使わず、メイン作業ディレクトリでブランチを切る |
| `--worktree` | 明示指定。既定と同じ動作（後方互換） |

## Step 1〜2: 対応するIssueの選定

Issue番号やPRが指定されていれば省略し、Step 3へ進みます。
指定が無いときは、候補を機械的に取得します。

```bash
python3 "$(git rev-parse --show-toplevel)/.claude/skills/issue-work/scripts/select_candidates.py" --promote-due
```

- 出力は `#番号 重要度 Status タイトル`（ステータス優先度・重要度順・作成日昇順）と、末尾サマリです。
- 候補にするStatusは「やること」（後方互換で「未対応」も対象）です。「対応中」（他のエージェントが着手中）、「完了」、「検討中」は除外されます。
  Project 6 の Status は「やること」「対応中」「完了」「検討中」の4つです。
- 終了コード1は取得失敗です。候補0件と取り違えず、失敗として報告します。

**どのIssueに着手するかをユーザーへ選ばせません。** 重要度（高 > 中 > 低）と実用性から自分で1件を選びます。
実用性は次の問いで判断し、工数の小ささ自体は選定理由にしません。

1. ユーザー体験・SEO・文字数カウントの正確性に効くか
2. 放置するとエラーや不整合が拡大するか
3. 他のIssueや外部要因に塞がれていないか

候補から1件を選び、選んだ理由を添えてそのまま着手します。
候補が0件のときだけ、その旨を報告して終了します。

## Step 3: まず作業IssueのStatusを「対応中」にし、作業場所を決める

Issue番号が指定された場合も、候補から選定した場合も、**ファイル調査やIssue本文の詳細確認、方針検討を始める前に、まず真っ先に `start.py` を実行してProject 6のStatusを「対応中」に変更し、専用worktreeを作成します。**
ステータス更新を後回しにすると、他エージェントとの重複着手や未着手放置の原因になります。

```bash
python3 "$(git rev-parse --show-toplevel)/.claude/skills/issue-work/scripts/start.py" \
  --issue <番号> --slug <短いslug> [--type fix|feat|perf|test|docs|refactor|chore] [--main] [--resume]
```

- `--slug` はIssueタイトルや内容から英小文字・数字・ハイフンで簡潔（2〜3単語程度）に即時命名します（事前の詳細調査は不要です）。
- 空き容量確認 → Statusを「対応中」にして読み戻し → `.claude/worktrees/issue-<番号>-<slug>` にworktree作成
  （ブランチ `<type>/<番号>-<slug>`、基点は `origin/main`）→ `node_modules`（ハードリンク）と `.env`（symlink）の共有、を一括実行します。
- 最終行 `START workdir=<path> branch=<name> deps=<ok|missing>` の `workdir` で以降の作業を行います。
- 終了コード: 0=完了 / 4=着手拒否（他エージェント対応中、既存worktreeあり等） / 5=準備失敗（Statusは元の値へロールバック）。
- `--resume` は自分の中断済み作業を再開するときだけ付けます。
- 復旧手順が必要なときは [`references/recovery.md`](references/recovery.md) を参照してください。

## Step 4: 着手前の確認・方針整理

`start.py` が準備した `workdir`（専用worktree）へ移動し、Issue本文・関連ファイルを確認して方針を整理します。
破壊的変更に該当しない限り、ユーザーへの事前確認なしで進めます。

## Step 5: 実装

- `CLAUDE.md` の絶対ルールを遵守します。
- コード変更時は lint 設定やテストの安易な緩和を行わず、本体側を修正します。
- コミットは目的ごとに分け、実装と対応するテスト・文書は同じコミットに含めます。

### 作業中に見つけた課題は起票する

Step 5〜12の全段階で、**対象Issueの範囲外の不具合やあるべき修正は、報告だけで済ませずその場で起票します。**
起票前の重複照合や既存Issueの確認には、次のコマンドを利用できます。

```bash
# 既存Issue/PRの索引検索（-qで複数クエリ指定可能、--include-closedで完了分含む）
python3 "$(git rev-parse --show-toplevel)/.claude/skills/issue-work/scripts/duplicate_index.py" index -q "<検索語>" [--include-closed]
# 候補の本文のみ上限付きで取得
python3 "$(git rev-parse --show-toplevel)/.claude/skills/issue-work/scripts/duplicate_index.py" body <Issue番号> [--max-bytes 8192]
```

今回のPRに混ぜず（コミットの粒度）、次のコマンドで起票します。重複照合・Issue起票・Project 6登録・Status（「やること」）と重要度（高・中・低）の設定・読み戻し検証を一括で行います。

```bash
python3 "$(git rev-parse --show-toplevel)/.claude/skills/issue-work/scripts/create_issues.py" \
  --title "<タイトル>" --body "<本文>" --priority <高|中|低> [--labels <ラベル,...>]
```
（本文が長い場合は `--body-file <ファイルパス>`、バッチ起票時は `--file <候補JSON>` を使用可能）

- 手動で `gh issue create` した場合は、続けて必ず次のコマンドで Project 6 に追加し、Status「やること」と重要度を入れます。
  ```bash
  python3 "$(git rev-parse --show-toplevel)/.claude/skills/issue-work/scripts/issue_status.py" \
    add --issue <起票した番号> --priority <高|中|低>
  ```
- `gh project item-add` だけで追加すると Status が空（No Status）になり、Step 1〜2 の候補から漏れます。
- 重要度ラベルと Project の重要度は同じ値にします（`priority: high`＝高、`priority: medium`＝中、`priority: low`＝低）。
- 起票しても今回の作業は止めずに進めます。

## Step 6: ローカル検証とセルフレビュー

push前に、以下の検証を必ず実行して通します（メイン側に `node_modules` が未インストールの場合はメイン側で `npm ci` を実行してから進めます）。

1. Lint チェック:
   ```bash
   npm run lint < /dev/null
   ```
2. 型チェック & PWA ビルド確認:
   ```bash
   npx --yes vue-tsc --noEmit < /dev/null
   npx --yes quasar build -m pwa < /dev/null
   ```
3. Python スクリプト（`.py`）を変更した場合:
   ```bash
   python3 -m py_compile <変更したファイル>
   ```
4. セルフレビュー:
   - `git diff origin/main...HEAD` で余計な変更やデバッグコードが混入していないか確認します。

## Step 7: PR作成

```bash
gh pr create --repo it-araiguma/char_cnt --base main --title "<type>: <日本語の要約> (#<Issue番号>)" --body "<本文>"
```

- 本文には `Closes #<番号>`、変更の概要、検証内容を記載します。
- PRの作成後、URLを報告して指示を待たずにStep 8へ進みます。

## Step 8: PRの状態確認

```bash
python3 "$(git rev-parse --show-toplevel)/.claude/skills/issue-work/scripts/wait_pr.py" --pr <PR番号>
```

- PR のチェック完了・コンフリクト有無を1プロセス内で待機・判定します。
- **手動ポーリングの厳禁**:
  - `wait_pr.py` 自体が内部でチェック完了まで待機するため、`gh pr checks` ループや `sleep` ループによる手動ポーリングは行いません。
  - AGY ではコマンドがバックグラウンド化された場合、`manage_task(status)` や `schedule` 等で手動ポーリングせず、ツールを呼び出さずに完了通知（Reactive Wakeup）を待ってターンを再開します。
- 終了コードが 0 であれば全チェックが成功しコンフリクトもありません。Step 10〜12 へ進みます。
- チェックが失敗した、またはコンフリクトがある場合、スクリプトは終了コード 1 で終了します。原因を確認し、Step 9 へ進みます。

## Step 9: 失敗・指摘への対応

- コンフリクトが発生した場合は、最新の `origin/main` を作業ブランチへ取り込んで解消します。
- 検証失敗や問題がある場合は修正し、Step 6の検証をやり直して再pushします。
- 指摘は、このPRの目的の範囲で直します。範囲外の課題は起票して分けます。

## Step 10〜12: マージ・本番デプロイ・片付け・完了

マージ条件（コンフリクトなし、未コミット変更なし）を満たしたら、ユーザー承認を挟まず次の1コマンドで完了処理を行います。

```bash
python3 "$(git rev-parse --show-toplevel)/.claude/skills/issue-work/scripts/finish.py" \
  --pr <PR番号> --issue <番号> [--worktree <START の workdir>]
```

- マージ前条件確認 → squashマージとリモートブランチ削除 → worktree除去・ローカルブランチ削除・メインのfast-forward → mainのCI確認（存在する場合）→ **本番VPS（`/home/appuser/public_html/char_cnt`）へのデプロイ（手元 PWA ビルド成果物の転送・flock による排他制御下でのリポジトリ同期とアトミック配置）と `https://count.it-araiguma.com/` の HTTP 200 外形確認** → Issueクローズ → Project 6のStatusを「完了」へ更新と読み戻し、を一括実行します。
- `--main` で作業した場合は `--worktree` を付けません。ドキュメントやスキルのみの変更で本番再ビルドが不要な場合は `--skip-deploy` を指定できます。
- 終了コード: 0=完了 / 1=CIまたはデプロイ失敗 / 4=条件不充足 / 5=処理失敗。
- 完了報告の前に、未起票の課題がないか点検し、あれば起票してから報告します。

## Step 13: 中断するとき

作業を中断する場合、または仕様確認待ち等で「完了」に到達せず終える場合は、Statusを「やること」へ戻します。

```bash
python3 "$(git rev-parse --show-toplevel)/.claude/skills/issue-work/scripts/issue_status.py" \
  set --issue <番号> --status やること
```

worktreeを残して一時中断する場合は「対応中」のまま残し、再開時に `--resume` を使用します。
