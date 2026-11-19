---
name: independent-implementation-review
description: "Perform evidence-based, read-only implementation reviews against approved contracts, code, tests, and change scope. Use when asked to independently review, audit, or verify an implementation for contract compliance, regressions, coverage gaps, or unintended changes."
---

# Independent Implementation Review

## Objective

Perform an evidence-based, read-only review of an implementation or
change against its approved contract, the relevant code and tests,
and the stated change scope.

Default mode is static, read-only review. Conclusions follow from
evidence that was inspected or, when authorized, executed.

Use the same procedure for Python, Unity, Unreal, and other stacks.
Do not assume a language, test runner, editor, or play mode, and do
not embed product rules from any one project.

## Related instructions

Read the applicable project instructions and the approved contract.
If the project names a design document as the source of requirements,
read only the sections that apply. In this repository that document
is `docs/DESIGN.md`.

Do not invent requirements. Do not copy project policies or the
design-evaluation procedure from `game-system-review` into this
review. That Skill judges design quality. This Skill judges
implementation evidence against an approved contract.

## Activation and non-activation guidance

Activate when the task asks for an evidence-based review of an
existing implementation or change and the expected result is a
report. Typical asks include contract compliance, confirmed defects,
regressions, invalid-input handling, state invariants, test coverage,
or unintended edits.

Do not activate when the task is to:

- Judge whether a design is balanced, deep, or enjoyable.
- Implement, fix, refactor, or write tests.
- Explain code without a compliance judgment.
- Speculate about failures when no implementation can be identified.

If the request is ambiguous, ask whether it is an implementation
review or a design review, and which contract, scope, and baseline
apply. Do not start until the subject and the contract are
identifiable.

## Required context and inputs

Establish these before reviewing in depth. Ask for a required input
that is missing. Do not supply the gap yourself.

- **Subject:** the implementation or change being reviewed.
- **Contract:** the approved requirements, as a document path and
  sections or as contract text supplied for this review.
- **Scope:** in-scope behavior and stated non-goals.
- **Revision/baseline:** commit, branch, pull request, or working-tree
  comparison when a diff is part of the review. Record "not
  applicable" when there is no diff.
- **Locations:** implementation and test paths when known. Otherwise
  find them from the scope, selectively.
- **Execution authority:** whether tests may be run. The default is
  no.
- **Stack:** optional hint for where evidence lives. It does not add
  requirements.

If the subject or the contract cannot be established, stop and ask.

## Review procedure

1. Identify the implementation or change being reviewed.
2. Establish the approved requirements and review scope. Record
   ambiguities. Do not invent missing rules.
3. Identify the baseline, commit, or diff when applicable. Record
   the revision that was inspected. Read-only Git inspection is
   permitted.
4. Inspect the relevant implementation selectively. Prefer files
   tied to the scope. Read source and other text the stack exposes.
   Leave binary or editor-only assets unverified when their contents
   cannot be read.
5. Inspect related tests and map each in-scope requirement to
   implementation evidence and test evidence.
6. Check invalid inputs, edge cases, state invariants, regressions,
   and side effects where the contract or the change makes them
   relevant.
7. Examine the diff for unintended changes when a diff is available.
8. Apply the verification gates.
9. Classify findings using evidence. Keep finding type separate
   from severity.
10. Produce the structured review report.
11. Stop without modifying implementation files.

## Verification gates

Assign every gate one status: Pass, Fail, Partial, Not verified, or
Not applicable.

- **Pass:** the gate's condition holds for the inspected scope.
- **Fail:** the condition does not hold, and the report cites evidence.
- **Partial:** the condition holds for only part of the scope.
- **Not verified:** the evidence needed for the gate was not obtained.
- **Not applicable:** the gate does not apply to this review.

Do not treat intentionally unexecuted tests as an automatic defect
or failed review. A Fail or Partial needs a finding or a short
evidence note. A Pass on a static gate is not runtime proof.

### G1 — Contract clarity

Pass when the in-scope requirements can be checked and ambiguities
are recorded rather than filled in. Fail when there is no usable
contract. Partial when only part of the scope is clear. Not verified
when the contract was not read.

### G2 — Requirements mapped to implementation evidence

Pass when every in-scope requirement has a cited implementation
result: supports, contradicts, or not found in the files inspected.
Fail when a settled claim has no citation or the mapping was skipped.
Partial when only some requirements are mapped. Not verified when
the implementation was not inspected. Record a contradiction as a
confirmed defect and reflect it on G3. Mapping can pass while G3
fails.

### G3 — Static behavior and invariant assessment

Pass when the inspected code agrees with the contract on the invalid
inputs, edge cases, state invariants, and side effects that apply.
Fail when the inspected code contradicts any of those. Partial when
the results are mixed. Not verified when those behaviors could not
be judged from the files read.

### G4 — Out-of-scope changes

Pass when the inspected implementation stays inside the approved
scope. Treat behavior the project marks as future work as out of
scope unless this review includes it. Fail when out-of-scope
behavior is present. Partial when the extra behavior is limited or unclear.
Not verified when the scope or the implementation was not established.

### G5 — Diff containment, when applicable

Pass when an available diff stays within the stated change surface.
Fail when it contains unrelated edits. Partial when containment is
mixed. Not applicable when the review has no diff. Not verified when
a required diff could not be inspected.

