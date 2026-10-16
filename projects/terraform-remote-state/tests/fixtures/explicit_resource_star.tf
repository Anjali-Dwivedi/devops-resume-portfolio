data "aws_iam_policy_document" "describe" {
  statement {
    sid       = "DescribeVpcs"
    effect    = "Allow"
    actions   = ["ec2:DescribeVpcs"]
    resources = ["*"]
  }
}
