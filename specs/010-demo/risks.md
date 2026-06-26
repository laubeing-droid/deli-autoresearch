# SPEC-010 Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Demo too simple to catch edge cases | Low | Test all lifecycle transitions explicitly |
| Local CI simulation differs from GitHub Actions | Medium | Validate scripts with same inputs as CI |
| Sorry gate test creates temporary .lean files | Low | Use dedicated test directory, clean up after |
