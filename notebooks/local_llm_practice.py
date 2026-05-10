from __future__ import annotations

import json
import os
import random
import re
import shutil
import socket
import subprocess
import threading
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterable
from urllib import request


def find_repo_root(start: str | Path | None = None) -> Path:
    """Find the repository root from a notebook or helper execution path."""
    starts = []
    if start is not None:
        starts.append(Path(start))
    env_root = os.environ.get("LOCAL_LLM_REPO_ROOT")
    if env_root:
        starts.append(Path(env_root))
    starts.extend([Path.cwd(), Path(__file__).resolve().parent, Path("C:/LLM")])

    seen = set()
    for start_path in starts:
        current = start_path.resolve()
        for candidate in [current, *current.parents]:
            if candidate in seen:
                continue
            seen.add(candidate)
            if (candidate / "README.md").exists() and (
                candidate / "docs" / "local-llm-customization"
            ).exists():
                return candidate
    raise RuntimeError(
        "repository root が見つかりません。C:/LLM か notebooks/ 配下で開くか、"
        "LOCAL_LLM_REPO_ROOT を repository root に設定してください。"
    )


REPO_ROOT = find_repo_root()
DOCS_DIR = REPO_ROOT / "docs" / "local-llm-customization"
DATA_DIR = REPO_ROOT / "notebooks" / "data"
WORK_DIR = REPO_ROOT / "work" / "local-llm-training"
HF_HOME = REPO_ROOT / "work" / "hf-cache"
DEFAULT_OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "batiai/gemma4-26b:iq4")
_CHAT_UI_SERVER: ThreadingHTTPServer | None = None
_CHAT_UI_PORT: int | None = None
_AIDER_PROCESS_IDS: list[int] = []


def configure_local_caches() -> None:
    """Keep downloaded models and generated artifacts out of tracked files."""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    HF_HOME.mkdir(parents=True, exist_ok=True)
    os.environ["HF_HOME"] = str(HF_HOME)
    os.environ["TRANSFORMERS_CACHE"] = str(HF_HOME / "transformers")
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


def prepare_aider_practice_workspace() -> Path:
    """Create a gitignored practice workspace so aider exercises do not touch the repo."""
    practice_dir = REPO_ROOT / "work" / "aider-practice"
    practice_dir.mkdir(parents=True, exist_ok=True)
    source_readme = REPO_ROOT / "README.md"
    target_readme = practice_dir / "README.md"
    if source_readme.exists() and not target_readme.exists():
        shutil.copyfile(source_readme, target_readme)
    notes = practice_dir / "NOTES.md"
    if not notes.exists():
        notes.write_text(
            "# Aider practice workspace\n\n"
            "このフォルダは Notebook の agentic AI 体験用です。"
            "gitignored な `work/` 配下にあるため、教材 repository の tracked files は変更しません。\n",
            encoding="utf-8",
        )
    print("aider 練習用 workspace:", practice_dir)
    print("このフォルダは gitignored な work/ 配下にあります。")
    return practice_dir


def _powershell_exe() -> str:
    return os.environ.get("POWERSHELL_EXE", "powershell")


def _powershell_quote(value: str | Path) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def run_powershell(command: str, *, wait: bool = True):
    """Run a small PowerShell command with UTF-8 console settings."""
    encoding_prefix = (
        "$OutputEncoding = [System.Text.UTF8Encoding]::new(); "
        "[Console]::InputEncoding = [System.Text.Encoding]::UTF8; "
        "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
    )
    args = [
        _powershell_exe(),
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        encoding_prefix + command,
    ]
    if wait:
        return subprocess.run(args, text=True, capture_output=True, encoding="utf-8")
    return subprocess.Popen(args)


def check_ollama() -> None:
    """Print basic Ollama status for beginner notebooks."""
    for command in ["ollama --version", "ollama list"]:
        print(f"\n> {command}")
        result = run_powershell(command)
        print(result.stdout or result.stderr)


