# Backend architecture

Operators and CI run Terraform. Terraform stores state in one S3 bucket and takes a lock in one DynamoDB table. Bootstrap creates those two resources with a local backend. Each consumer root selects its own state key. This demonstration does not use workspaces, a VPC, or a cluster.

```mermaid
flowchart LR
  classDef control fill:#0B1F3A,color:#ffffff,stroke:#0B1F3A
  classDef data fill:#0F6E6E,color:#ffffff,stroke:#0F6E6E

  operators["Operators and CI"]:::control
  terraform["Terraform 1.9.8"]:::control
  s3["S3 state bucket<br/>versioning, SSE-S3, public access block, TLS deny"]:::data
  dynamodb["DynamoDB lock table<br/>partition key LockID"]:::data

  operators --> terraform
  terraform --> s3
  terraform --> dynamodb
```

Example keys in the shared bucket:

- `env/dev/terraform.tfstate`
- `env/sit/terraform.tfstate`
- `env/uat/terraform.tfstate`
- `env/prod/terraform.tfstate`

The DynamoDB lock id for Terraform 1.9.8 is `{bucket}/{key}`, plus a digest item `{bucket}/{key}-md5`.
