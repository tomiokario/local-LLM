---
name: parallel-task-processing
description: Use when the user wants Codex to process multiple local tasks or GitHub issues in parallel using a management thread, per-task Codex threads, git worktrees, separate branches, review gates, and cleanup.
metadata:
  short-description: Run multiple tasks in parallel with worktrees
---

# Parallel Task Processing

Use this skill when multiple tasks should progress at the same time in this repository.

The public canonical rules are `AGENTS.md` and `.codex/agents/*.toml`. Keep detailed local progress notes out of tracked files.

## Policy

- The management thread keeps the task inventory, dependency order, branch/worktree mapping, review status, and final cleanup state.
- Each worker thread owns exactly one task or Issue.
- Create worktrees under the gitignored `tmp/worktrees/` directory inside this repository.
- Keep content whose publication status is not confirmed out of tracked files, and do not enumerate concrete categories of non-public data in public-facing docs.
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