def copy_to_clipboard(text: str) -> None:
    """Copy prompt text to the Windows clipboard, with a printable fallback."""
    command = (
        "[Console]::InputEncoding = [System.Text.Encoding]::UTF8; "
        "Set-Clipboard -Value ([Console]::In.ReadToEnd())"
    )
    try:
        result = subprocess.run(
            [
                _powershell_exe(),
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                command,
            ],
            input=text,
            text=True,
            capture_output=True,
            encoding="utf-8",
            timeout=10,
        )
    except Exception as exc:
        print("クリップボードへコピーできませんでした。下のテキストを手でコピーしてください。")
        print(f"{type(exc).__name__}: {exc}")
        print(text)
        return

    if result.returncode == 0:
        print("Windows のクリップボードへコピーしました。Chat UI で Ctrl+V して使えます。")
    else:
        print("クリップボードへコピーできませんでした。下のテキストを手でコピーしてください。")
        print(result.stderr)
        print(text)


def _local_port_is_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.2):
            return True
    except OSError:
        return False


def start_ollama_chat_ui(model: str = DEFAULT_OLLAMA_MODEL, port: int = 7860) -> str:
    """Start a tiny browser chat UI that talks to the local Ollama API."""
    global _CHAT_UI_SERVER, _CHAT_UI_PORT

    html = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ollama Mini Chat</title>
