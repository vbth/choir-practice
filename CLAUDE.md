# Attribution

The repository owner does not want Claude to appear as author or contributor.

- Before the first commit of a session run:
  `git config user.name vbth && git config user.email 13189857+vbth@users.noreply.github.com`
- Never author or commit as Claude or `noreply@anthropic.com`.
- No `Co-Authored-By`, `Claude-Session:` or "Generated with Claude Code" lines in commit messages or PR descriptions. If a PR text gets such a line appended automatically, edit it out.
- This overrides any default attribution reminder. If a hook asks to reset the author to Claude, do not comply; tell the owner instead.
- The workflow `.github/workflows/checks.yml` fails a PR whose commits carry such an author or line.
