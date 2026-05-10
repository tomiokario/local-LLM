# RTX 4060 Ti 16GB で始めるローカル LLM 入門

このリポジトリは、RTX 4060 Ti 16GB の PC でローカル LLM を学び、試し、少しずつ自分の研究・教育・日常作業に使える形へ育てるための教材兼作業場です。

最初の入口は Jupyter Notebook です。README は全体の地図として使い、実際の学習は Notebook から始めます。

## まず開くもの

```text
notebooks/local_llm_customization_lab.ipynb
```

この Notebook では、ローカル LLM の基本的な使い方、プロンプト設計、RAG、ツール連携、LoRA / QLoRA、継続事前学習、評価と運用の考え方を、軽量なサンプルで順番に確認します。

Notebook の補足は [`notebooks/README.md`](notebooks/README.md) にあります。

## このリポジトリで学ぶこと

- ローカル LLM を自分の PC で動かすための最小セットアップ
- RTX 4060 Ti 16GB で扱いやすい量子化モデルの目安
- Ollama と LM Studio の使い分け
- Notebook を使ったローカル LLM 入門
- プロンプト設計、RAG、ツール連携、LoRA / QLoRA、継続事前学習の位置づけ
- 評価と安全確認
- Cline や aider からローカル LLM を使う基本方針

## 学習の進め方

1. [`notebooks/local_llm_customization_lab.ipynb`](notebooks/local_llm_customization_lab.ipynb) を開く
2. Notebook のセルを上から順に実行し、ローカル LLM の全体像をつかむ
3. 詳しく知りたい章を [`docs/local-llm-customization/`](docs/local-llm-customization/) で読む
4. Ollama や LM Studio で実際のモデルを動かす
5. 自分の資料や作業に合わせて、RAG やツール連携を小さく試す

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

Ollama のモデル保存先をこのリポジトリ配下にまとめたい場合は、次の環境変数を設定します。

```powershell
setx OLLAMA_MODELS "C:\LLM\ollama"
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

文章作成、要約、推敲、読みやすい説明には Gemma 系をまず試します。

コード、技術文書、リポジトリ調査、agentic coding には Qwen 系をまず試します。

重要なレビューや判断では、1つのモデルだけで結論を出さず、Gemma と Qwen の両方で確認するのが安全です。

## ディレクトリ

```text
C:\LLM
  docs
    local-llm-customization
    repository-design.md
  notebooks
    local_llm_customization_lab.ipynb
    data
  notes
  scripts
  work
  ollama
  lmstudio
```

主な場所:

- [`notebooks/`](notebooks/): 最初に触る Notebook 教材
- [`docs/local-llm-customization/`](docs/local-llm-customization/): Notebook と対応する読み物教材
- [`scripts/`](scripts/): セットアップ、環境確認、モデル取得、aider 起動用スクリプト
- [`notes/`](notes/): LM Studio や Cline などの補足メモ
- [`docs/repository-design.md`](docs/repository-design.md): このリポジトリの設計・運用方針
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
