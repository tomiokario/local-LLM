# Codex マルチエージェント運用

この文書は、`C:\LLM` で Codex がタスクを確実に進めるための作業手順です。Web サイト運用、論文管理、Notion 連携などの参照元リポジトリ固有のルールは持ち込まず、ローカル LLM 運用、PowerShell スクリプト、ドキュメント整備に必要な部分だけを残します。

## 目的

- 依頼内容を小さな受け入れ条件に分ける。
- 実装者とは別視点の確認を必ず通せる形にする。
- ローカル専用データと tracked files の境界を守る。
- 複数タスクを扱うときに worktree、branch、Codex スレッドを分ける。
- 完了報告で、何を直し、何を確認し、何が残っているかを明確にする。

## 標準フロー

1. 意図を整理する
   - ユーザー依頼、Issue、関連コメント、既存ルールを読む。
   - 目的、受け入れ条件、変更対象、validation profile を書き出す。
2. ルール変更は先に反映する
   - 作業手順、レビュー順序、保存方針、エージェント定義が変わる場合は、先に `AGENTS.md`、この文書、`.codex/agents/*` を更新する。
3. ローカルで実装する
   - 割り当てられた branch / worktree で作業する。
   - モデル本体、ログ、`.env`、`private/`、`private_data/`、ローカル専用データを tracked files に混ぜない。
4. 検証する
   - validation profile に沿って、テスト、構文確認、ドキュメント整合性確認などを実行する。
5. fresh review を通す
   - 実装者とは別の視点で、現在差分、関連 docs/scripts、検証結果、ローカル専用データ境界を確認する。
6. intent review を通す
   - ユーザーの依頼と会話で固まった意図に沿っているか確認する。
7. 完了、commit、push、PR へ進む
   - 必要なレビューが通った場合だけ次へ進む。
   - 制約でレビューできない場合は、完了報告に理由と残リスクを書く。

## 役割分担

再利用用の定義は `.codex/agents/*.toml` に置きます。

- 親オーケストレータ: ユーザーとの窓口、判断、進行管理、最終報告を担当する。
- 質問担当: 不足仕様、変更タイプ、validation profile、受け入れ条件を整理する。
- 実装担当: 合意済み仕様に従って実装し、検証結果と evidence handoff を返す。
- fresh review 担当: 要求とのズレ、回帰、検証不足、ローカル専用データ混入を確認する。
- intent review 担当: ユーザーの本来の意図、追加指示、優先順位との整合を確認する。

## Validation Profiles

- `docs-process`: README、`docs/`、`notes/`、`AGENTS.md`、`.codex/agents/*` の整合性。
- `script-powershell`: PowerShell 構文、引数、エラー時の挙動、既存スクリプトとの使い分け。
- `model-config`: Ollama / LM Studio / aider / Cline の設定、モデル名、VRAM 前提、環境変数。
- `benchmark-evaluation`: 測定条件、再現手順、結果の保存先、tracked files に入れるべきでない生成物。
- `tool-integration`: Codex、aider、Cline、GitHub、外部ツール連携の権限境界。
- `infra-config`: `.gitignore`、`.env.example`、ディレクトリ構成、ローカル作業領域、改行コード。

## 並列タスク

複数タスクを並列に進める場合の基本単位は次です。

- 1 タスクまたは 1 Issue
- 1 作業ブランチ
- 1 worktree
- 1 Codex 作業スレッド

worktree は repository 内の gitignored な `tmp/worktrees/` に作ります。

```powershell
git checkout main
git pull --rebase origin main
git worktree add tmp/worktrees/task-short-topic -b codex/task-short-topic main
```

進行管理スレッドは、依存関係、作業順序、review 結果、PR 状態、merge 後の片付けを管理します。各作業スレッドは、割り当てられたタスクの差分だけを扱います。

## Handoff

作業スレッドへ渡す最小情報:

- 対象タスクまたは Issue
- 合意済み仕様
- acceptance criteria
- validation profile
- 触ってよい範囲
- 触らない範囲
- 検証コマンド
- worktree と branch 名

作業スレッドから受け取る最小情報:

- 変更したファイル
- 実行した検証
- validation profile を満たす evidence
- 残リスク
- 次に必要な判断

## 完了条件

- 実装または文書更新が完了している。
- validation profile に沿った確認が完了している。
- ローカル専用データ境界を確認している。
- fresh review と intent review が必要な場合に通っている。
- `git status` で意図しない差分がないことを確認している。
- 完了報告に、変更内容、確認結果、未実施確認、残リスクを書ける状態になっている。

## Merge 後の片付け

PR が merge された後、ユーザーから完了連絡を受けた場合は primary worktree で片付けます。

```powershell
git checkout main
git pull --rebase origin main
git worktree remove tmp/worktrees/task-short-topic
git branch -d codex/task-short-topic
git worktree prune
```

未 merge の差分や未 push の変更がある場合は削除せず、残っている状態を報告します。
