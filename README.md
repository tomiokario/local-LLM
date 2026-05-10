# RTX 4060 Ti 16GB で始めるローカル LLM 入門

このリポジトリは、RTX 4060 Ti 16GB の PC でローカル LLM を学び、試し、少しずつ文書作成、コーディング、確認作業などに使える形へ育てるための教材兼作業場です。

最初の入口は Jupyter Notebook です。README は全体の地図として使い、実際の学習は章ごとの Notebook から始めます。

## まず開くもの

- [Notebook 目次](notebooks/local-llm-customization/00-index.ipynb)
- [Notebook 補足 README](notebooks/README.md)

単一 Notebook への旧リンクは [`notebooks/local_llm_customization_lab.ipynb`](notebooks/local_llm_customization_lab.ipynb) に案内ページとして残しています。新しく学ぶ場合は、章ごとに分かれた Notebook を使ってください。

## Notebook 目次

| 章 | Notebook | 学ぶこと |
|---:|---|---|
| 0 | [目次](notebooks/local-llm-customization/00-index.ipynb) | 全体像、章構成、進め方 |
| 1 | [ローカル LLM の基本操作](notebooks/local-llm-customization/01-overview.ipynb) | Ollama 確認、Python API、Chat UI、aider の安全な入口 |
| 2 | [プロンプト設計](notebooks/local-llm-customization/02-prompt-design.ipynb) | Chat UI と Python API で短い依頼と構造化依頼を比較する |
| 3 | [RAG](notebooks/local-llm-customization/03-rag.ipynb) | Markdown 教材を検索し、根拠なし回答と根拠つき回答を比べる |
| 4 | [活用ワークフロー](notebooks/local-llm-customization/04-tool-use.ipynb) | Chat UI、API、エージェンティック coding、文書やコードのレビューを作業の入口として使い分ける |
| 5 | [LoRA / QLoRA](notebooks/local-llm-customization/05-lora-qlora.ipynb) | 事前学習済みモデルに LoRA adapter を付け、教材データで実学習する |
| 6 | [追加学習の判断と実践](notebooks/local-llm-customization/06-continued-pretraining.ipynb) | 教材コーパスで continued-pretraining 風の追加学習を実行する |
| 7 | [評価と運用](notebooks/local-llm-customization/07-evaluation-operation.ipynb) | 評価ケース、回帰確認、運用チェック |

補足の読み物は [`docs/local-llm-customization/`](docs/local-llm-customization/) にあります。Notebook で手を動かし、必要に応じて docs で考え方を読み返す構成です。

## このリポジトリで学ぶこと

- ローカル LLM を自分の PC で動かすための最小セットアップ
- RTX 4060 Ti 16GB で扱いやすい量子化モデルの目安
- Ollama と LM Studio の使い分け
- Notebook を使ったローカル LLM 入門
- プロンプト設計、RAG、ツール連携、LoRA / QLoRA、継続事前学習の位置づけ
- 評価と安全確認
- Chat UI、Cline、aider、文書やコードのレビューでローカル LLM を使う基本方針

## 学習の進め方

1. [Notebook 目次](notebooks/local-llm-customization/00-index.ipynb) を開く
2. 第1章から第4章までを順番に実行し、呼び出し、プロンプト、RAG、Chat UI、エージェンティック coding、文書やコードのレビューの入口を理解する
3. 第5章と第6章で、活用しても残る不足から LoRA や追加学習を実際に短く試す
4. 第7章で、評価ケースと運用チェックを作る
5. 詳しく知りたい章を [`docs/local-llm-customization/`](docs/local-llm-customization/) で読む

ファインチューニングは最初の目的地ではありません。まずは「手元のモデルに、資料と道具と評価を組み合わせる」ことから始めます。

## セットアップ

PowerShell でリポジトリのルートに移動し、環境確認を行います。

```powershell
.\scripts\setup.ps1
.\scripts\check-env.ps1
```

Ollama と aider も入れる場合は、次のように実行します。

```powershell
.\scripts\setup.ps1 -InstallOllama -InstallAider
```

PowerShell、Ollama、LM Studio を再起動した後、最小モデルを取得します。

```powershell
.\scripts\pull-minimal.ps1
```

