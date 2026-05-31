"""Minimal QLoRA/LoRA training script example.

Usage (example):
  python train_lora.py --model-name meta-llama/Llama-2-7b-chat-hf --data data/train.jsonl --output-dir adapters/lora-7b --num-steps 100

This script is intentionally small; adapt hyperparameters and dataset handling for production.
"""

from __future__ import annotations

import argparse

from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    default_data_collator,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--model-name", required=True)
    p.add_argument("--data", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--num-steps", type=int, default=1000)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    ds = load_dataset("json", data_files=args.data)["train"]

    tokenizer = AutoTokenizer.from_pretrained(args.model_name, use_fast=False)

    def preprocess(ex):
        prompt = ex.get("prompt") or ""
        completion = ex.get("completion") or ""
        text = prompt + "\n" + completion
        toks = tokenizer(text, truncation=True, max_length=1024)
        toks["labels"] = toks["input_ids"].copy()
        return toks

    tokenized = ds.map(preprocess, batched=False)

    # Try to load in 4-bit (QLoRA) when bitsandbytes is available; otherwise
    # fall back to a standard model load. For small models (distilgpt2) this
    # fallback is fine for local experimentation on a single RTX card.
    try:
        model = AutoModelForCausalLM.from_pretrained(
            args.model_name,
            load_in_4bit=True,
            device_map="auto",
        )
        model = prepare_model_for_kbit_training(model)
    except Exception:
        model = AutoModelForCausalLM.from_pretrained(args.model_name, device_map="auto")
        try:
            model = prepare_model_for_kbit_training(model)
        except Exception:
            # If prepare for kbit fails on non-quantized model, continue without it.
            pass

    # Attempt to auto-detect target modules suitable for LoRA injection.
    known_targets = [
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "c_attn",
        "c_proj",
        "c_kv",
        "c_q",
    ]
    available = set()
    for name, _module in model.named_modules():
        for t in known_targets:
            if name.endswith(t) or t in name:
                available.add(t)

    target_modules = list(available) if available else ["q_proj", "v_proj"]

    peft_config = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=target_modules,
        lora_dropout=0.05,
        bias="none",
    )

    model = get_peft_model(model, peft_config)

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        num_train_epochs=1,
        max_steps=args.num_steps,
        fp16=True,
        logging_steps=50,
        save_total_limit=2,
        report_to=[],
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized,
        data_collator=default_data_collator,
    )

    trainer.train()
    model.save_pretrained(args.output_dir)
    # After saving the adapter, attempt to upload to MinIO (best-effort).
    try:
        from veriq.infrastructure.config.settings import get_settings

        settings = get_settings()
        from pathlib import Path

        def upload_adapter_dir_to_minio(adapter_path: str) -> None:
            try:
                from minio import Minio
            except Exception:
                print("MinIO client not installed; skipping adapter upload.")
                return

            endpoint = settings.minio_endpoint or ""
            # Strip scheme if present
            if endpoint.startswith("http://"):
                endpoint = endpoint[len("http://") :]
            if endpoint.startswith("https://"):
                endpoint = endpoint[len("https://") :]

            client = Minio(
                endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=False,
            )

            bucket = settings.minio_bucket or "veriq-artifacts"
            try:
                if not client.bucket_exists(bucket):
                    client.make_bucket(bucket)
            except Exception:
                # If bucket check/creation fails, continue without failing training
                print(f"Could not verify/create bucket '{bucket}'; skipping upload.")
                return

            adapter_dir = Path(adapter_path)
            if not adapter_dir.exists():
                print(f"Adapter dir {adapter_dir} does not exist; skipping upload.")
                return

            for p in adapter_dir.rglob("*"):
                if p.is_file():
                    # Object name: adapters/<adapter_name>/<relative_path>
                    rel = p.relative_to(adapter_dir.parent)
                    obj_name = f"{rel.as_posix()}"
                    try:
                        client.fput_object(bucket, obj_name, str(p))
                        print(f"Uploaded {p} -> {bucket}/{obj_name}")
                    except Exception as e:
                        print(f"Failed to upload {p}: {e}")

    except Exception:
        # Non-fatal: do not break training script if upload logic errors
        upload_adapter_dir_to_minio(args.output_dir)


if __name__ == "__main__":
    main()
