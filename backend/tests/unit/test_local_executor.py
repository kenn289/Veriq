from types import SimpleNamespace

from veriq.execution.local_executor import LocalTestExecutor


def test_local_executor_run_case_reports(monkeypatch):
    reported = []

    def fake_report(
        session, test_run_id, test_case_id, status, duration_seconds=0, **kwargs
    ):
        reported.append((test_case_id, status, kwargs))

    monkeypatch.setattr(
        "veriq.application.services.test_run_service.report_test_result", fake_report
    )

    exe = LocalTestExecutor()
    steps_fail = [SimpleNamespace(id="s1", value="__FAIL__")]
    ok = exe._run_test_case(
        session=None, test_run_id="r1", test_case_id="tc1", steps=steps_fail
    )
    assert ok is False
    assert reported and reported[-1][1] == "failed"

    # success path
    reported.clear()
    steps_ok = [SimpleNamespace(id="s1", value="ok")]
    ok2 = exe._run_test_case(
        session=None, test_run_id="r1", test_case_id="tc2", steps=steps_ok
    )
    assert ok2 is True
    assert reported and reported[-1][1] == "passed"
