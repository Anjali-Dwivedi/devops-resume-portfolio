from pathlib import Path

from iam_policy import main, scan_paths

ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "modules"
ENVS = ROOT / "envs"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_modules_and_envs_have_no_wildcard_allow() -> None:
    findings = scan_paths([MODULES, ENVS])
    assert findings == []


def test_wildcard_allow_fixture_is_rejected() -> None:
    findings = scan_paths([FIXTURES / "wildcard_allow.tf"])
    assert findings
    assert any("wildcard action *" in finding.message for finding in findings)


def test_explicit_describe_on_resource_star_is_allowed() -> None:
    findings = scan_paths([FIXTURES / "explicit_resource_star.tf"])
    assert findings == []


def test_remote_state_module_keeps_diagram_controls() -> None:
    collapsed = " ".join((MODULES / "remote_state" / "main.tf").read_text(encoding="utf-8").split())
    for required in (
        "aws_s3_bucket_versioning",
        "aws_s3_bucket_server_side_encryption_configuration",
        "aws_s3_bucket_public_access_block",
        "block_public_acls = true",
        "block_public_policy = true",
        "ignore_public_acls = true",
        "restrict_public_buckets = true",
        "DenyInsecureTransport",
        'hash_key = "LockID"',
        'sse_algorithm = "AES256"',
    ):
        assert required in collapsed, required


def test_lab_refuses_apply_at_plan_time() -> None:
    main = " ".join((ENVS / "lab" / "main.tf").read_text(encoding="utf-8").split())
    variables = " ".join((ENVS / "lab" / "variables.tf").read_text(encoding="utf-8").split())
    assert "terraform_data" in main
    assert "condition = var.allow_apply" in main
    assert "var.allow_apply == false" in variables
    assert "enable_nat_gateway = false" in main
    assert "enable_eks = false" in main


def test_cli_passes_modules(capsys) -> None:
    code = main([str(MODULES), str(ENVS)])
    assert code == 0
    assert "IAM policy check passed" in capsys.readouterr().out
