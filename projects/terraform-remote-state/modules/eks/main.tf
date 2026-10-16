data "aws_iam_policy_document" "cluster_assume" {
  statement {
    sid     = "EksClusterAssume"
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["eks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "cluster" {
  count = var.enable_eks ? 1 : 0

  name               = "${var.cluster_name}-cluster"
  assume_role_policy = data.aws_iam_policy_document.cluster_assume.json

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "cluster" {
  count = var.enable_eks ? 1 : 0

  role       = aws_iam_role.cluster[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

data "aws_iam_policy_document" "node_assume" {
  statement {
    sid     = "EksNodeAssume"
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "node" {
  count = var.enable_eks ? 1 : 0

  name               = "${var.cluster_name}-node"
  assume_role_policy = data.aws_iam_policy_document.node_assume.json

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "node_worker" {
  count = var.enable_eks ? 1 : 0

  role       = aws_iam_role.node[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "node_cni" {
  count = var.enable_eks ? 1 : 0

  role       = aws_iam_role.node[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

resource "aws_iam_role_policy_attachment" "node_ecr" {
  count = var.enable_eks ? 1 : 0

  role       = aws_iam_role.node[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

data "aws_iam_policy_document" "pass_node" {
  count = var.enable_eks ? 1 : 0

  statement {
    sid       = "PassNodeRoleToEks"
    effect    = "Allow"
    actions   = ["iam:PassRole"]
    resources = [aws_iam_role.node[0].arn]

    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values   = ["eks.amazonaws.com"]
    }
  }
}

resource "aws_iam_policy" "pass_node" {
  count = var.enable_eks ? 1 : 0

  name   = "${var.cluster_name}-pass-node"
  policy = data.aws_iam_policy_document.pass_node[0].json

  tags = var.tags
}

resource "aws_eks_cluster" "this" {
  count = var.enable_eks ? 1 : 0

  name     = var.cluster_name
  version  = var.kubernetes_version
  role_arn = aws_iam_role.cluster[0].arn

  vpc_config {
    subnet_ids              = var.private_subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = false
  }

  tags = var.tags

  depends_on = [aws_iam_role_policy_attachment.cluster]
}
