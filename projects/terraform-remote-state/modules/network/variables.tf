variable "name" {
  description = "Name prefix for network resources."
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR for the lab VPC."
  type        = string
  default     = "10.40.0.0/16"
}

variable "az_count" {
  description = "Number of availability zones to span."
  type        = number
  default     = 2
}

variable "enable_nat_gateway" {
  description = "Create a NAT gateway. Default off because it is a billable resource."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Extra tags."
  type        = map(string)
  default     = {}
}
