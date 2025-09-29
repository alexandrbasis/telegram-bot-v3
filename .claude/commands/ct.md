# Create Task Command

## PRIMARY OBJECTIVE
Create comprehensive task documents with mandatory business approval gate, technical decomposition, and Linear integration. NO time estimations for any work items. 
IMPORTANT: Think hard

## CRITICAL CONTROL GATES

### GATE 1: Business Requirements Approval (MANDATORY)
**Must complete BEFORE technical decomposition:**

```markdown
# Task: [Name]
**Status**: Business Review

## Primary Objective
[One-line user value statement after approval and Single clear statement of business need]

## Use Cases
1. [Specific scenario with acceptance criteria]
2. [Specific scenario with acceptance criteria]

## Constraints
- [Dependencies, timelines, resources]
```

**ACTION:** Present to user with: "Approve business requirements? [Yes/No]"
**BLOCKING:** Cannot proceed to test plan review without explicit approval

### GATE 2: Test Plan Review & Approval (MANDATORY)
**Must complete AFTER business approval and BEFORE technical decomposition:**

```markdown
Update **Status**: Awaiting Test Plan Approval

## Test Coverage Strategy
Target: 90%+ coverage across all implementation areas

## Proposed Test Categories
### Business Logic Tests (If needed)
- [ ] [Core functionality test covering requirement 1]
- [ ] [Validation test for acceptance criteria A]
- [ ] [Calculation/formatting test for scenario B]

### State Transition Tests (If needed)
- [ ] [Dialog flow test from state X to Y]
- [ ] [Command processing state changes]
- [ ] [Error recovery state transitions]

### Error Handling Tests (If needed)
- [ ] [API failure scenario test]
- [ ] [Invalid input handling test]
- [ ] [Edge case boundary test]

### Integration Tests (If needed)
- [ ] [External API interaction test]
- [ ] [Database operation test]
- [ ] [Third-party service integration test]

### User Interaction Tests (If needed)
- [ ] [Command processing test]
- [ ] [Response formatting test]
- [ ] [User journey end-to-end test]

## Test-to-Requirement Mapping
- Business Requirement 1 → Tests: [list test names]
- Business Requirement 2 → Tests: [list test names]
```

**ACTION:** Present test plan to user with: "Approve testing strategy requirements? [Yes/No]"
**BLOCKING:** Cannot proceed to technical decomposition without explicit test plan approval

### GATE 3: Technical Decomposition Approval (MANDATORY)
After business and test plan approval, add implementation details to the task document according to "Technical Task Example"

## TECHNICAL TASK EXAMPLE

```markdown
# Task: [Name]
**Status**: Technical Review

## Technical Requirements
- [ ] [Specific, measurable requirements]

## Implementation Steps & Change Log
- [ ] Step 1: [Action]
  - [ ] Sub-step 1.1: [Atomic action in specific directory]
    - **Directory**: `src/[specific-path]/`
    - **Files to create/modify**: `[exact-file-paths]`
    - **Accept**: [Measurable criteria]
    - **Tests**: [Test files to write first in tests/[path]/]
    - **Done**: [Completion proof]
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: [Action]
  - [ ] Sub-step 2.1: [Atomic action in specific directory]
    - **Directory**: `src/[specific-path]/`
    - **Files to create/modify**: `[exact-file-paths]`
    - **Accept**: [Measurable criteria]
    - **Tests**: [Test files to write first in tests/[path]/]
    - **Done**: [Completion proof]
    - **Changelog**: [Record changes made with file paths and line ranges]

### Constraints
- [Dependencies, timelines, resources]
```

### GATE 4: Technical Plan Review (MANDATORY)
**Must complete AFTER technical decomposition and BEFORE task splitting evaluation:**

**INITIAL REVIEW ACTION:** After technical requirements are created, automatically invoke Plan Reviewer agent to:
1. Review technical decomposition and implementation steps
2. Validate file paths, testing strategy, and acceptance criteria
3. Identify critical issues, clarifications, or improvements needed
4. Create comprehensive review document in task directory
5. Provide implementation readiness assessment

**ITERATIVE FEEDBACK LOOP:** When Plan Reviewer provides feedback requiring revisions:
1. **Address Feedback**: Make necessary updates to the task document based on feedback OR ask user to clarify if the clarification requires business decision.
2. **Re-submit for Review**: Automatically invoke Plan Reviewer agent again with:
   - Comprehensively updated task document according to Plan Reviewer's feedback
   - File Path to the task document
   - File Path to the previous plan review document for context
   - Clear summary of what was updated since last review with a reference to original plan review feedback and specific changes made to address each point
1. **Repeat Until Approved**: Continue this cycle until Plan Reviewer confirms approval.

**After approval, update Status to: Ready for Implementation**

**BLOCKING:** Cannot proceed to task splitting evaluation without Plan Reviewer final approval
**DECISION OUTCOMES:**
- ✅ **APPROVED**: Proceed to task splitting evaluation
- ❌ **NEEDS REVISIONS**: Address critical issues and re-submit for another review cycle
- 🔄 **NEEDS CLARIFICATIONS**: Make minor updates and re-submit for confirmation

**INTEGRATION:** Use `Task` tool with `plan-reviewer` agent type for both initial review and all subsequent feedback iterations

### GATE 5: Task Splitting Evaluation (MANDATORY)
**Must complete AFTER plan review and BEFORE Linear creation:**

**ACTION:** After Plan Reviewer approval, automatically invoke Task Splitter agent to:
1. Evaluate whether the task is too large for a single pull request
2. Analyze scope, complexity, and dependencies
3. Determine if task should be split into smaller sub-tasks
4. If splitting is needed, create sub-task directories and documents following the exact template structure
5. Provide clear reasoning for split/no-split decision

