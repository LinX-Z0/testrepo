
# AI Agent Instructions

## General Development
- Inspect existing files before modifying them.
- Prefer simple, maintainable solutions.
- Avoid unnecessary changes or dependencies.
- Follow existing project conventions.

## Planning
- For complex tasks, investigate and propose a plan first.
- Identify affected files and potential risks.
- Ask for approval before significant architecture changes.
- Proceed directly with small, well-defined tasks.

## Project Documentation

- docs/DESIGN.md contains the approved game design
  and gameplay requirements.
- Before implementing or modifying gameplay mechanics,
  read the relevant sections of docs/DESIGN.md.
- Treat approved design requirements as the source of truth.
- Do not implement features listed under Future Features
  unless explicitly requested.
- If a requirement is unclear or missing, identify the
  ambiguity rather than inventing gameplay rules.
- Report any conflicts between the design and existing code.


## Verification
- Run available tests after making changes.
- Review changes for unintended modifications.
- Do not claim tests passed unless they were executed.
- Explain what could not be verified.

## Safety
- Do not modify AGENTS.md or AI skill files
  unless explicitly instructed.
- Ask before deleting files or installing dependencies.
- Never expose credentials or secrets.
- Do not push or publish changes without approval.

## Completion
Summarize:
- Files changed
- Work completed
- Tests performed
- Remaining issues
