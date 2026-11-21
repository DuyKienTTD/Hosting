# P0 Level 1 sandbox

This directory contains the public, secret-free deployment source for the
approved Level 1 n8n ↔ Hermes structural integration test.

## Safety properties

- Uses the two images already present on the verified KVM 2 host.
- Adds no published port and attaches only to the existing internal Docker
  network `ttd-ai-p0-sandbox`.
- Does not mount data or configuration from the primary n8n or Hermes services.
- The reasoner is deterministic mock logic. It cannot call a model and the
  internal Docker network has no Internet egress.
- Both services have CPU, memory and PID limits. The reasoner also has a
  read-only root filesystem and no Linux capabilities.
- Secrets are generated and stored only on the VPS in root-only env/runtime
  files. The placeholder `__P0_TOKEN__` must never be committed after replacement.

## Deployment outline

1. Verify primary health, the internal network and image digests.
2. Copy the deployment files to a root-only directory on the VPS.
3. Generate a dedicated sandbox bearer token and n8n encryption key.
4. Replace `__P0_TOKEN__` only in the private runtime workflow copy.
5. Initialize a new n8n data directory with `import:workflow`, then publish the
   imported workflow by ID; do not touch the primary n8n data volume.
6. Start the two auxiliary services with `docker compose up -d` and
   `pull_policy: never`.
7. Test missing/wrong auth, valid fake data, invalid schema, idempotent replay,
   timeout behavior, execution logs and post-change health.

## Rollback

Rollback stops the two auxiliary containers and leaves their root-only working
directory intact for inspection or recovery. It does not remove the existing
private bridge or change the primary containers. Destructive cleanup is a
separate explicitly approved action.

This mock test is not evidence of real model reasoning. Level 2 requires an
approved provider, model and monetary cap before any paid inference call.
