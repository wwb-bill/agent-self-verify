import json, re
from agent_self_verify.types import Assertion, Verdict, VerifyReport, TaskSpec


def verify(output: str, assertions: list[Assertion], task: str = "") -> VerifyReport:
    return VerifyReport(task=task, output=output, verdicts=[_check(a, output) for a in assertions])


def verify_spec(output: str, spec: TaskSpec) -> VerifyReport:
    return verify(output, spec.assertions, spec.task)


def load_spec(path: str) -> TaskSpec:
    with open(path, encoding="utf-8") as f: data = json.load(f)
    return TaskSpec(task=data.get("task",""), assertions=[Assertion(type=a["type"],value=a.get("value",""),severity=a.get("severity","error"),reason=a.get("reason","")) for a in data.get("assertions",[])])


def _check(a: Assertion, output: str) -> Verdict:
    try:
        if a.type == "contains":
            ok = a.value in output; return Verdict(a, ok, "found" if ok else f"missing '{a.value}'")
        elif a.type == "not-contains":
            ok = a.value not in output; return Verdict(a, ok, "absent" if ok else f"found forbidden '{a.value}'")
        elif a.type == "min-length":
            n = int(a.value) if a.value else 1; ok = len(output) >= n; return Verdict(a, ok, f"length={len(output)} (min={n})")
        elif a.type == "max-length":
            n = int(a.value) if a.value else 10000; ok = len(output) <= n; return Verdict(a, ok, f"length={len(output)} (max={n})")
        elif a.type == "matches":
            ok = bool(re.search(a.value, output)); return Verdict(a, ok, "matches" if ok else f"no match for '{a.value}'")
        elif a.type == "is-json":
            try: json.loads(output); return Verdict(a, True, "valid JSON")
            except json.JSONDecodeError as e: return Verdict(a, False, f"invalid JSON: {e}")
        elif a.type == "has-keys":
            try:
                obj = json.loads(output)
                if isinstance(obj, dict):
                    missing = [k.strip() for k in a.value.split(",") if k.strip() not in obj]
                    return Verdict(a, len(missing)==0, f"missing keys: {missing}" if missing else "all keys present")
                return Verdict(a, False, "not a JSON object")
            except json.JSONDecodeError: return Verdict(a, False, "not valid JSON")
        else: return Verdict(a, False, f"unknown type: {a.type}")
    except Exception as e: return Verdict(a, False, f"error: {e}")