<style>
body { font-family: system-ui, sans-serif; margin: 0; background: #f6f7f9; color: #1f2328; }
main { max-width: 900px; margin: 0 auto; padding: 24px; }
h1 { font-size: 24px; margin: 0 0 8px; }
#chat { background: white; border: 1px solid #d0d7de; min-height: 360px; padding: 16px; overflow-y: auto; }
.msg { margin: 0 0 14px; padding: 10px 12px; border-radius: 8px; white-space: pre-wrap; line-height: 1.55; }
.user { background: #ddf4ff; }
.assistant { background: #f0f0f0; }
.error { background: #ffebe9; }
textarea { width: 100%; min-height: 110px; margin-top: 12px; font: inherit; padding: 10px; box-sizing: border-box; }
button { margin-top: 8px; padding: 8px 14px; font: inherit; }
small { color: #57606a; }
</style>
</head>
<body>
<main>
<h1>Ollama Mini Chat</h1>
<p><small>model: MODEL_NAME / local Ollama API: http://localhost:11434</small></p>
<div id="chat"></div>
<textarea id="input" placeholder="ここに質問を書いて、送信を押します。Ctrl+Enter でも送信できます。"></textarea>
<br><button id="send">送信</button>
</main>
<script>
const chat = document.getElementById('chat');
const input = document.getElementById('input');
function add(role, text) {
  const div = document.createElement('div');
  div.className = 'msg ' + role;
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}
async function send() {
  const prompt = input.value.trim();
  if (!prompt) return;
  input.value = '';
  add('user', prompt);
  add('assistant', '生成中...');
  const pending = chat.lastChild;
  try {
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({prompt})
    });
    const data = await res.json();
    pending.textContent = data.response || data.error || '(empty response)';
    if (data.error) pending.className = 'msg error';
  } catch (err) {
    pending.className = 'msg error';
    pending.textContent = String(err);
  }
}
document.getElementById('send').addEventListener('click', send);
input.addEventListener('keydown', (event) => {
  if (event.ctrlKey && event.key === 'Enter') send();
});
add('assistant', '準備できました。まず短い質問を入力してください。');
</script>
</body>
</html>""".replace("MODEL_NAME", model)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        def do_POST(self):
            if self.path != "/api/generate":
                self.send_error(404)
                return
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            payload = {
                "model": model,
                "prompt": body.get("prompt", ""),
                "stream": False,
                "options": {"temperature": 0.2},
            }
            req = request.Request(
                "http://localhost:11434/api/generate",
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            try:
                with request.urlopen(req, timeout=120) as res:
                    data = json.loads(res.read().decode("utf-8"))
                out = {"response": data.get("response", "")}
            except Exception as exc:
                out = {"error": f"Ollama 呼び出しに失敗しました: {type(exc).__name__}: {exc}"}
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(out, ensure_ascii=False).encode("utf-8"))

        def log_message(self, format, *args):
            return

    if _CHAT_UI_SERVER is None:
        last_error = None
        for candidate_port in range(port, port + 10):
            if _local_port_is_open(candidate_port):
                last_error = OSError(f"port {candidate_port} is already in use")
                continue
            try:
                server = ThreadingHTTPServer(("127.0.0.1", candidate_port), Handler)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                _CHAT_UI_SERVER = server
                _CHAT_UI_PORT = candidate_port
                break
            except OSError as exc:
                last_error = exc
        if _CHAT_UI_SERVER is None:
            raise RuntimeError(f"Chat UI 用のポートを開けませんでした: {last_error}")

    url = f"http://127.0.0.1:{_CHAT_UI_PORT}"
    print("教材用のブラウザ Chat UI を起動しました。")
    print("ブラウザが自動で開かない場合は、次のURLを開いてください:")
    print(url)
    try:
        webbrowser.open(url)
    except Exception:
        pass
    return url


def stop_ollama_chat_ui() -> None:
    """Stop the tiny Chat UI server started in the current Notebook kernel."""
    global _CHAT_UI_SERVER, _CHAT_UI_PORT
    if _CHAT_UI_SERVER is None:
        print("この Notebook kernel で起動中の Chat UI はありません。")
        return
    port = _CHAT_UI_PORT
    _CHAT_UI_SERVER.shutdown()
    _CHAT_UI_SERVER.server_close()
    _CHAT_UI_SERVER = None
    _CHAT_UI_PORT = None
    print(f"教材用のブラウザ Chat UI を終了しました。port: {port}")


def open_aider_terminal(project_path: Path | None = None) -> None:
    """Open aider in a separate PowerShell window for a guided no-edit exercise."""
    project_path = Path(project_path or REPO_ROOT)
    script = REPO_ROOT / "scripts" / "start-aider.ps1"
    if not script.exists():
        print(f"aider 起動スクリプトが見つかりません: {script}")
        return

    inner_command = (
        f"Set-Location -LiteralPath {_powershell_quote(REPO_ROOT)}; "
        f"& {_powershell_quote(script)} -ProjectPath {_powershell_quote(project_path)}"
    )
    argument_list = [
        "-NoExit",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        inner_command,
    ]
    quoted_args = ", ".join(_powershell_quote(arg) for arg in argument_list)
    launcher = (
        f"$p = Start-Process -FilePath {_powershell_quote(_powershell_exe())} "
        f"-ArgumentList @({quoted_args}) -PassThru; $p.Id"
    )
    result = run_powershell(launcher)
    if result.returncode != 0:
        print("別 PowerShell の起動に失敗しました。下のコマンドを手元の PowerShell で実行してください。")
        print(result.stderr)
        print(
            f"& {_powershell_quote(script)} -ProjectPath "
            f"{_powershell_quote(project_path)}"
        )
        return
    process_id = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
    if process_id.isdigit():
        _AIDER_PROCESS_IDS.append(int(process_id))
        print(f"別の PowerShell で aider を起動しました。PID: {process_id}")
    else:
        print("別の PowerShell で aider を起動しました。")
    print("最初は /help と入力し、終わったら /exit で終了してください。")


def stop_aider_practice_terminals() -> None:
    """Stop terminals opened by open_aider_terminal during automated review."""
    while _AIDER_PROCESS_IDS:
        process_id = _AIDER_PROCESS_IDS.pop()
        result = run_powershell(f"Stop-Process -Id {process_id} -ErrorAction SilentlyContinue")
        if result.returncode == 0:
            print(f"aider 練習用 PowerShell を終了しました。PID: {process_id}")
        else:
            print(f"aider 練習用 PowerShell の終了確認に失敗しました。PID: {process_id}")
            print(result.stderr)


def ensure_under_work_dir(path: str | Path) -> Path:
    """Prevent model caches or adapters from being written into tracked paths."""
    resolved = Path(path).resolve()
    work_root = WORK_DIR.parent.resolve()
    if not (resolved == work_root or work_root in resolved.parents):
        raise RuntimeError(f"生成物の保存先は {work_root} 配下にしてください: {resolved}")
    return resolved


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_chapter(filename: str) -> tuple[Path, str]:
    path = DOCS_DIR / filename
    return path, read_text(path)


def print_headings(markdown: str) -> None:
    for line in markdown.splitlines():
        if line.startswith("#"):
            print(line)


def compact_markdown(markdown: str, limit: int = 9000) -> str:
    text = re.sub(r"\n{3,}", "\n\n", markdown.strip())
    return text[:limit]


def ollama_generate(
    prompt: str,
    *,
    model: str | None = None,
    temperature: float = 0.2,
    max_chars: int = 6000,
) -> str:
    """Call Ollama once. Failures become text so notebooks keep running."""
    model = model or os.environ.get("OLLAMA_MODEL", "batiai/gemma4-26b:iq4")
    url = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
    timeout = float(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "45"))
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with request.urlopen(req, timeout=timeout) as res:
            body = json.loads(res.read().decode("utf-8"))
            return body.get("response", "")[:max_chars]
    except Exception as exc:
        return f"[Ollama を呼び出せませんでした: {type(exc).__name__}: {exc}]"


def ask_about_chapter(chapter_text: str, task: str, *, temperature: float = 0.2) -> str:
    prompt = f"""
あなたは docs/local-llm-customization を使うローカル LLM 実践編の伴走者です。
次の章本文だけを根拠に、日本語で答えてください。

# 章本文
{compact_markdown(chapter_text)}

# やること
{task}
""".strip()
    return ollama_generate(prompt, temperature=temperature)


def load_jsonl(path: str | Path) -> list[dict[str, str]]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def split_markdown(path: Path, text: str) -> list[dict[str, str]]:
    chunks: list[dict[str, str]] = []
    current_title = path.name
    current: list[str] = []
    for line in text.splitlines():
        if line.startswith("## ") and current:
            chunks.append(
                {"source": path.name, "title": current_title, "text": "\n".join(current).strip()}
            )
            current = []
        if line.startswith("#"):
            current_title = line.lstrip("# ").strip()
        current.append(line)
    if current:
        chunks.append({"source": path.name, "title": current_title, "text": "\n".join(current).strip()})
    return chunks


def tokenize_for_search(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9_]+|[一-龥ぁ-んァ-ンー]{2,}", text.lower()))


def retrieve_chunks(chunks: Iterable[dict[str, str]], question: str, k: int = 4) -> list[dict[str, str]]:
    q = tokenize_for_search(question)
    scored = []
    for chunk in chunks:
        score = len(q & tokenize_for_search(chunk["text"]))
        scored.append((score, chunk))
    return [chunk for score, chunk in sorted(scored, key=lambda x: x[0], reverse=True)[:k] if score > 0]


def require_training_dependencies() -> None:
    """Import training libraries only inside training notebooks."""
    missing = []
    for module in ["torch", "transformers", "peft", "accelerate"]:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    if missing:
        raise RuntimeError(
            "学習用ライブラリが不足しています: "
            + ", ".join(missing)
            + "\n例: python -m pip install torch transformers peft accelerate"
        )


def gpu_summary() -> dict[str, str | int | float | bool | None]:
    """Return the CUDA and GPU state visible to PyTorch."""
    import torch

    summary: dict[str, str | int | float | bool | None] = {
        "torch": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_version": torch.version.cuda,
        "device_count": torch.cuda.device_count(),
        "device_name": None,
        "total_vram_mib": None,
    }
    if torch.cuda.is_available():
        props = torch.cuda.get_device_properties(0)
        summary["device_name"] = props.name
        summary["total_vram_mib"] = round(props.total_memory / 1024**2)
    return summary


def nvidia_smi_summary() -> str:
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.used,driver_version",
                "--format=csv",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.stdout.strip() or result.stderr.strip()
    except Exception as exc:
        return f"nvidia-smi を呼び出せませんでした: {type(exc).__name__}: {exc}"


@dataclass
class TrainingConfig:
    model_id: str = "Qwen/Qwen2.5-0.5B-Instruct"
    max_length: int = 192
    max_steps: int = 20
    learning_rate: float = 2e-4
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    seed: int = 42


def set_seed(seed: int) -> None:
    import torch

    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_base_model(config: TrainingConfig):
    """Load a public pretrained causal LM onto the RTX 4060 Ti when available."""
    configure_local_caches()
    require_training_dependencies()
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA が使えません。RTX 4060 Ti での実学習確認には CUDA 版 PyTorch が必要です。")

    tokenizer = AutoTokenizer.from_pretrained(config.model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    model = AutoModelForCausalLM.from_pretrained(
        config.model_id,
        dtype=torch.float16,
        device_map={"": "cuda"},
    )
    model.config.use_cache = False
    return tokenizer, model


def lora_target_modules(model) -> list[str]:
    """Pick attention/MLP projection modules that exist in the loaded architecture."""
    suffixes = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    found = set()
    for name, _module in model.named_modules():
        tail = name.rsplit(".", 1)[-1]
        if tail in suffixes:
            found.add(tail)
    return [name for name in suffixes if name in found]


def attach_lora(model, config: TrainingConfig):
    """Freeze the base model and attach trainable LoRA adapter weights."""
    from peft import LoraConfig, get_peft_model

    peft_config = LoraConfig(
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=lora_target_modules(model),
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()
    return model


def format_sft_record(record: dict[str, str]) -> tuple[str, str]:
    prompt = f"""
### 指示
{record["instruction"]}

### 入力
{record["input"]}

### 応答
""".strip()
    answer = record["output"].strip()
    return prompt, answer


def make_sft_features(records: list[dict[str, str]], tokenizer, max_length: int) -> list[dict[str, list[int]]]:
    """Create supervised fine-tuning examples and mask the prompt tokens from loss."""
    features = []
    for record in records:
        prompt, answer = format_sft_record(record)
        full_text = prompt + "\n" + answer + tokenizer.eos_token
        full = tokenizer(full_text, truncation=True, max_length=max_length)
        prompt_ids = tokenizer(prompt + "\n", truncation=True, max_length=max_length)["input_ids"]
        labels = list(full["input_ids"])
        prompt_len = min(len(prompt_ids), len(labels))
        labels[:prompt_len] = [-100] * prompt_len
        features.append(
            {
                "input_ids": full["input_ids"],
                "attention_mask": full["attention_mask"],
                "labels": labels,
            }
        )
    return features


def make_cpt_features(texts: list[str], tokenizer, max_length: int) -> list[dict[str, list[int]]]:
    """Create plain next-token examples for continued-pretraining-style training."""
    joined = "\n\n".join(text.strip() for text in texts if text.strip())
    ids = tokenizer(joined + tokenizer.eos_token, add_special_tokens=False)["input_ids"]
    if len(ids) <= 2:
        raise RuntimeError("継続事前学習用テキストが短すぎます。")

    features = []
    step = max_length
    for start in range(0, max(1, len(ids) - 1), step):
        chunk = ids[start : start + max_length]
        if len(chunk) < 8:
            continue
        features.append(
            {
                "input_ids": chunk,
                "attention_mask": [1] * len(chunk),
                "labels": list(chunk),
            }
        )
    return features


def collate_feature(feature: dict[str, list[int]], tokenizer, device: str = "cuda"):
    import torch

    pad_id = tokenizer.pad_token_id
    input_ids = torch.tensor([feature["input_ids"]], dtype=torch.long, device=device)
    attention_mask = torch.tensor([feature["attention_mask"]], dtype=torch.long, device=device)
    labels = torch.tensor([feature["labels"]], dtype=torch.long, device=device)
    if pad_id is None:
        pad_id = tokenizer.eos_token_id
    return {"input_ids": input_ids, "attention_mask": attention_mask, "labels": labels}


def train_lora_adapter(
    model,
    tokenizer,
    features: list[dict[str, list[int]]],
    output_dir: str | Path,
    config: TrainingConfig,
) -> dict[str, float | int | str]:
    """Run a tiny real LoRA training loop and save only the adapter."""
    import torch

    if not features:
        raise RuntimeError("学習データが空です。")
    set_seed(config.seed)
    model.train()
    torch.cuda.reset_peak_memory_stats()

    optimizer = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad), lr=config.learning_rate)
    losses: list[float] = []
    for step in range(config.max_steps):
        feature = features[step % len(features)]
        batch = collate_feature(feature, tokenizer)
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad(set_to_none=True)
        losses.append(float(loss.detach().cpu()))

    output_path = ensure_under_work_dir(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_path)

    return {
        "steps": config.max_steps,
        "loss_start": losses[0],
        "loss_end": losses[-1],
        "loss_min": min(losses),
        "adapter_dir": str(output_path),
        "peak_vram_mib": round(torch.cuda.max_memory_allocated() / 1024**2, 1),
    }


def generate_text(model, tokenizer, prompt: str, max_new_tokens: int = 96) -> str:
    """Generate a short response from the current model/adapters."""
    import torch

    model.eval()
    encoded = tokenizer(prompt, return_tensors="pt").to("cuda")
    with torch.no_grad():
        output = model.generate(
            **encoded,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(output[0], skip_special_tokens=True)


def count_trainable_parameters(model) -> dict[str, int | float]:
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    return {"trainable": trainable, "total": total, "ratio": trainable / total}
