# Notebook 教材

このディレクトリには、RTX 4060 Ti 16GB でローカル LLM を学ぶための Jupyter Notebook 教材を置きます。

学習の本体は `local-llm-customization/` 配下に、1章1 Notebook で分けています。旧来の単一 Notebook へのリンクを踏んだ場合も迷わないように、`local_llm_customization_lab.ipynb` は案内ページとして残しています。

## 章構成

| 章 | Notebook | 内容 |
|---:|---|---|
| 0 | [`local-llm-customization/00-index.ipynb`](local-llm-customization/00-index.ipynb) | 全体の目次と進め方 |
| 1 | [`local-llm-customization/01-overview.ipynb`](local-llm-customization/01-overview.ipynb) | Ollama 確認、Python API、Chat UI、aider の安全な入口 |
| 2 | [`local-llm-customization/02-prompt-design.ipynb`](local-llm-customization/02-prompt-design.ipynb) | Chat UI と Python API で短い依頼と構造化依頼を比較する |
| 3 | [`local-llm-customization/03-rag.ipynb`](local-llm-customization/03-rag.ipynb) | Markdown 教材を検索し、根拠なし回答と根拠つき回答を比べる |
| 4 | [`local-llm-customization/04-tool-use.ipynb`](local-llm-customization/04-tool-use.ipynb) | Chat UI、API、エージェンティック coding、文書やコードのレビューを作業の入口として使い分ける |
| 5 | [`local-llm-customization/05-lora-qlora.ipynb`](local-llm-customization/05-lora-qlora.ipynb) | 事前学習済みモデルに LoRA adapter を付け、教材データで実学習する |
| 6 | [`local-llm-customization/06-continued-pretraining.ipynb`](local-llm-customization/06-continued-pretraining.ipynb) | 教材コーパスで continued-pretraining 風の追加学習を実行する |
| 7 | [`local-llm-customization/07-evaluation-operation.ipynb`](local-llm-customization/07-evaluation-operation.ipynb) | 評価ケース、回帰確認、運用チェック |

## データ

- `data/sample_measurements.csv`: API 呼び出しや確認練習用の教材サンプル
- `data/lora_dummy_dataset.jsonl`: LoRA / QLoRA 形式確認用の教材サンプル
- `data/continued_pretraining_corpus.txt`: 追加学習を検討する時の教材サンプル

## 使い方

Notebook は repository のルートを基準に、`docs/local-llm-customization/` の Markdown 教材を読み込みます。

Ollama が起動していない環境でも、回答生成セルは処理を止めずに例外理由を表示します。第5章と第6章の学習セルは、CUDA 版 PyTorch、Transformers、PEFT を使い、事前学習済みモデルに adapter を付けて実行します。学習済み adapter やキャッシュは `work/` 配下に保存し、git には入れません。

学習セルを実行する Python 環境には、少なくとも `torch`、`transformers`、`peft`、`accelerate` が必要です。RTX 4060 Ti で検証した環境では CUDA 版 PyTorch を使いました。既定の検証モデルは `Qwen/Qwen2.5-0.5B-Instruct` です。

RTX 4060 Ti 16GB での確認結果（2026-05-10、`notebooks/local-llm-customization/05-lora-qlora.ipynb` と `06-continued-pretraining.ipynb` のコードセルを検証用 venv で実行）:

- GPU: NVIDIA GeForce RTX 4060 Ti, 16,380 MiB VRAM
- Python training stack: `torch 2.11.0+cu128`, `transformers 5.8.0`, `peft 0.19.1`, `accelerate 1.13.0`
- 第5章 LoRA: `Qwen/Qwen2.5-0.5B-Instruct`, 20 steps, loss `3.5695 -> 0.0347`, peak VRAM `1434.9 MiB`
- 第6章 continued-pretraining 風 LoRA: 20 steps, loss `3.5899 -> 0.0917`, peak VRAM `1411.1 MiB`

## サンプルの扱い

Notebook に入れるサンプルは、公開可否を確認済みの教材用データだけにしてください。公開向けの README や教材では、非公開データの具体的な種類を列挙しません。
