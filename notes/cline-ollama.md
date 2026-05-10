# Cline + Ollama 接続メモ

VS Code の Cline から Ollama を使う時は、まず Ollama が起動していることを確認します。

```powershell
ollama --version
ollama list
```

Cline 側のモデル指定は、Ollama provider を選び、用途に応じて次を使います。

```text
batiai/qwen3.6-35b:iq3
batiai/gemma4-26b:iq4
```

最初はコンテキストを 16K から 32K 程度にして、`nvidia-smi` で VRAM 使用量を確認します。
