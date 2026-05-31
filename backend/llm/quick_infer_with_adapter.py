from veriq.infrastructure.ai.llm_client import HuggingFaceLLMClient

print("Instantiating client with adapter...")
client = HuggingFaceLLMClient(
    "distilgpt2", adapter_dir="backend/llm/adapters/lora-distilgpt2"
)
print("Generating with adapter...")
print(
    client.generate(
        "Requirement: Users can log in with email and password. Generate a short test scenario.",
        max_new_tokens=80,
        do_sample=True,
        temperature=0.8,
        top_p=0.9,
    )
)
