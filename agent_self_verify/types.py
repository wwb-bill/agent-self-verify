from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Assertion:
    type: str
    value: str = ""
    severity: Severity = Severity.ERROR
    reason: str = ""


@dataclass
class Verdict:
    assertion: Assertion
    passed: bool
    detail: str = ""


@dataclass
class VerifyReport:
    task: str
    output: str
    verdicts: list[Verdict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        critical = [v for v in self.verdicts if v.assertion.severity == Severity.CRITICAL and not v.passed]
        errors = [v for v in self.verdicts if v.assertion.severity == Severity.ERROR and not v.passed]
        return len(critical) == 0 and len(errors) == 0

    def summary(self) -> str:
        total = len(self.verdicts)
        passed_c = sum(1 for v in self.verdicts if v.passed)
        failed = total - passed_c
        lines = [f"Verification: {'PASSED' if self.passed else 'FAILED'}", f"  {passed_c}/{total} checks passed"]
        if failed > 0:
            lines.append(f"  {failed} failures:")
            for v in self.verdicts:
                if not v.passed: lines.append(f"    [{v.assertion.severity.value}] {v.assertion.type}: {v.detail}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {"passed":self.passed,"total":len(self.verdicts),"passed_count":passed_c,"verdicts":[{"type":v.assertion.type,"passed":v.passed,"detail":v.detail,"severity":v.assertion.severity.value} for v in self.verdicts]}


@dataclass
class TaskSpec:
    task: str = ""
    assertions: list[Assertion] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
