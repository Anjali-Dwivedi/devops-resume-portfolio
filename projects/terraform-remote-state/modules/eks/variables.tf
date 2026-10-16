variable "enable_eks" {
  description = "Create the EKS control plane and node role. Keep false unless a cloud plan is approved."
  type        = bool
  default     = false
}

variable "cluster_name" {
  description = "EKS cluster name used only when enable_eks is true."
  type        = string
  default     = "portfolio"
}

variable "kubernetes_version" {
  description = "Kubernetes version for the optional cluster stub."
  type        = string
  default     = "1.32"
}

variable "private_subnet_ids" {
  description = "Private subnet ids for the optional cluster."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Extra tags."
  type        = map(string)
  default     = {}
}
