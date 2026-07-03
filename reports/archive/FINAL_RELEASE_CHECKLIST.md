# Final Release Checklist

- [x] Read-only audit completed.
- [x] Local tests passed in Phase 6 evidence: `141 passed, 1 skipped`.
- [x] Coverage threshold met in Phase 6 evidence: `95.03%`.
- [x] Ruff passed in Phase 6 evidence.
- [x] Compileall passed in Phase 6 evidence.
- [x] Wheel build passed in Phase 6 evidence.
- [x] Installed-wheel smoke passed in Phase 6 evidence.
- [x] README integrity passed in Phase 6 evidence.
- [x] Hero integrity passed in Phase 6 evidence.
- [x] Footer integrity passed in Phase 6 evidence.
- [x] Security review completed in Phase 6 evidence.
- [x] Clean worktree audit passed in Phase 6 evidence.
- [x] Final release commit existed before closure: `e50da461ca03b71c4ae669c857b2def680e45f70`.
- [x] Push verified for release commit: local `HEAD` matched `origin/main`.
- [x] Tag exists locally: `v0.3.0`.
- [x] Tag exists remotely: `v0.3.0`.
- [x] GitHub Release exists and is published for `v0.3.0`.
- [x] Post-release GitHub metadata verified.
- [ ] GitHub Actions success for the published release commit.

Final local verdict:

```text
PHASE 6 ACCEPTED
PROJECT RELEASE BLOCKED BY EXISTING TAG CONFLICT
```

Reason: after release publication, the GitHub Actions run for the published release commit failed at wheel build because `setuptools>=68` and `wheel` were not installed before `python -m build --wheel --no-isolation`. A limited CI dependency fix is prepared in the closure changes. The already published `v0.3.0` tag must not be force-moved.
