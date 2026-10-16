from pathlib import Path

from iam_policy import main, scan_paths

ROOT = Path(__file__).resolve().parents[1]
CONFIG = [ROOT / "bootstrap", ROOT / "consumer", ROOT / "iam"]
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_configuration_has_no_wildcard_allow() -> None:
    assert scan_paths(CONFIG) == []


def test_wildcard_allow_fixture_is_rejected() -> None:
    findings = scan_paths([FIXTURES / "wildcard_allow.tf"])
    assert findings
    assert any("wildcard action *" in finding.message for finding in findings)


def test_service_wildcard_allow_json_is_rejected() -> None:
    findings = scan_paths([FIXTURES / "service_wildcard_allow.json"])
    assert findings
    assert any("service wildcard s3:*" in finding.message for finding in findings)


def test_tls_deny_wildcard_is_not_treated_as_allow() -> None:
    assert scan_paths([FIXTURES / "tls_deny.json"]) == []


def test_explicit_describe_on_resource_star_is_allowed() -> None:
    findings = scan_paths([FIXTURES / "explicit_resource_star.tf"])
    assert findings == []


def test_cli_passes_configuration(capsys) -> None:
    code = main([str(path) for path in CONFIG])
    assert code == 0
    assert "IAM policy check passed" in capsys.readouterr().out
