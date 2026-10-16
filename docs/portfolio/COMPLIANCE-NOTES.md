# Change-management notes

Documentation only. These are ordinary controls for a regulated change, written for the portfolio. They are not an employer's process and they are not a certification.

## Controls this repo actually implements

| Control | Where |
|---------|--------|
| Change is reviewed as a diff | Git history and pull requests |
| A bad config cannot pass the pipeline | `validate_config_file` rejects sqlite on `prod` |
| Plan is separate from apply | Terraform lab validates and refuses plan/apply via a failing precondition |
| Least privilege for automation | IAM module lists state and lock actions; Kubernetes deployer Role is namespace-scoped |
| Secrets stay out of git | `.gitignore` ignores `.env`, `*.pem`, credential files, and resume PDFs |
| Rollback is defined before the change | Canary controller and `RELEASE-RUNBOOK.md` |
| After the fact, the reason is written down | Incident lab RCA template |

## Controls this repo does not implement

- No ticketing integration
- No production access review
- No claim of SOC, SOX, or PCI compliance
- No cloud audit trail, because no cloud resources were created

Use the implemented rows in an interview. Do not imply the missing rows were done.
