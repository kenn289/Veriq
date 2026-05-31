from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    # Optional heavy deps; import lazily at runtime
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception:  # pragma: no cover - optional import
    AutoModelForCausalLM = None  # type: ignore
    AutoTokenizer = None  # type: ignore
    torch = None  # type: ignore


class LLMClientProtocol:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError()


@dataclass
class HuggingFaceLLMClient(LLMClientProtocol):
    """Lightweight adapter to run inference with a Hugging Face model.

    Example usage:
        client = HuggingFaceLLMClient("meta-llama/Llama-2-7b-chat-hf", adapter_dir="adapters/lora-7b")
        text = client.generate("Hello world")
    """

    model_name: str
    adapter_dir: str | None = None
    model: Any | None = None
    tokenizer: Any | None = None

    def _ensure_loaded(self) -> None:
        if self.model is not None and self.tokenizer is not None:
            return
        if AutoModelForCausalLM is None:
            raise RuntimeError(
                "transformers not installed; install backend/llm/requirements.txt"
            )

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=False)
        # Prefer 4-bit quantized load when available for larger models, but
        # fall back to a normal load if bitsandbytes / quantization isn't
        # available in the environment (common on developer machines).
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                load_in_4bit=True,
                device_map="auto",
            )
        except Exception:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name, device_map="auto"
            )

        # If a LoRA adapter dir exists, try to load it
        if self.adapter_dir:
            try:
                # PEFT adapters are usually stored with save_pretrained
                from peft import PeftModel

                self.model = PeftModel.from_pretrained(self.model, self.adapter_dir)
            except Exception:
                # fallback: ignore adapter load errors in dev
                pass

    def generate(self, prompt: str, **generation_options) -> str:
        """Generate text for `prompt` using optional generation settings.

        Supported generation_options (examples):
          - do_sample: bool
          - temperature: float
          - top_k: int
          - top_p: float
          - max_new_tokens: int
        """

        self._ensure_loaded()
        inputs = self.tokenizer(prompt, return_tensors="pt")
        if torch is not None:
            inputs = {
                k: v.to(next(self.model.parameters()).device) for k, v in inputs.items()
            }

        # Map common option names to the transformers generate() API
        gen_kwargs = dict(
            max_new_tokens=generation_options.get("max_new_tokens", 256),
            do_sample=generation_options.get("do_sample", False),
            temperature=generation_options.get("temperature", 1.0),
            top_k=generation_options.get("top_k", None),
            top_p=generation_options.get("top_p", None),
        )

        # Remove None values to avoid passing unsupported args
        gen_kwargs = {k: v for k, v in gen_kwargs.items() if v is not None}

        outputs = self.model.generate(**inputs, **gen_kwargs)
        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return text
