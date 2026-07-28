import json, sys, tempfile, os, pytest
from agent_self_verify.types import Assertion, Severity
from agent_self_verify.verifier import verify, verify_spec, load_spec


class TestVerifier:
    def test_contains(self):
        assert verify("hello", [Assertion(type="contains", value="hello")]).passed
    def test_contains_missing(self):
        assert not verify("hello", [Assertion(type="contains", value="world")]).passed
    def test_not_contains(self):
        assert verify("hello", [Assertion(type="not-contains", value="world")]).passed
    def test_not_contains_found(self):
        assert not verify("hello world", [Assertion(type="not-contains", value="world")]).passed
    def test_min_length(self):
        assert verify("abc", [Assertion(type="min-length", value="2")]).passed
        assert not verify("a", [Assertion(type="min-length", value="5")]).passed
    def test_max_length(self):
        assert verify("hi", [Assertion(type="max-length", value="10")]).passed
        assert not verify("too long!", [Assertion(type="max-length", value="3")]).passed
    def test_matches(self):
        assert verify("hello123", [Assertion(type="matches", value=r"\d+")]).passed
        assert not verify("hello", [Assertion(type="matches", value=r"\d+")]).passed
    def test_is_json(self):
        assert verify('{"a":1}', [Assertion(type="is-json")]).passed
        assert not verify("not json", [Assertion(type="is-json")]).passed
    def test_has_keys(self):
        assert verify('{"a":1,"b":2}', [Assertion(type="has-keys", value="a,b")]).passed
        assert not verify('{"a":1}', [Assertion(type="has-keys", value="a,c")]).passed
    def test_critical_blocks(self):
        assert not verify("bad", [Assertion(type="contains", value="missing", severity=Severity.CRITICAL)]).passed
    def test_warning_doesnt_block(self):
        assert verify("ok", [Assertion(type="contains", value="missing", severity=Severity.WARNING)]).passed
    def test_summary(self):
        r = verify("hello", [Assertion(type="contains", value="hello")])
        assert "PASSED" in r.summary()


class TestSpec:
    def test_load_and_verify(self):
        fd, path = tempfile.mkstemp(suffix=".json"); os.close(fd)
        with open(path, "w") as f: json.dump({"assertions":[{"type":"contains","value":"world"}]}, f)
        spec = load_spec(path); os.unlink(path)
        assert verify_spec("hello world", spec).passed


class TestCLI:
    def _r(self, *a):
        from agent_self_verify.cli import main
        import io; b = io.StringIO(); o = sys.stdout; sys.stdout = b
        try: main(list(a))
        except SystemExit: pass
        finally: sys.stdout = o
        return b.getvalue()
    def test_quick_pass(self):
        assert "PASSED" in self._r("quick", "hello", "--contains", "hello")
    def test_quick_fail(self):
        assert "FAILED" in self._r("quick", "hello", "--contains", "world")
    def test_check(self):
        fd, path = tempfile.mkstemp(suffix=".json"); os.close(fd)
        with open(path, "w") as f: json.dump({"assertions":[{"type":"contains","value":"test"}]}, f)
        o = self._r("check", path, "test output"); os.unlink(path)
        assert "PASSED" in o