第5章と第6章の実学習 Notebook を動かす Python 環境には、CUDA 版 PyTorch、Transformers、PEFT、Accelerate が必要です。環境に合わせて Python 仮想環境を作り、例として次のように導入します。

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install torch --index-url https://download.pytorch.org/whl/cu128
.\.venv\Scripts\python -m pip install transformers peft accelerate sentencepiece protobuf ipykernel
.\.venv\Scripts\python -m ipykernel install --user --name local-llm-training --display-name "local-llm-training"
```

Notebook の既定モデルは `Qwen/Qwen2.5-0.5B-Instruct` です。モデルキャッシュ、adapter、検証ログは `work/` 配下に置き、git には入れません。

Ollama のモデル保存先をこのリポジトリ配下にまとめたい場合は、次の環境変数を設定します。

```powershell
$repo = (Resolve-Path .).Path
setx OLLAMA_MODELS (Join-Path $repo "ollama")
```

設定後は Ollama を再起動してからモデルを pull してください。

## RTX 4060 Ti 16GB での目安

この PC では、13GB から 15GB 程度の量子化モデルが扱いやすい目安です。19GB 級以上のモデルも動く可能性はありますが、CPU/RAM オフロードが増えやすく、速度や安定性が落ちます。

- 13GB から 15GB 級: 現実的に運用しやすい
- 19GB 級以上: 品質確認用の候補だが重い
- 長いコンテキスト: VRAM を圧迫しやすい
- 最初は 16K から 32K 程度のコンテキストで試す

最小構成の例:

```powershell
ollama pull batiai/gemma4-26b:iq4
ollama pull batiai/qwen3.6-35b:iq3
```

余裕があれば追加する候補:

```powershell
ollama pull batiai/qwen3.6-35b:iq4
ollama pull gemma4:e4b
```

## 使い分けの目安

文書作成、要約、添削、読みやすい説明には Gemma 系をまず試します。

コード、技術文書、リポジトリ調査、agentic coding には Qwen 系をまず試します。

重要な確認や判断では、1つのモデルだけで結論を出さず、Gemma と Qwen の両方で確認するのが安全です。

## ディレクトリ

```text
<repo-root>
  docs
    local-llm-customization
    repository-design.md
  notebooks
    local-llm-customization
      00-index.ipynb
      01-overview.ipynb
      ...
      07-evaluation-operation.ipynb
    local_llm_customization_lab.ipynb
    data
  notes
  scripts
  work
  ollama
  lmstudio
```

主な場所:

- [`notebooks/local-llm-customization/`](notebooks/local-llm-customization/): 章ごとの入門 Notebook
- [`notebooks/README.md`](notebooks/README.md): Notebook の補足
- [`docs/local-llm-customization/`](docs/local-llm-customization/): Notebook と対応する読み物教材
- [`scripts/`](scripts/): セットアップ、環境確認、モデル取得、aider 起動用スクリプト
- [`notes/`](notes/): LM Studio や Cline などの補足メモ
- [`docs/repository-design.md`](docs/repository-design.md): このリポジトリの設計と運用方針
- [`AGENTS.md`](AGENTS.md): Codex など AI エージェントがこのリポジトリで作業するためのルール

## 動作確認

GPU 確認:

```powershell
nvidia-smi
```

Ollama 確認:

```powershell
ollama --version
ollama list
```

モデル実行例:

```powershell
ollama run batiai/gemma4-26b:iq4
ollama run batiai/qwen3.6-35b:iq3
```

## 参考リンク

- [Ollama Windows](https://docs.ollama.com/windows)
- [Ollama GPU support](https://docs.ollama.com/gpu)
- [Gemma 4 on Ollama](https://ollama.com/library/gemma4)
- [BatiAI Gemma4 26B](https://ollama.com/batiai/gemma4-26b%3Alatest)
- [BatiAI Qwen3.6 35B](https://ollama.com/batiai/qwen3.6-35b)
- [LM Studio docs](https://lmstudio.ai/docs/app/)
- [Cline Ollama integration](https://docs.ollama.com/integrations/cline)
- [aider Ollama](https://aider.chat/docs/llms/ollama.html)
