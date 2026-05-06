# Notebook 教材

このディレクトリには、軽量ローカル LLM カスタマイズ入門の実習 Notebook を置きます。

## ファイル

- `local_llm_customization_lab.ipynb`: Issue #1 対応の自己完結型 Notebook 教材。
- `data/sample_measurements.csv`: CSV / ツール連携用の公開ダミーデータ。
- `data/lora_dummy_dataset.jsonl`: LoRA / QLoRA 形式確認用の公開ダミーデータ。
- `data/continued_pretraining_corpus.txt`: 継続事前学習の tokenizer 確認用の公開ダミーコーパス。

## 使い方

Notebook は `C:\LLM` repository のルートを基準に、`docs/local-llm-customization/` の Markdown 教材を読み込みます。

Ollama が起動していない環境でも、回答生成セルは例外理由を表示して止まります。実学習セルは `RUN_TRAINING = False` を既定値にしており、設定確認とデータ形状の確認だけを行います。

## ローカル専用データの扱い

この Notebook に入れるサンプルは公開ダミーデータだけにしてください。実験ログ、学生情報、未公開論文、モデル本体、個人用メモは `private_data/` やローカル作業領域に置き、Notebook 配下へ混ぜないでください。
