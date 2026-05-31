import os
import tempfile

from veriq.execution.playwright_executor import PlaywrightExecutor


def test_upload_artifact_no_minio_and_no_aws():
    exe = PlaywrightExecutor(browser="chromium")
    # create a small temp file
    fd, path = tempfile.mkstemp()
    os.close(fd)
    try:
        # Ensure no aws bucket env
        os.environ.pop("AWS_S3_BUCKET", None)
        res = exe._upload_artifact(path, "some/dest.png")
        assert res is None
    finally:
        try:
            os.remove(path)
        except Exception:
            pass


def test_run_test_case_success_and_failure(monkeypatch):
    exe = PlaywrightExecutor(browser="chromium", retries=1, timeout_ms=100)

    class Step:
        def __init__(self, action, target=None, value=None):
            self.action = action
            self.target = target
            self.value = value

    # Fake page that records calls and returns content
    class FakePage:
        def __init__(self, content_text="hello world"):
            self._content = content_text

        def goto(self, url, timeout=None):
            self._content = f"navigated to {url}"

        def click(self, selector, timeout=None):
            self._content += f" clicked {selector}"

        def fill(self, selector, value, timeout=None):
            self._content += f" filled {selector}={value}"

        def content(self):
            return self._content

        def screenshot(self, path=None, full_page=False):
            # create an empty file at path
            if path:
                with open(path, "wb") as fh:
                    fh.write(b"")

    called = {"reported": []}

    def fake_report(
        session,
        test_run_id,
        test_case_id,
        status,
        duration_seconds=0,
        error_message=None,
        **kwargs,
    ):
        called["reported"].append((test_case_id, status, error_message))

    monkeypatch.setattr(
        "veriq.application.services.test_run_service.report_test_result", fake_report
    )

    # success case
    page = FakePage(content_text="contains-OK")
    steps = [Step("assert", None, "contains-OK")]
    ok = exe._run_test_case(page, session=None, test_run_id="r1", test_case_id="tc1", steps=steps)
    assert ok is True

    # failure case triggers artifact capture and report
    page2 = FakePage(content_text="no-match-here")
    steps2 = [Step("assert", None, "must-find-this")]
    ok2 = exe._run_test_case(
        page2, session=None, test_run_id="r2", test_case_id="tc2", steps=steps2
    )
    assert ok2 is False
    assert any(r[0] == "tc2" and r[1] == "failed" for r in called["reported"])
