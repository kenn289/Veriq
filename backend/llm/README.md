Getting started with fine-tuning a pre-trained LLM (recommended path)

Overview
- This folder provides a minimal scaffold to fine-tune an open pre-trained model
  using LoRA/QLoRA (PEFT + bitsandbytes) and to run inference locally.

Recommended flow
1. Prepare a dataset of instruction-response pairs in JSONL with `prompt` and `completion` fields.
2. Install dependencies (see `requirements.txt`).
3. Run `train_lora.py` to produce LoRA adapter weights.
4. Use the adapter with the inference client (`llm_client.py`) in `ModelTestGenerationProvider`.
 
 Quick example (local CPU / small model):
 
 1. Install dependencies into your venv:
 ```powershell
  .venv\Scripts\Activate.ps1
  pip install -r backend/llm/requirements.txt
 ```
 
 2. Train a tiny LoRA adapter (example using `distilgpt2` — this is just illustrative; QLoRA needs `bitsandbytes` and GPU):
 ```powershell
  python backend/llm/train_lora.py --model-name distilgpt2 --data backend/llm/sample_data.jsonl --output-dir backend/llm/adapters/lora-distilgpt2 --num-steps 10
 ```
 
 3. Use the adapter in the app by setting environment variables before starting the app:
 ```powershell
  $env:VERIQ_TEST_GENERATION_PROVIDER = "model"
  $env:VERIQ_LLM_MODEL_NAME = "distilgpt2"
  $env:VERIQ_LLM_ADAPTER_DIR = "backend/llm/adapters/lora-distilgpt2"
 ```
 
 Then the API will construct `HuggingFaceLLMClient` and use the adapter when available.

Notes
- Fine-tuning and inference require GPU for reasonable speed. For experimentation 7B–13B models
  on one 48GB GPU (A4000/RTX 6000/4090) are practical with QLoRA. For CPU-only, use small models
  or `llama.cpp` builds.
