"""Reject wildcard Allow IAM in this lab's Terraform.

Deny statements may use a service wildcard (the TLS-only bucket policy uses
``s3:*`` with ``Effect = Deny``). Allow statements must name actions.
``iam:PassRole`` is allowed only with a condition block.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

COMMENT_BLOCK = re.compile(r"/\*.*?\*/", re.S)
COMMENT_LINE = re.compile(r"(?m)//.*?$|#.*?$")
QUOTED = re.compile(r'"(?:\\.|[^"\\])*"')
ACTION_HINT = re.compile(r'(?i)\b(?:"action"|"actions"|action|actions)\b')


@dataclass(frozen=True)
class Finding:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


def strip_comments(text: str) -> str:
    text = COMMENT_BLOCK.sub("", text)
    return COMMENT_LINE.sub("", text)


def _brace_bodies(text: str) -> list[str]:
    bodies: list[str] = []
    for index, char in enumerate(text):
        if char != "{":
            continue
        depth = 0
        for cursor in range(index, len(text)):
            if text[cursor] == "{":
                depth += 1
            elif text[cursor] == "}":
                depth -= 1
                if depth == 0:
                    bodies.append(text[index + 1 : cursor])
                    break
    return bodies


def _quoted(value: str) -> list[str]:
    return [token[1:-1] for token in QUOTED.findall(value)]


def _assigned(block: str, names: tuple[str, ...]) -> list[str]:
    found: list[str] = []
    name_re = "|".join(names)
    pattern = re.compile(
        rf'(?is)(?:"(?:{name_re})"|{name_re})\s*[:=]\s*(\[[^\]]*\]|"(?:\\.|[^"\\])*")'
    )
    for match in pattern.finditer(block):
        found.extend(_quoted(match.group(1)))
    return found


def _is_deny(block: str) -> bool:
    # HCL uses effect = "Deny". JSON uses "Effect": "Deny".
    return re.search(r'(?i)(?:"effect"|effect)\s*[:=]\s*"deny"', block) is not None


def forbidden_action(action: str) -> str | None:
    if action == "*":
        return "wildcard action *"
    if re.fullmatch(r"[A-Za-z0-9-]+:\*", action):
        return f"service wildcard {action}"
    if "*" in action and not re.fullmatch(
        r"[A-Za-z0-9-]+:(?:Describe|List|Get)[A-Za-z0-9]*\*", action
    ):
        return f"unsupported action wildcard {action}"
    return None


def _has_action(block: str) -> bool:
    return ACTION_HINT.search(block) is not None


def scan_text(path: str, text: str) -> list[Finding]:
    bodies = [body for body in _brace_bodies(strip_comments(text)) if _has_action(body)]
    innermost = [
        body
        for body in bodies
        if not any(other != body and other in body for other in bodies)
    ]
    findings: list[Finding] = []
    for block in innermost:
        if _is_deny(block):
            continue
        actions = _assigned(block, ("action", "actions"))
        resources = _assigned(block, ("resource", "resources"))
        principals = _assigned(block, ("identifiers",))
        for action in actions:
            reason = forbidden_action(action)
            if reason:
                findings.append(Finding(path, f"Allow statement uses {reason}"))
            if action == "iam:PassRole" and not re.search(r"(?i)\bcondition\b", block):
                findings.append(Finding(path, "Allow iam:PassRole without a condition"))
        if any(item == "*" for item in resources) and any(
            forbidden_action(action) for action in actions
        ):
            findings.append(
                Finding(path, "Allow statement combines a wildcard action with Resource *")
            )
        if actions and any(item == "*" for item in principals):
            findings.append(Finding(path, "Allow statement uses principal *"))
    return findings


def _candidate_files(raw: Path) -> list[Path]:
    if raw.is_file():
        return [raw]
    files: list[Path] = []
    for pattern in ("*.tf", "*.json"):
        files.extend(raw.rglob(pattern))
    selected: list[Path] = []
    for file in files:
        if not file.is_file():
            continue
        if ".terraform" in file.parts:
            continue
        selected.append(file)
    return sorted(selected)


def scan_paths(paths: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for raw in paths:
        for file in _candidate_files(raw):
            findings.extend(scan_text(str(file), file.read_text(encoding="utf-8")))
    return findings


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    roots = [Path(arg) for arg in args] or [Path("bootstrap"), Path("consumer"), Path("iam")]
    findings = scan_paths(roots)
    for finding in findings:
        print(finding)
    if findings:
        print(f"{len(findings)} IAM policy finding(s)")
        return 1
    print(f"IAM policy check passed for {', '.join(str(root) for root in roots)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
