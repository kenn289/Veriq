import os
from fastapi.testclient import TestClient

os.environ["VERIQ_TEST_GENERATION_PROVIDER"] = "model"
os.environ["VERIQ_LLM_MODEL_NAME"] = "distilgpt2"
os.environ["VERIQ_LLM_ADAPTER_DIR"] = "backend/llm/adapters/lora-distilgpt2"

from veriq.main import app

client = TestClient(app)
resp = client.post("/api/v1/ai/test-generation", json={"requirement": "Users can log in with email and password", "scenario_limit": 2})
print('status', resp.status_code)
print(resp.json())
