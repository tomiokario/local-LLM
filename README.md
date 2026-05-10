# RTX 4060 Ti 16GB ローカルLLM運用メモ

このメモは、このPCでローカルLLMをできるだけシンプルに運用するための方針です。

## このプロジェクトで追加した実行環境

このディレクトリには、方針に沿って環境を作るためのスクリプトと設定ファイルを置きます。

```text
<repo-root>
  scripts
    setup.ps1
    check-env.ps1
    pull-minimal.ps1
    pull-extra.ps1
    start-aider.ps1
  .aider.conf.yml
  .env.example
```

最初に実行するコマンド:

```powershell
.\scripts\setup.ps1
.\scripts\check-env.ps1
```

Ollama と aider も入れる場合:

```powershell
.\scripts\setup.ps1 -InstallOllama -InstallAider
```

PowerShell、Ollama、LM Studio を再起動した後、最小モデルを取得します。

```powershell
.\scripts\pull-minimal.ps1
```

aider は次で起動します。

```powershell
.\scripts\start-aider.ps1
```

## 作業場所

作業ディレクトリは任意の場所に置けます。以下ではリポジトリのルートを `<repo-root>` と表します。

```powershell
<repo-root>
```

モデル、作業用プロジェクト、設定メモはこの配下に置きます。

```text
<repo-root>
  ollama
  lmstudio
  work
  notes
```

Ollamaのモデル保存先は次のように設定します。

```powershell
$repo = (Resolve-Path .).Path
setx OLLAMA_MODELS (Join-Path $repo "ollama")
```

設定後は、Ollamaを再起動してからモデルをpullします。

## PC前提

このPCはRTX 4060 Ti 16GB搭載です。

ローカルLLMでは、13GBから15GB程度の量子化モデルが現実的です。19GB級以上はCPU/RAMオフロード前提になりやすく、速度や安定性が落ちます。

目安:

- 13GBから15GB級: 現実的に運用しやすい
- 19GB級以上: 動く可能性はあるが重い
- 長いコンテキスト: VRAMを圧迫しやすい
- まずは16Kから32K程度で試す

## まず入れる最小構成

```powershell
ollama pull batiai/gemma4-26b:iq4
ollama pull batiai/qwen3.6-35b:iq3
```

## 余裕があれば追加

```powershell
ollama pull batiai/qwen3.6-35b:iq4
ollama pull gemma4:e4b
```

`batiai/qwen3.6-35b:iq4` は19GB級になりやすいため、このPCでは重めです。品質を上げたい時や重要なレビューで試す候補にします。

## 文書作成・要約・推敲

用途:

- メール
- 議事録
- 要約
- 定型文作成
- 文書作成
- 文体調整
- トーン調整
- 構成案
- リライト
- 短い下書き
- 高速な言い換え

使うアプリ:

- LM Studio
- Ollama

使うモデル:

- 第一候補: Gemma 4 26B-A4B IQ4
- 第二候補: Gemma 4 E4B Q4系

Gemma 4 26B-A4B IQ4は、文章の安定感、要約、読みやすい説明、文書の整形に向いています。

短い下書きや軽い要約を速く済ませたい時は、Gemma 4 E4Bを使います。

## 文書レビュー・PDF確認

用途:

- 文書
- 報告書
- 申請書
- 技術文書
- 図表
- 画像
- PDF
- スクリーンショットを含む文書の確認

使うアプリ:

- LM Studio
- 必要に応じてOllama

使うモデル:

- 第一候補: Gemma 4 26B-A4B IQ4
- 第二候補: Qwen3.6-35B-A3B IQ3

文書全体の構成、文章表現、主張の一貫性を見るならGemmaを使います。

技術内容、コード、アルゴリズムが絡む文書ではQwenも使います。

重要な確認では、1つのモデルだけで結論を出さず、GemmaとQwenの両方で確認するのが安全です。

画像入力を使いたい場合、Ollama版はtext-onlyのものがあるため、LM Studioでマルチモーダル対応モデルとして読み込めるか確認します。

## Agentic Coding・Code Review

用途:

- リポジトリ調査
- 実装
- 修正
- テスト方針の検討
- 差分レビュー
- バグ探し
- 境界条件の確認

使うアプリ:

- Cline + Ollama
- aider + Ollama

使うモデル:

- 第一候補: Qwen3.6-35B-A3B IQ3
- 第二候補: Qwen3.6-35B-A3B IQ4

Qwen 3.6は、agentic coding、repository-level reasoning、tool useが強化されているため、まずはIQ3で使います。

IQ4は品質を上げたい時や重要なレビューで試します。ただし約19GB級なので、このPCでは重いです。

使い分け:

- Cline + Ollama: VS Code上で、調査から編集まで対話的に進める時
- aider + Ollama: ターミナルで、差分を見ながら堅実に編集する時

Clineではコンテキスト長を大きくしすぎるとVRAMを圧迫します。まずは16Kから32K程度で試します。

aiderでは次の形式を使います。

```text
ollama_chat/<model>
```

## Codex マルチエージェント運用

このリポジトリで Codex が作業するときの正本ルールは [`AGENTS.md`](AGENTS.md) です。

複数ファイル変更、PowerShell スクリプト修正、モデル評価、運用ルール変更、Issue 対応のように失敗時の影響が大きい作業では、親オーケストレータ、質問担当、実装担当、fresh review 担当、intent review 担当の役割に分けて進めます。再利用用の役割定義は [`.codex/agents/`](.codex/agents/) に置いています。

複数タスクを同時に進める場合は、repository 内の gitignored な `tmp/worktrees/` に task ごとの worktree を作り、branch と Codex スレッドを分けます。詳細なローカル進行メモは tracked files に置かず、公開してよい運用ルールだけを `AGENTS.md` と `.codex/agents/*` に残します。

## 初期セットアップ手順

1. 任意の作業ディレクトリへこのリポジトリを clone する
2. Ollamaをインストールする
3. `OLLAMA_MODELS`を`<repo-root>\ollama`に設定する
4. Ollamaを再起動する
5. 最小構成の2モデルをpullする
6. `ollama run`で短いプロンプトを試す
7. `nvidia-smi`でVRAM使用量を確認する
8. LM Studioでモデル保存先を`<repo-root>\lmstudio`にする
9. Cline/aiderからOllama接続を確認する

## 動作確認コマンド

GPU確認:

```powershell
nvidia-smi
```

Ollama確認:

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
