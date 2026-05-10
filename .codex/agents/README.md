# Repo Local Agent Definitions

このディレクトリには、このリポジトリの作業で再利用するマルチエージェント役割定義を置きます。実際の subagent 起動では、親オーケストレータが該当する TOML の role / instructions / 出力形式を同等設定へ写して使います。

## 役割

- [question-agent.toml](./question-agent.toml): 不足仕様、変更タイプ、検証観点、受け入れ条件を整理する。
- [implementation-agent.toml](./implementation-agent.toml): 合意済み仕様に従って編集し、検証結果と evidence handoff を返す。
- [notebook-experience-review-agent.toml](./notebook-experience-review-agent.toml): Notebook や教材を読者順に実行し、意図した体験が成立するか確認する。
- [fresh-review-agent.toml](./fresh-review-agent.toml): 実装者とは別視点で、現在差分と検証結果を確認する。
- [intent-review-agent.toml](./intent-review-agent.toml): ユーザーの意図と差分がずれていないか確認する。

## Pre Completion Review Gate

完了扱い、commit、push、PR 作成の前に、必要に応じて次の順で確認します。

Notebook、教材、GUI、clipboard、外部プロセス起動を含む作業では、静的な JSON parse、構文確認、リンク確認だけでは完了扱いにしません。親オーケストレータまたは実装担当が、対象セルや手順を読者の順序で実行し、意図した体験が得られるかを evidence として渡します。

完了報告後にユーザーから手順、セル実行、体験導線、レビュー観点の問題が報告された場合は、前回の acceptance criteria が不足していたものとして扱います。question-agent が不足条件を整理し、必要な実行条件を追加してから、notebook-experience review、fresh review、intent review を再実行します。

1. `notebook-experience-review-agent`
   - 対象 Notebook や手順を読者の順序で実行し、出力、GUI、clipboard、外部プロセス、終了方法、実行後の作業ツリー状態を evidence として返す。
2. `fresh-review-agent`
   - 現在差分、関連 docs/tests、実行体験 evidence、公開可否の境界を確認する。
3. `intent-review-agent`
   - ユーザーの依頼、会話で固まった意図、受け入れ条件と実際に得られた体験の整合を確認する。

どちらかが blocker を返した場合は修正し、該当レビューを再実行してから次へ進みます。

## 公開可否の境界

この repository では、公開可否を確認できない設定、生成物、データ、作業状態を public な tracked files に混ぜません。公開向けの文書では、非公開データの具体的な種類を列挙しません。
