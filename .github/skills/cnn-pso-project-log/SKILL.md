---
name: cnn-pso-project-log
description: "Logs progress, experiment results, bug fixes, implementation updates, session notes, and new RMSE/MAE/R2/MAPE/MdMRE/Pred25 values into project_log/PROJECT_LOG.md for the CNN+PSO software cost estimation project. Use whenever running an experiment, fixing a bug, getting new metrics, completing a task, starting a new session, or when the user says log this, document this, update the docs, add this to the project log, note this down, record these results, or update the documentation. Trigger aggressively for any CNN+PSO project update."
user-invocable: false
---

# CNN+PSO Project Log

Use this skill to keep the repository's running project documentation synchronized with actual work completed in the CNN+PSO software cost estimation project.

## Target File

- Update `project_log/PROJECT_LOG.md`.

## When to Use

- Any experiment run, rerun, or tuning cycle.
- Any new metric or comparison result.
- Any completed implementation step.
- Any bug fix, regression, or debugging conclusion.
- Any new saved artifact such as models, figures, histories, or hyperparameters.
- Any session start where goals, current state, or carry-over notes should be preserved.
- Any user instruction to log, document, note, record, or update documentation.

## Procedure

1. Read the relevant part of `project_log/PROJECT_LOG.md` before editing so you do not duplicate an existing entry.
2. If the update changes the overall project state, refresh the summary sections near the top of the file.
3. Append a dated entry under `## Chronological Log`; do not replace older history.
4. If the update includes metrics, record exact dataset names, model names, and exact values.
5. If the update includes a bug fix, record the symptom, root cause, affected files, and the validation that confirmed the fix.
6. If the update includes an implementation step, record what changed, where it changed, and what new artifacts were produced.
7. Keep the writing factual, compact, and specific to the repository state.

## Entry Checklist

- Date and short title.
- What changed.
- Files or artifacts affected.
- Metrics or results, when available.
- Validation or evidence.
- Next step or remaining risk, when relevant.

## What NOT to Do

- **Do not rewrite or restructure existing sections** — Only append new entries, never edit prior history.
- **Do not delete or modify old session entries** — Preserve chronological record exactly as written.
- **Do not change results tables unless new numbers were explicitly shared** — Keep existing metrics frozen unless a conversation explicitly provided new values.
- **Do not invent numbers or observations not present in the conversation** — Only log what the user reported or what the code/artifacts demonstrate.
- **Do not add filler text** — Keep entries factual, specific, and concise. Every sentence must report something that actually happened.

## Template

Use [the log entry template](./assets/log-entry-template.md) when adding a new project entry.
