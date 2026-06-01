from veriq.infrastructure.ai.code_generation import generate_zip_from_plan
from veriq.api.v1.schemas.test_generation import (
    TestGenerationResponse,
    GeneratedScenarioResponse,
    GeneratedStepResponse,
)


def make_sample_plan():
    steps = [
        GeneratedStepResponse(order=1, action="navigate", target="/login", description="Open login"),
        GeneratedStepResponse(order=2, action="type", target="#email", value="user@example.com", description="Fill email"),
        GeneratedStepResponse(order=3, action="click", target="#submit", description="Submit"),
    ]
    scenario = GeneratedScenarioResponse(
        name="Login Flow",
        description="Test login",
        priority=1,
        preconditions=["app deployed"],
        steps=steps,
        assertions=["Welcome text appears"],
        tags=["smoke"],
    )
    return TestGenerationResponse(requirement="login", summary="", focus="", scenarios=[scenario])


def test_generate_zip_contains_files(tmp_path):
    plan = make_sample_plan()
    blob = generate_zip_from_plan(plan, target="playwright-ts")
    assert isinstance(blob, (bytes, bytearray))
    # write to disk and inspect zip
    p = tmp_path / "out.zip"
    p.write_bytes(blob)
    import zipfile

    with zipfile.ZipFile(p, "r") as z:
        names = z.namelist()
        assert "package.json" in names
        assert "tests/login_flow.spec.ts" in names or any(n.startswith("tests/") for n in names)
