# CI onboarding

How a new service joins the same gates as `checkout-api`. This is a portfolio convention, not a copy of an employer pipeline.

## Add the service

1. Put the service under `projects/<name>` with a README that leads with the matching diagram.
2. Add a workflow that runs tests before image build. Copy the shape of `.github/workflows/ci-cd-container-platform.yml`.
3. Fail the job when tests fail. Do not use `continue-on-error` on the test step.
4. If the service has environment config, add a validator and a fixture that must fail (the sqlite-in-prod case is the example).
5. Build a multi-stage image that runs as a non-root user. Keep a single-stage Dockerfile only when you need a measured comparison.
6. Document the local command in the project README. A reviewer should not need cluster credentials to see the gate work.

## Definition of joined

- `pytest` (or the service's test command) is green in CI
- The bad-config fixture exits non-zero
- The README links the diagram and the workflow file

No manual deploy step is required to "finish" onboarding in this repo. Promotion past UAT stays an approval, described in `RELEASE-RUNBOOK.md`.
