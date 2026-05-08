# Contributing

Thanks for contributing to Mission-Critical Access Gatekeeper.

## Workflow

1. Open an issue describing scope, risk, and expected behavior.
2. Create a focused branch for one change set.
3. Implement changes with tests when behavior changes.
4. Update docs and notebook content when user-facing behavior changes.
5. Open a PR with a clear summary and test plan.

## Local Setup

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Fallback runtime:

```powershell
py -3.12 -m venv .venv-fallback
.\.venv-fallback\Scripts\Activate.ps1
python -m pip install -r requirements-fallback.txt
```

## Coding Guidelines

- Keep security behavior deterministic and explicit.
- Avoid silent bypasses for identity or emotion checks.
- Preserve clear deny reasons for operators and audit trails.
- Keep README, docs in `docs/`, and notebook demo aligned with runtime behavior.

## Test Expectations

- Verify both pass and deny paths for changed logic.
- Validate config defaults and advanced tuning behavior.
- If UI text changes, verify terminal and notebook wording remains consistent.

## Pull Request Checklist

- [ ] Scope is small and reviewable.
- [ ] Tests added or updated as needed.
- [ ] README/docs/notebook updated if behavior changed.
- [ ] No secrets, credentials, or private data included.
- [ ] Risk notes included for security-impacting changes.
