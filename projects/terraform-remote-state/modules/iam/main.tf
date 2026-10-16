data "aws_iam_policy_document" "assume" {
  statement {
    sid     = "GitHubActionsOidc"
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [var.github_oidc_provider_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_repository}:ref:refs/heads/main"]
    }
  }
}

resource "aws_iam_role" "terraform_ci" {
  name               = "${var.name}-terraform-ci"
  assume_role_policy = data.aws_iam_policy_document.assume.json

  tags = var.tags
}

data "aws_iam_policy_document" "state_access" {
  statement {
    sid     = "StateBucketList"
    effect  = "Allow"
    actions = ["s3:ListBucket"]

    resources = [var.state_bucket_arn]
  }

  statement {
    sid    = "StateObjectReadWrite"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
    ]

    resources = ["${var.state_bucket_arn}/*"]
  }

  statement {
    sid    = "LockTableItem"
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem",
    ]

    resources = [var.lock_table_arn]
  }
}

resource "aws_iam_policy" "state_access" {
  name   = "${var.name}-terraform-state"
  policy = data.aws_iam_policy_document.state_access.json

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "state_access" {
  role       = aws_iam_role.terraform_ci.name
  policy_arn = aws_iam_policy.state_access.arn
}
