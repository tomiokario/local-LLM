# Repo Local Agent Definitions

このディレクトリには、`C:\LLM` の作業で再利用するマルチエージェント役割定義を置きます。実際の subagent 起動では、親オーケストレータが該当する TOML の role / instructions / 出力形式を同等設定へ写して使います。

## 役割

- [question-agent.toml](./question-agent.toml): 不足仕様、変更タイプ、検証観点、受け入れ条件を整理する。
- [implementation-agent.toml](./implementation-agent.toml): 合意済み仕様に従って編集し、検証結果と evidence handoff を返す。
- [fresh-review-agent.toml](./fresh-review-agent.toml): 実装者とは別視点で、現在差分と検証結果を確認する。
- [intent-review-agent.toml](./intent-review-agent.toml): ユーザーの意図と差分がずれていないか確認する。

## Pre Completion Review Gate

完了扱い、commit、push、PR 作成の前に、必要に応じて次の順で確認します。

1. `fresh-review-agent`
   - 現在差分、関連 docs/tests、検証結果、ローカル専用データ境界を確認する。
2. `intent-review-agent`
   - ユーザーの依頼、会話で固まった意図、受け入れ条件と差分の整合を確認する。

どちらかが blocker を返した場合は修正し、該当レビューを再実行してから次へ進みます。

## ローカルデータ境界

この repository では、モデル本体、ログ、一時ベンチマーク出力、`.env`、`*.local.*`、`private/`、`private_data/`、`ollama/`、`lmstudio/`、`work/` 配下の実作業データを public な tracked files に混ぜません。ドキュメントにローカルパスを書く場合は、ユーザー環境の前提として必要なものだけに限定します。
