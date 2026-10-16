# Portfolio Completion Checklist

Use this as the definition of done for the overall portfolio and for each project.

## Portfolio-level

- [ ] Resume ingested and stored privately for agent use (not published)
- [ ] Every technical resume bullet appears in the traceability matrix
- [ ] Each bullet has: mapped project(s), evidence type, verification status
- [ ] Project set is coherent (depth over proliferation)
- [ ] Landing documentation links resume themes → projects
- [ ] No secrets / proprietary employer artifacts in git history
- [ ] Public publication only after explicit approval
- [ ] Final report delivered (completed work, tests, deploys, URLs, limits, approvals)

## Per-project definition of done

### Problem & design

- [ ] Real problem statement and NFRs documented
- [ ] Architecture justified (why these tools; what was rejected)
- [ ] Editable architecture / deploy / failure diagrams present and consistent with code

### Implementation

- [ ] Sample app or workload exists and runs locally (or documented external blocker)
- [ ] IaC / config is reproducible
- [ ] CI/CD (or local equivalent) with at least one meaningful quality gate
- [ ] Success-path demo automated
- [ ] At least one deliberate failure/recovery demo where applicable
- [ ] Observability story documented (and implemented when in scope)

### Verification

- [ ] Automated tests executed; results recorded (pass/fail, commands)
- [ ] Lint/security checks run where tooling available
- [ ] Failures investigated and fixed or explicitly blocked
- [ ] Claims in README match verified behavior

### Security & ops

- [ ] IAM/secrets/least-privilege notes present
- [ ] Threat notes / limitations honest
- [ ] Runbook: deploy, verify, rollback, common incidents
- [ ] Cost estimate + teardown for any cloud resources

### Interview readiness

- [ ] Challenging Q&A with model answers grounded in *this* implementation
- [ ] Staff-level review completed; deficiencies fixed
- [ ] Resume bullets for this project marked with evidence links

## Current snapshot (2026-10-15)

Portfolio-level: **foundation scaffolding only** — blocked on resume.
Per-project: **none started**.
