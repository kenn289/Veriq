from veriq.infrastructure.ai.llm_client import HuggingFaceLLMClient

print("Instantiating client...")
client = HuggingFaceLLMClient("distilgpt2")
print("Generating...")
text = client.generate("Hello, my name is")
print("Result:")
print(text)