### G6 — Test coverage assessment

Pass when the inspected tests address contract-critical behavior.
Fail when that coverage is missing from the inspected test surface.
Partial when coverage is incomplete. Not verified when tests were
not located or read. Not applicable when the task excludes a coverage
judgment. A Fail here is a coverage finding. Missing tests are not
proof of incorrect implementation.

### G7 — Test execution evidence, when authorized

Pass or Fail only from tests executed in this review, with the
command and result recorded. Partial when execution is incomplete
or the results are mixed. Not verified when tests were not executed,
including when execution was not authorized. Not applicable when
there are no tests to run. Not verified is not a defect and does not
fail the review. A failing result is a confirmed defect only when
the failure demonstrates a contract break.

### G8 — Tooling and verification limitations

Pass when the report's claims did not depend on an unavailable tool.
Partial or Not verified when a build, editor, play mode, unreadable
asset, or other missing channel blocks part of the review. Not
applicable when reading files was sufficient. Do not mark Fail only
because those tools were not used.

## Finding classification

Keep type separate from severity. Every confirmed defect must have
clear supporting evidence. Use relevant file paths and line numbers
when available. Do not report a hypothesis as a confirmed defect.

### Types

- **Confirmed defect:** the approved contract and the inspected
  evidence disagree, or an authorized test failure demonstrates that
  disagreement.
- **Missing test coverage:** a contract-relevant behavior has weak or
  no automated test in the inspected tests. Missing tests are not
  proof of incorrect implementation.
- **Potential risk:** a plausible failure mode suggested by the
  inspected code, not shown as a contract break.
- **Unverified assumption or limitation:** a claim that was not
  checked, including an ambiguous requirement, an unread path, or an
  unavailable tool.

### Severity criteria

Assign severity to actionable findings: confirmed defects, missing
test coverage, and potential risks. Do not assign a severity to an
unverified assumption or limitation.

- **Critical:** a confirmed defect that breaks a safety, security,
  data-integrity, or core contract invariant, or that makes the
  reviewed behavior unusable.
- **High:** a confirmed defect with serious impact short of Critical,
  or missing coverage or a risk on a contract-critical path.
- **Medium:** a confirmed defect with limited scope, or missing
  coverage or a risk on an important path.
- **Low:** a narrow confirmed mismatch, or a low-impact coverage gap
  or risk. On the evidence reviewed, primary contract behavior holds.

Severity does not change type. A High missing-coverage finding does
not mean the implementation is incorrect. Critical is only for a
confirmed defect.

## Read-only safety boundaries

Default mode is static, read-only review. Authorized test execution
changes the mode to static inspection plus executed tests. It still
does not authorize edits.

- Do not run tests unless explicitly authorized by the user or task.
- Do not create, modify, or delete implementation files.
- Do not edit tests, documents, or instructions during a review.
- Do not modify Git state.
- Read-only Git inspection is permitted when relevant.
- Do not install dependencies.
- Do not silently fix findings.
- Do not use MCP unless required for authorized verification.
- Do not claim runtime correctness solely from static inspection.
- Clearly distinguish inspected tests from executed tests.

Follow applicable project instructions as well. This Skill does not
replace them and does not authorize a fix, commit, or publication.

## Report

Use this template for every review. Cite evidence in the findings
and the coverage map. If a section has nothing to report, write
"None." Do not add defects to fill the template.

An overall review conclusion should not imply approval to merge or
publish.

```markdown
# Independent Implementation Review

## Review metadata
- Scope:
- Contract:
- Revision/baseline:
- Mode: static read-only | static plus authorized test execution

## Executive summary
<What was reviewed, whether any confirmed defects were found, and the mode.>

## Verification gates
| Gate | Status | Notes |
| --- | --- | --- |
| G1 Contract clarity | | |
| G2 Requirements mapped to implementation evidence | | |
| G3 Static behavior and invariant assessment | | |
| G4 Out-of-scope changes | | |
| G5 Diff containment | | |
| G6 Test coverage assessment | | |
| G7 Test execution evidence | | |
| G8 Tooling and verification limitations | | |

## Findings
### F1 — <short title>
- Type: Confirmed defect | Missing test coverage | Potential risk | Unverified assumption or limitation
- Severity: Critical | High | Medium | Low | Not assigned
- Evidence: <contract location, file path, and line numbers when available>
- Impact:

## Contract coverage map
| Requirement | Implementation evidence | Test evidence | Assessment |
| --- | --- | --- | --- |
| | | | Supported / Contradicted / Not found / Not verified |

## Change-scope observations
<Unrelated edits or out-of-scope behavior. "None observed." or "Not applicable" when there is no diff.>

## Tests inspected versus tests executed
- Inspected: <test files read, or none>
- Executed: <command and result, or "None — execution not authorized">

## Unverified items and limitations

## Overall review conclusion
<What the evidence supports. Do not approve a merge, release, or publish.>
```

Coverage-map assessment is independent of test evidence. Implementation
evidence can be Supported while test evidence shows a coverage gap.
Contradicted requires the same evidence bar as a confirmed defect.
Not found means a sufficient inspection did not find the behavior.
Not verified means the relevant files or tools were not available.
