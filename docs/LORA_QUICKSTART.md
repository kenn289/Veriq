LoRA / QLoRA Quickstart and Resource Estimates

This document summarises recommended commands and resource estimates for running LoRA/QLoRA fine-tuning.

Small local experiment (good for dev & CI smoke-tests)
- Model: `distilgpt2` (tiny)
- Steps: 10-100
- GPU: not required (CPU fine for tiny runs), GPU helps

Example command (quick small LoRA run):

```bash
python -m backend.llm.train_lora \
  --model-name distilgpt2 \
  --data backend/llm/sample_data.jsonl \
  --output-dir backend/llm/adapters/lora-distilgpt2 \
  --num-steps 10
```

7B model (QLoRA recommended)
- Typical setup: QLoRA with 4-bit quantization + LoRA adapters
- Minimum GPU memory: 24-32 GB (with sharding/grad-accumulation), prefer 48+ GB
- Disk: ~30-40 GB for model + checkpoints
- Training time: depends on dataset; small adapter runs (10-100 steps) are fast; full fine-tune may take hours

13B model (QLoRA)
- Preferred: multi-GPU or a single 80GB GPU for comfortable training
- Minimum GPU memory: 48-80 GB (or multiple GPUs with ZeRO/accelerate)
- Disk: 60+ GB

Practical tips
- Use `HF_TOKEN` environment variable for authenticated downloads and higher rate limits.
- Use `accelerate` for multi-GPU or ZeRO configurations.
- Store produced adapters in artifact storage (S3/MinIO) and load them with `PeftModel.from_pretrained(model, adapter_dir)`.

CI smoke-test suggestion
- Train a tiny adapter on `distilgpt2` for 2-5 steps and run `backend/llm/quick_infer_with_adapter.py` to ensure load and inference.

For detailed production commands I can produce a tuned `accelerate` config and exact step-by-step playbook for a chosen model.
