# リポジトリ設計・運用方針

この文書は、このリポジトリの設計方針と運用上の境界をまとめます。初学者向けの入口は [`../README.md`](../README.md) に置き、この文書ではリポジトリを保守するときの考え方を扱います。

## 位置づけ

このリポジトリは、RTX 4060 Ti 16GB の PC でローカル LLM を学び、検証し、日常的に使うための作業場です。

## 基本ディレクトリ

作業場所は任意のディレクトリに置けます。以下ではリポジトリのルートを `<repo-root>` と表します。

```text
<repo-root>
  docs
  notebooks
    local-llm-customization
    data
  notes
  scripts
  work
  ollama
  lmstudio
```

各ディレクトリの役割:

- `docs/`: 公開してよい説明資料、設計メモ、教材本文
- `docs/local-llm-customization/`: ローカル LLM カスタマイズ入門の読み物教材
- `notebooks/`: 最初に学ぶための Jupyter Notebook 教材
- `notebooks/local-llm-customization/`: 1章ごとに分けた入門 Notebook
- `notebooks/data/`: Notebook 用の教材サンプル
- `notes/`: LM Studio、Cline、Ollama などの補足メモ
- `scripts/`: セットアップ、環境確認、モデル取得、aider 起動などの PowerShell スクリプト
- `work/`: ローカル作業用プロジェクト置き場
- `ollama/`: Ollama のモデル保存先
- `lmstudio/`: LM Studio のモデル保存先

## Notebook を入口にする理由

このリポジトリは、最初に Notebook で学べる構成にします。

Notebook を入口にすると、説明、コード、出力、失敗時の確認を同じ場所に置けます。ローカル LLM に初めて触る人でも、環境確認、プロンプト、RAG、ツール連携、評価の流れを手で動かしながら理解できます。

Markdown 教材は Notebook の補助線として使います。じっくり読みたい内容は `docs/local-llm-customization/` に置き、Notebook から参照します。

Notebook は 1 章 1 ファイルを基本にします。README から目次 Notebook へ進み、各章へリンクで移動できる状態を保ちます。

## RTX 4060 Ti 16GB 前提

この PC では、13GB から 15GB 程度の量子化モデルを主な運用対象にします。

19GB 級以上のモデルは、CPU/RAM オフロードが増えやすく、速度や安定性が落ちます。品質確認や重要なレビューで試す候補に留めます。

コンテキスト長は最初から大きくしすぎず、16K から 32K 程度で試します。長いコンテキストは VRAM を圧迫しやすいため、用途に応じて段階的に増やします。

## モデルと用途の考え方

文書作成、要約、推敲、読みやすい説明では Gemma 系を第一候補にします。

コード、技術文書、リポジトリ調査、agentic coding では Qwen 系を第一候補にします。

重要な確認や判断では、1つのモデルだけで結論を出さず、Gemma と Qwen の両方で確認します。

## ツールの役割

- Ollama: CLI やエージェント連携で使うローカル LLM 実行基盤
- LM Studio: GUI でモデルを試す、文書やマルチモーダル対応を確認する
- Cline: VS Code 上で調査から編集まで対話的に進める
- aider: ターミナルで差分を見ながら堅実に編集する
- Jupyter Notebook: 初学者向け教材と軽量な実験環境

## Agentic Coding の扱い

このリポジトリで Codex が作業するときの正本ルールは [`../AGENTS.md`](../AGENTS.md) です。

複数ファイル変更、PowerShell スクリプト修正、モデル評価、運用ルール変更、Issue 対応のように失敗時の影響が大きい作業では、レビュー観点を明確にしてから完了扱いにします。

複数タスクを同時に進める場合は、repository 内の gitignored な `tmp/worktrees/` に task ごとの worktree を作り、branch と Codex スレッドを分けます。詳細なローカル進行メモは tracked files に置かず、公開してよい運用ルールだけを `AGENTS.md` と `.codex/agents/*` に残します。

## 初期セットアップの流れ

1. 任意の作業ディレクトリへこのリポジトリを clone する
2. Ollama をインストールする
3. `OLLAMA_MODELS` を `<repo-root>\ollama` に設定する
4. Ollama を再起動する
5. 最小構成のモデルを pull する
6. `ollama run` で短いプロンプトを試す
7. `nvidia-smi` で VRAM 使用量を確認する
8. LM Studio でモデル保存先を `<repo-root>\lmstudio` にする
9. Cline や aider から Ollama 接続を確認する

## 保守時の注意

README は初学者向けの入口として保ちます。内部向けの設計判断、運用ルール、エージェント作業手順は README に厚く書かず、`docs/` や `AGENTS.md` に分けます。

教材や Notebook を更新するときは、README、Notebook、`docs/local-llm-customization/` の導線がずれていないか確認します。
