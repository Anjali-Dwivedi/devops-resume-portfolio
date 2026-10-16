"""Static checks of the bootstrap, consumer, and IAM files.

These tests parse the project files. They do not call AWS and they are not
Terraform integration tests.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_COMMENT_BLOCK = re.compile(r"/\*.*?\*/", re.S)
_COMMENT_LINE = re.compile(r"(?m)#.*?$|//.*?$")

ROOT = Path(__file__).resolve().parents[1]
STATE_KEYS = [
    "env/dev/terraform.tfstate",
    "env/sit/terraform.tfstate",
    "env/uat/terraform.tfstate",
    "env/prod/terraform.tfstate",
]
CREDENTIAL_MARKERS = (
    "access_key",
    "secret_key",
    "aws_secret_access_key",
    "AWS_ACCESS_KEY",
    "AKIA",
)


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _code(text: str) -> str:
    """Drop comments so documentation of forbidden fields is not treated as a secret."""
    return _COMMENT_LINE.sub("", _COMMENT_BLOCK.sub("", text))


def _brace_body(text: str, marker: str) -> str:
    start = text.find(marker)
    assert start >= 0, marker
    brace = text.find("{", start)
    assert brace >= 0, marker
    depth = 0
    for index in range(brace, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[brace + 1 : index]
    raise AssertionError(f"unbalanced block for {marker}")


def _policy(name: str) -> dict:
    return json.loads(_text(f"iam/{name}.json"))


def _statements(name: str) -> list[dict]:
    body = _policy(name)
    assert body["Version"] == "2012-10-17"
    return body["Statement"]


def _actions(statement: dict) -> list[str]:
    action = statement["Action"]
    return [action] if isinstance(action, str) else list(action)


def _resources(statement: dict) -> list[str]:
    resource = statement["Resource"]
    return [resource] if isinstance(resource, str) else list(resource)


def test_version_pin_and_provider_are_explicit() -> None:
    bootstrap = _text("bootstrap/versions.tf")
    consumer = _text("consumer/versions.tf")
    assert 'required_version = "~> 1.9.8"' in bootstrap
    assert 'required_version = "~> 1.9.8"' in consumer
    assert 'version = "5.100.0"' in bootstrap
    assert "hashicorp/aws" in bootstrap
    assert "required_providers" not in consumer
    assert "use_lockfile" not in _code(bootstrap)
    assert "use_lockfile" not in _code(consumer)


def test_bootstrap_backend_is_local_and_consumer_backend_is_partial() -> None:
    versions = _text("bootstrap/versions.tf")
    local = _brace_body(versions, 'backend "local"')
    assert 'path = "terraform.tfstate"' in local
    assert 'backend "s3"' not in versions
    assert 'backend "s3"' not in _text("bootstrap/main.tf")

    backend = _brace_body(_text("consumer/backend.tf"), 'backend "s3"')
    assert backend.strip() == ""


def test_backend_example_has_placeholders_and_no_secrets() -> None:
    example = _text("backend.hcl.example")
    assert 'bucket         = "EXAMPLE_STATE_BUCKET"' in example
    assert 'key            = "env/dev/terraform.tfstate"' in example
    assert 'region         = "EXAMPLE_REGION"' in example
    assert 'dynamodb_table = "EXAMPLE_LOCK_TABLE"' in example
    assert "encrypt        = true" in example
    for key in STATE_KEYS:
        assert key in example
    code = _code(example)
    for forbidden in ("access_key", "secret_key", "kms_key_id", "use_lockfile", "AKIA"):
        assert forbidden not in code
    assert not re.search(r'(?m)^\s*token\s*=', code)


def test_example_state_keys_match_across_roots() -> None:
    for relative in ("bootstrap/outputs.tf", "consumer/main.tf"):
        text = _text(relative)
        for key in STATE_KEYS:
            assert f'"{key}"' in text


def test_bucket_controls_match_the_backend_contract() -> None:
    main = _text("bootstrap/main.tf")
    versioning = _brace_body(main, 'resource "aws_s3_bucket_versioning" "state"')
    assert 'status = "Enabled"' in versioning

    encryption = _brace_body(main, 'resource "aws_s3_bucket_server_side_encryption_configuration" "state"')
    assert 'sse_algorithm = "AES256"' in encryption
    assert "kms_master_key_id" not in encryption
    assert "kms_key_id" not in main

    block = _brace_body(main, 'resource "aws_s3_bucket_public_access_block" "state"')
    for setting in (
        "block_public_acls       = true",
        "block_public_policy     = true",
        "ignore_public_acls      = true",
        "restrict_public_buckets = true",
    ):
        assert setting in block

    policy = _brace_body(main, 'data "aws_iam_policy_document" "tls_only"')
    assert 'sid    = "DenyInsecureTransport"' in policy
    assert 'effect = "Deny"' in policy
    assert 'actions = ["s3:*"]' in policy
    assert 'variable = "aws:SecureTransport"' in policy
    assert 'values   = ["false"]' in policy


def test_lock_table_uses_the_terraform_1_9_schema() -> None:
    table = _brace_body(_text("bootstrap/main.tf"), 'resource "aws_dynamodb_table" "lock"')
    assert 'billing_mode = "PAY_PER_REQUEST"' in table
    assert 'hash_key     = "LockID"' in table
    assert 'name = "LockID"' in table
    assert 'type = "S"' in table
    assert "point_in_time_recovery" not in table
    assert "kms_key_arn" not in table


def test_apply_guard_is_a_hardcoded_false_precondition() -> None:
    for relative in ("bootstrap/main.tf", "consumer/main.tf"):
        text = _text(relative)
        body = _brace_body(text, 'resource "terraform_data" "apply_guard"')
        assert "apply_allowed = false" in text
        assert "condition     = local.apply_allowed" in body
        assert "allow_apply" not in text
        assert "not a security boundary" in body
    assert "allow_apply" not in _text("bootstrap/variables.tf")
    assert not (ROOT / "consumer/variables.tf").exists()
    readme = _text("README.md").replace("`", "")
    assert "terraform validate does not evaluate" in readme
    assert "A plan fails at that precondition" in readme
    assert "Backend initialization can run before it" in readme
    assert "Editing the source removes the guard" in readme


def test_consumer_declares_no_aws_resources() -> None:
    consumer = "\n".join(
        _text(name)
        for name in ("consumer/backend.tf", "consumer/main.tf", "consumer/versions.tf")
    )
    assert 'resource "aws_' not in consumer
    assert "provider \"aws\"" not in consumer


def test_operator_policy_is_scoped_to_state_keys_and_lock_items() -> None:
    statements = {item["Sid"]: item for item in _statements("backend-operator")}
    assert set(statements) == {
        "ListExampleStateKeys",
        "ReadWriteExampleStateObjects",
        "DescribeLockTable",
        "LockAndDigestItems",
    }

    listing = statements["ListExampleStateKeys"]
    assert _actions(listing) == ["s3:ListBucket"]
    assert _resources(listing) == ["arn:aws:s3:::EXAMPLE_STATE_BUCKET"]
    assert listing["Condition"]["StringEquals"]["s3:prefix"] == STATE_KEYS

    objects = statements["ReadWriteExampleStateObjects"]
    assert _actions(objects) == ["s3:GetObject", "s3:PutObject"]
    assert _resources(objects) == [f"arn:aws:s3:::EXAMPLE_STATE_BUCKET/{key}" for key in STATE_KEYS]
    assert "Condition" not in objects

    describe = statements["DescribeLockTable"]
    assert _actions(describe) == ["dynamodb:DescribeTable"]
    assert _resources(describe) == [
        "arn:aws:dynamodb:EXAMPLE_REGION:EXAMPLE_ACCOUNT_ID:table/EXAMPLE_LOCK_TABLE"
    ]
    assert "Condition" not in describe

    items = statements["LockAndDigestItems"]
    assert _actions(items) == ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:DeleteItem"]
    assert _resources(items) == _resources(describe)
    condition = items["Condition"]
    leading = condition["ForAllValues:StringEquals"]["dynamodb:LeadingKeys"]
    expected_leading = []
    for key in STATE_KEYS:
        expected_leading.append(f"EXAMPLE_STATE_BUCKET/{key}")
        expected_leading.append(f"EXAMPLE_STATE_BUCKET/{key}-md5")
    assert leading == expected_leading
    assert condition["Null"] == {"dynamodb:LeadingKeys": "false"}
    for action in (action for statement in statements.values() for action in _actions(statement)):
        assert action not in {"s3:ListBucketVersions", "s3:GetObjectVersion"}


def test_policies_reject_state_deletion_and_broad_allow() -> None:
    for name in ("backend-operator", "bootstrap", "state-recovery"):
        for statement in _statements(name):
            assert statement["Effect"] == "Allow"
            for action in _actions(statement):
                assert action != "*"
                assert not action.endswith(":*")
                assert "*" not in action
            for resource in _resources(statement):
                assert resource != "*"
                assert resource.startswith("arn:aws:")
            assert "s3:DeleteObject" not in _actions(statement)
            assert ".tflock" not in json.dumps(statement)


BUCKET_ARN = "arn:aws:s3:::EXAMPLE_STATE_BUCKET"
TABLE_ARN = "arn:aws:dynamodb:EXAMPLE_REGION:EXAMPLE_ACCOUNT_ID:table/EXAMPLE_LOCK_TABLE"
PROVIDER_REFRESH_READS = {
    "s3:GetBucketAcl",
    "s3:GetBucketCORS",
    "s3:GetBucketWebsite",
    "s3:GetAccelerateConfiguration",
    "s3:GetBucketRequestPayment",
    "s3:GetBucketLogging",
    "s3:GetLifecycleConfiguration",
    "s3:GetReplicationConfiguration",
    "s3:GetBucketObjectLockConfiguration",
    "s3:GetBucketTagging",
    "dynamodb:DescribeTimeToLive",
    "dynamodb:DescribeContinuousBackups",
    "dynamodb:ListTagsOfResource",
}


def test_bootstrap_policy_scopes_refresh_reads_and_destroy() -> None:
    statements = {item["Sid"]: item for item in _statements("bootstrap")}
    assert set(statements) == {
        "ManageStateBucket",
        "DestroyPublicAccessBlock",
        "ManageLockTable",
    }
    bucket = statements["ManageStateBucket"]
    assert _resources(bucket) == [BUCKET_ARN]
    assert PROVIDER_REFRESH_READS.intersection(_actions(bucket)) == {
        action for action in PROVIDER_REFRESH_READS if action.startswith("s3:")
    }
    assert "s3:PutBucketAcl" not in _actions(bucket)
    destroy = statements["DestroyPublicAccessBlock"]
    assert _actions(destroy) == ["s3:DeletePublicAccessBlock"]
    assert _resources(destroy) == [BUCKET_ARN]
    table = statements["ManageLockTable"]
    assert _resources(table) == [TABLE_ARN]
    assert "s3:GetBucketTagging" in _actions(bucket)
    assert {
        "dynamodb:DescribeTimeToLive",
        "dynamodb:DescribeContinuousBackups",
        "dynamodb:DescribeTable",
        "dynamodb:ListTagsOfResource",
    } <= set(_actions(table))
    for forbidden in (
        "dynamodb:UpdateTimeToLive",
        "dynamodb:UpdateContinuousBackups",
        "dynamodb:TagResource",
        "dynamodb:UntagResource",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:PutBucketTagging",
        "s3:DeleteBucketTagging",
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:DeleteItem",
    ):
        assert forbidden not in [action for statement in statements.values() for action in _actions(statement)]


def test_recovery_policy_matches_the_runbook_and_stays_narrow() -> None:
    statements = {item["Sid"]: item for item in _statements("state-recovery")}
    assert set(statements) == {"ListExampleStateVersions", "ReadExampleStateVersions"}
    listing = statements["ListExampleStateVersions"]
    assert _actions(listing) == ["s3:ListBucketVersions"]
    assert _resources(listing) == [BUCKET_ARN]
    assert listing["Condition"]["StringEquals"]["s3:prefix"] == STATE_KEYS
    reading = statements["ReadExampleStateVersions"]
    assert _actions(reading) == ["s3:GetObjectVersion"]
    assert _resources(reading) == [f"{BUCKET_ARN}/{key}" for key in STATE_KEYS]
    runbook = _text("docs/RUNBOOK.md")
    assert "iam/state-recovery.json" in runbook
    assert "s3:ListBucketVersions" in runbook
    assert "s3:GetObjectVersion" in runbook
    assert "iam/backend-operator.json" in runbook
    operator_actions = [
        action for statement in _statements("backend-operator") for action in _actions(statement)
    ]
    assert "s3:PutObject" in operator_actions
    assert "s3:GetObjectVersion" not in operator_actions


def test_provider_lock_file_pins_the_reviewed_provider() -> None:
    lock = _text("bootstrap/.terraform.lock.hcl")
    assert "registry.terraform.io/hashicorp/aws" in lock
    assert 'version     = "5.100.0"' in lock
    assert 'constraints = "5.100.0"' in lock


def test_tracked_examples_do_not_contain_credentials() -> None:
    roots = [ROOT / "bootstrap", ROOT / "consumer", ROOT / "iam", ROOT / "backend.hcl.example"]
    for raw in roots:
        files = [raw] if raw.is_file() else [path for path in raw.rglob("*") if path.is_file()]
        for file in files:
            if ".terraform" in file.parts:
                continue
            text = _code(file.read_text(encoding="utf-8"))
            for marker in CREDENTIAL_MARKERS:
                assert marker not in text, f"{file.name} contains {marker}"


def test_gitignore_covers_local_state_and_copied_backend_config() -> None:
    gitignore = (ROOT.parents[1] / ".gitignore").read_text(encoding="utf-8")
    assert "**/.terraform/" in gitignore
    assert "**/*.tfstate" in gitignore
    assert "backend.hcl" in gitignore