**BLOCKING:** Cannot proceed to Linear creation without Task Splitter evaluation
**DECISION OUTCOMES:**
- ✅ **NO SPLIT NEEDED**: Proceed to Linear creation with original task
- ✅ **SPLIT COMPLETED**: Proceed with created sub-tasks, each requiring separate Linear issues
- ❌ **NEEDS REVISION**: Task structure needs adjustment before proceeding

**INTEGRATION:** Use `Task` tool with `task-splitter` agent type after plan review is complete

### Issue Creation (After Task Splitting Evaluation)
```javascript
mcp__linear__create_issue({
  title: "[Task Name from document]",
  team: "AGB",
  description: "[Business context + technical requirements]",
  priority: 0-4  // 0=None, 1=Urgent, 2=High, 3=Normal, 4=Low
})

**Note**: If task was split into sub-tasks, create separate Linear issues for each sub-task following the same format.

```

## FINAL TASK DOCUMENT STRUCTURE

IMPORTANT: After all gates are completed, the final task document should follow this exact structure:

```markdown
# Task: [Name]
**Status**: Ready for Implementation

## Tracking & Progress
### Linear Issue
- **ID**: [Issue-ID]
- **URL**: [Issue URL]  

### PR Details
- **Branch**: [branch-name]
- **PR URL**: [Will be added during implementation]
- **Status**: [Draft/Review/Merged]

## Business Requirements

## Primary Objective
[One-line user value statement after approval and Single clear statement of business need]

## Use Cases
1. [Specific scenario with acceptance criteria]
2. [Specific scenario with acceptance criteria]

## Constraints
- [Dependencies, timelines, resources]

## Test Plan
**Status**: ✅ Approved | **Approved by**: [User] | **Date**: [Date]

## Test Coverage Strategy
Target: 90%+ coverage across all implementation areas

## Proposed Test Categories
### Business Logic Tests (If needed)
- [ ] [Core functionality test covering requirement 1]
- [ ] [Validation test for acceptance criteria A]
- [ ] [Calculation/formatting test for scenario B]

### State Transition Tests (If needed)
- [ ] [Dialog flow test from state X to Y]
- [ ] [Command processing state changes]
- [ ] [Error recovery state transitions]

### Error Handling Tests (If needed)
- [ ] [API failure scenario test]
- [ ] [Invalid input handling test]
- [ ] [Edge case boundary test]

### Integration Tests (If needed)
- [ ] [External API interaction test]
- [ ] [Database operation test]
- [ ] [Third-party service integration test]

### User Interaction Tests (If needed)
- [ ] [Command processing test]
- [ ] [Response formatting test]
- [ ] [User journey end-to-end test]

## Test-to-Requirement Mapping
- Business Requirement 1 → Tests: [list test names]
- Business Requirement 2 → Tests: [list test names]

## TECHNICAL TASK

### Technical Requirements
- [ ] [Specific, measurable technical requirements]
- [ ] [Architecture/design requirements]

### Implementation Steps & Change Log
- [ ] Step 1: [High-level action]
  - [ ] Sub-step 1.1: [Atomic action in specific directory]
    - **Directory**: `src/[specific-path]/`
    - **Files to create/modify**: `[exact-file-paths]`
    - **Accept**: [Measurable criteria]
    - **Tests**: [Test files to write first in tests/[path]/]
    - **Done**: [Completion proof]
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: [High-level action]
  - [ ] Sub-step 2.1: [Atomic action in specific directory]
    - **Directory**: `src/[specific-path]/`
    - **Files to create/modify**: `[exact-file-paths]`
    - **Accept**: [Measurable criteria]
    - **Tests**: [Test files to write first in tests/[path]/]
    - **Done**: [Completion proof]
    - **Changelog**: [Record changes made with file paths and line ranges]


### Task Splitting Evaluation
**Status**: ✅ Evaluated | **Evaluated by**: Task Splitter Agent | **Date**: [Date]
**Decision**: [No Split Needed / Split into X sub-tasks]
**Reasoning**: [Clear explanation of decision]

## Notes for Other Devs (Optional)
- [Implementation gotchas or important considerations]
- [Dependencies or prerequisites to be aware of]
- [Links to relevant documentation or discussions]

```

## DOCUMENT SPECIFICATIONS

### Directory Structure

tasks/
├── task-YYYY-MM-DD-[kebab-case]/
│   └── [Task Title].md           (Single document with both gates)
└── completed/                     (Archive after PR merge)
```

### Pre-Creation Discovery Requirements
1. Search existing documentation: `grep -r "relevant-terms" docs/`
2. Review codebase patterns: `find src/ -name "*.ts" -type f`
3. Document gaps found in task document under "Knowledge Gaps" section

## Tracking & Progress
### Linear Issue
- **ID**: [Created after technical approval]
- **URL**: [Link]
- **Status Flow**: Business Review → Ready for Implementation → In Progress → Ready for Review → In Review → Testing → Done

## Workflow Feedback Collection

### Step 6: Collect Workflow Feedback
```
After completing task creation, engage the workflow-feedback-collector agent to gather improvement insights about instruction clarity, process efficiency, and missing guidance that could benefit future developers.
```

**Agent Trigger**: Use workflow-feedback-collector agent
**Focus Areas**:
- Clarity of business requirements and approval process
- Effectiveness of technical decomposition instructions
- Adequacy of test planning guidelines
- Task splitting criteria and complexity assessment accuracy
- Any missing information that slowed down the task creation process
**Documentation**: All feedback automatically logged to docs/development/dev-wf-feedback.md
