# Assumptions & Environment Inventory

Recorded: 2026-10-15

## Workspace

- Git remote: `https://github.com/Anjali-Dwivedi/Devops-` (currently **public**, empty of portfolio content; placeholder `saturn*` / planet dirs present)
- Default branch: `main`
- Working branch: `cursor/portfolio-foundation-0812`
- Project store: `/cursor/stores/bc-f71a30b9-5eb0-4a05-934d-42caf4af82f0` (empty at start)

## Resume

- **Not found** under `/workspace`, attachments, or project store
- Assumption: human will provide resume as PDF/DOCX/MD/TXT (or paste text)
- Until then: no project invention from guessed experience

## Tooling available in this environment

| Tool | Status | Notes |
|------|--------|-------|
| Git / gh | Available | `gh` authenticated as integration; repo view works; `gh api user` 403 |
| Node.js | Available | v22.x |
| Python 3 | Available | 3.12; ansible present |
| Go / Rust | Available | Present on PATH |
| Docker | **Not found** | Install before container demos |
| Terraform | **Not found** | Install before IaC project |
| kubectl / helm / kind | **Not found** | Install before K8s demos |
| AWS / GCP / Azure CLIs | **Not found** | Needed only after cloud approval |
| Chrome / VNC | Available | Useful for GUI demos if needed |

## Working assumptions (low risk)

1. This repository will become the **portfolio landing / index** repo unless resume mapping shows a better split.
2. Placeholder `saturn*` / `jupiter` / `nebula` / `pluto` files are unrelated test clutter; will be removed or quarantined when building the landing page (low risk cleanup).
3. Prefer open-source, locally reproducible demos first; cloud only when it adds unique interview value and is approved.
4. Individual extra repositories only when a theme needs independent CI history or clarity; default to monorepo `/projects/<name>` under the landing repo for speed and coherence during development.

## Update 2026-10-16

- This working copy is `Anjali-Dwivedi/devops-resume-portfolio`. Changes land through a branch into `main`.
- Terraform 1.16.6, AWS provider 6.69.1, Helm 4.3.1, kubeconform 0.8.0, and kubectl 1.37.1 were installed for local checks.
- Docker, kind, and the AWS CLI are still absent. Demos that need them are written and were not executed.
- A `terraform plan` was run only to observe the apply guard. It failed. No state file and no AWS resource were created.

## Explicit non-assumptions

- Do not assume AWS vs GCP vs Azure preference until resume (or human) indicates cloud focus
- Do not assume Kubernetes depth until resume bullets support it
- Do not assume permission to spend cloud budget
