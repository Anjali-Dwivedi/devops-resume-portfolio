output "terraform_ci_role_arn" {
  description = "Role GitHub Actions would assume with OIDC. Not created until apply is approved."
  value       = aws_iam_role.terraform_ci.arn
}

output "terraform_ci_role_name" {
  description = "CI role name."
  value       = aws_iam_role.terraform_ci.name
}
