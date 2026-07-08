# Security

rulebench exists because **rules files are untrusted code**: instructions an
agent executes with tool access. `rulebench vet` is the offline screen for
known-shape risks (pipe-to-shell, credential access, exfiltration shapes,
always-run directives, destructive commands, hidden text, instruction
overrides). A clean vet means "no known-shape red flags," **not** "safe" —
pattern matching cannot catch cleverly worded natural-language social
engineering. Read anything you let an agent follow.

Running rulebench itself: eval runs execute `claude` sessions in isolated
temp workspaces with the rules UNDER TEST loaded — treat a run of untrusted
rules with the same caution as running untrusted code (throwaway machine,
rotatable credentials).

## Reporting

Non-sensitive: open a GitHub issue. Sensitive (e.g., a vet bypass shape, a
workspace-isolation escape): use GitHub's private vulnerability reporting on
this repo. Vet bypasses are especially wanted — each one becomes a test in
`test_vet.py`.
