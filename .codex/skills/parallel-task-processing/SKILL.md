---
name: parallel-task-processing
description: Use when the user wants Codex to process multiple local tasks or GitHub issues in parallel using a management thread, per-task Codex threads, git worktrees, separate branches, review gates, and cleanup.
metadata:
  short-description: Run multiple tasks in parallel with worktrees
---

# Parallel Task Processing

Use this skill when multiple tasks should progress at the same time in this repository.

The canonical workflow is `docs/codex-multi-agent-workflow.md`. The canonical reusable role definitions are `.codex/agents/*.toml`.

## Policy

- The management thread keeps the task inventory, dependency order, branch/worktree mapping, review status, and final cleanup state.
- Each worker thread owns exactly one task or Issue.
- Create worktrees under the gitignored `tmp/worktrees/` directory inside this repository.
- Keep local-only data out of tracked files: `.env`, `*.local.*`, logs, model files, benchmark scratch output, `private/`, `private_data/`, `ollama/`, `lmstudio/`, and `work/` content.
- Run fresh review and intent review before completion, commit, push, or PR when the change has meaningful risk.

## Steps

1. Check `git status --short --branch` and `git worktree list --porcelain`.
2. Inventory tasks and classify them as close candidate, needs clarification, sequential, parallelizable, or blocked.
3. For each parallelizable task, create a branch such as `codex/task-short-topic` and a worktree under `tmp/worktrees/task-short-topic`.
4. Hand each worker thread the task, acceptance criteria, validation profile, allowed files, forbidden files, verification commands, worktree path, and branch name.
5. Require each worker to return changed files, verification results, evidence handoff, and residual risks.
6. Run fresh review and intent review for each finished task.
7. Commit, push, or prepare PRs only after the required reviews pass.
8. After merge or cancellation, remove the task worktree and local branch, then run `git worktree prune` when appropriate.
