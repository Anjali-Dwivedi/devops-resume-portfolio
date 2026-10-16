# Interview Q&A — progressive delivery

## Why two Services?

The architecture sequence shifts **ingress weight** (10, then 50, then 100), not a replica ratio. kube-proxy on a single Service does not apply those weights. Ingress-nginx does, with a primary Ingress and a canary Ingress (`nginx.ingress.kubernetes.io/canary-weight`). Each Ingress targets its own ClusterIP. Diagram `04-k8s-progressive-delivery` shows that split.

## Why not start at 50%?

The sequence starts the candidate at a small weight so a bad build affects a slice of traffic. The controller then has an explicit 50% step before 100%. Skipping straight to 100% would ignore the gate the diagram draws.

## What happens at exactly 5%?

Rollback. The comparison is `error_rate >= 0.05`, and the Prometheus rule uses the same `>=`. A strict `>` would promote a canary the alert already considers bad, or the reverse. `incident/flow.py` in the observability lab loads this module so the two cannot drift quietly: a test asserts the constants match.

## Why hold when there are few samples?

Three failures out of three requests is 100%, and it is also noise. The controller waits for 20 samples before promote or rollback. That is a demo minimum, not an SLO from production traffic.

## How does this relate to Route53 and ALB?

`docs/ingress-alb.example.yaml` is the production edge: internet-facing ALB, `/readyz` health check, hostname annotation. Kind does not create that load balancer. Weighted target groups would be the ALB actuator; the decision function stays `controller/canary.py`. No AWS load balancer was created.

## What is intentionally missing?

No live kind cluster in the verified run (Docker was absent). No Argo Rollouts or Flagger: a small controller keeps the promote/rollback rule visible in one file, which is the point of the interview demo. A service mesh would be justified if the weight had to be per-route instead of per-host.
