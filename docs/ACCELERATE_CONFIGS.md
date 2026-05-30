Accelerate configs and example commands

Single 80GB GPU (A100/H100)
- Use `backend/llm/accelerate_configs/single_80gb.yaml`
- Example run:

```bash
accelerate launch --config_file backend/llm/accelerate_configs/single_80gb.yaml backend/llm/train_lora.py --model-name <MODEL> --data <DATA> --output-dir <OUT> --num-steps 1000
```

Multi-GPU with ZeRO stage 3 offload
- Use `backend/llm/accelerate_configs/multi_gpu_zero3.yaml`
- Example run (ensure `accelerate config` is set up across nodes):

```bash
accelerate launch --config_file backend/llm/accelerate_configs/multi_gpu_zero3.yaml backend/llm/train_lora.py --model-name <MODEL> --data <DATA> --output-dir <OUT> --num-steps 1000
```

Notes:
- Set `HF_TOKEN` in the environment for authenticated downloads.
- Adjust `per_device_train_batch_size`, `gradient_accumulation_steps`, and `fp16` based on GPU memory.
