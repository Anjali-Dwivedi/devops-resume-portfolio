output "cluster_name" {
  description = "Cluster name when enable_eks is true; null otherwise."
  value       = try(aws_eks_cluster.this[0].name, null)
}

output "cluster_endpoint" {
  description = "Cluster endpoint when enable_eks is true; null otherwise."
  value       = try(aws_eks_cluster.this[0].endpoint, null)
}

output "enabled" {
  description = "Whether the EKS stub is turned on."
  value       = var.enable_eks
}
