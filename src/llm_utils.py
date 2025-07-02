from __future__ import annotations

import os
from typing import List, Tuple

from llama_cpp import Llama
from llama_cpp_agent import LlamaCppAgent
from llama_cpp_agent.providers import LlamaCppPythonProvider
from llama_cpp_agent.chat_history import BasicChatHistory
from llama_cpp_agent.chat_history.messages import Roles
from llama_cpp_agent.messages_formatter import MessagesFormatter, PromptMarkers

__all__ = [
    "respond",
]

# ───────────────────────── Gemma‑3 prompt markers ──────────────────────────
_gemma_3_prompt_markers = {
    Roles.system:    PromptMarkers("", "\n"),
    Roles.user:      PromptMarkers("<start_of_turn>user\n",  "<end_of_turn>\n"),
    Roles.assistant: PromptMarkers("<start_of_turn>model\n", "<end_of_turn>\n"),
    Roles.tool:      PromptMarkers("", ""),
}
_gemma_3_formatter = MessagesFormatter(
    pre_prompt="",
    prompt_markers=_gemma_3_prompt_markers,
    include_sys_prompt_in_first_user_message=True,
    default_stop_sequences=["<end_of_turn>", "<start_of_turn>"],
    strip_prompt=False,
    bos_token="<bos>",
    eos_token="<eos>",
)


_llm: Llama | None = None
_llm_model_path: str | None = None


def _lazy_load_model(model_path: str) -> Llama:
    """Load (or return cached) GGUF model from *model_path*."""
    global _llm, _llm_model_path

    if _llm and _llm_model_path == model_path:
        return _llm

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")

    _llm = Llama(
        model_path=model_path,
        flash_attn=False,
        n_gpu_layers=0,
        n_batch=8,
        n_ctx=102_400,
        n_threads=8,
        n_threads_batch=8,
    )
    _llm_model_path = model_path
    return _llm


# ───────────────────────────────── respond() ────────────────────────────────

def respond(
    message: str,
    history: List[Tuple[str, str]],
    *,
    model: str | None = None,
    system_message: str = "You are a helpful assistant.",
    max_tokens: int = 102_400,
    temperature: float = 0.7,
    top_p: float = 0.95,
    top_k: int = 40,
    repeat_penalty: float = 1.1,
):

    model_path = (
        model
        or "gemma-3-1b-it-Q4_K_M.gguf"  # default
    )

    llm = _lazy_load_model(model_path)
    provider = LlamaCppPythonProvider(llm)
    agent = LlamaCppAgent(
        provider,
        system_prompt=system_message,
        custom_messages_formatter=_gemma_3_formatter,
        debug_output=False,
    )

    settings = provider.get_provider_default_settings()
    settings.temperature = temperature
    settings.top_k = top_k
    settings.top_p = top_p
    settings.max_tokens = max_tokens
    settings.repeat_penalty = repeat_penalty
    settings.stream = True

    chat_hist = BasicChatHistory()
    for user_msg, assistant_msg in history:
        chat_hist.add_message({"role": Roles.user, "content": user_msg})
        chat_hist.add_message({"role": Roles.assistant, "content": assistant_msg})

    stream = agent.get_chat_response(
        message,
        llm_sampling_settings=settings,
        chat_history=chat_hist,
        returns_streaming_generator=True,
        print_output=False,
    )

    full = ""
    try:
        for tok in stream:
            full += tok
            yield full
    except Exception as exc:
        yield f"[Error] {exc}\n"
