from veriq.infrastructure.ai.code_generation import generate_zip_from_plan
from veriq.api.v1.schemas.test_generation import (
    TestGenerationResponse,
    GeneratedScenarioResponse,
    GeneratedStepResponse,
)


def make_sample_plan():
    steps = [
        GeneratedStepResponse(order=1, action="navigate", target="/", description="Open home"),
        GeneratedStepResponse(order=2, action="click", target="#start", description="Start"),
    ]
    scenario = GeneratedScenarioResponse(
        name="Home Start",
        description="Start from home",
        priority=1,
        preconditions=[],
        steps=steps,
        assertions=[],
        tags=[],
    )
    return TestGenerationResponse(requirement="home", summary="", focus="", scenarios=[scenario])


def test_generate_zip_pytest_contains_tests(tmp_path):
    plan = make_sample_plan()
    blob = generate_zip_from_plan(plan, target="pytest-playwright")
    assert isinstance(blob, (bytes, bytearray))
    p = tmp_path / "py_out.zip"
    p.write_bytes(blob)
    import zipfile

    with zipfile.ZipFile(p, "r") as z:
        names = z.namelist()
        assert any(n.startswith("tests/") for n in names)
        assert any(n.endswith(".py") for n in names)
