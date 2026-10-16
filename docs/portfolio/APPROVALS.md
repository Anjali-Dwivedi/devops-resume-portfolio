# Approval Log

Only significant gates are recorded here. Ordinary engineering decisions are executed without asking.

| Date | Decision | Status | Notes |
|------|----------|--------|-------|
| 2026-10-15 | Create foundation scaffolding (rules, trackers, docs) | Auto-approved | Low risk; no cloud, no public change of content beyond PR |
| 2026-10-16 | Validate-only Terraform, canary controller, incident lab | Auto-approved | No cloud create, no visibility change |
| — | Cloud resource provisioning | **Required before action** | Plan is in `projects/terraform-remote-state/docs/AWS-APPLY-PLAN.md`. Not approved. |
| — | Public visibility change | **Required before action** | Repository was already public. This work does not change visibility. |
| — | Destroy existing infrastructure | **Required before action** | Nothing was provisioned |
| — | Grant additional cloud privileges | **Required before action** | No cloud credentials used |

## Pending human actions

1. Approve or reject a future AWS apply. Default is do not apply. NAT and EKS stay off.
2. Approve any further publication change. The GitHub repository is already public.
