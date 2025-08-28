# Create Task Command

## PRIMARY OBJECTIVE
Create comprehensive task documents with mandatory business approval gate, technical decomposition, and Linear integration. NO time estimations for any work items. IMPORTANT: Think very hard

## CRITICAL CONTROL GATES

### GATE 1: Business Requirements Approval (MANDATORY)
**Must complete BEFORE technical decomposition:**

```markdown
# Business Requirements: [Task Name]
**Status**: Awaiting Business Approval | **Created**: [Date]

## Primary Objective
[Single clear statement of business need]

## Use Cases
1. [Specific scenario with acceptance criteria]
2. [Specific scenario with acceptance criteria]

## Success Metrics
- [ ] [Measurable business outcome]
- [ ] [User satisfaction indicator]

## Constraints
- [Dependencies, timelines, resources]
```

**ACTION:** Present to user with: "Approve business requirements? [Yes/No]"
**BLOCKING:** Cannot proceed to test plan review without explicit approval

### GATE 2: Test Plan Review & Approval (MANDATORY)
**Must complete AFTER business approval and BEFORE technical decomposition:**

```markdown
# Test Plan: [Task Name]
**Status**: Awaiting Test Plan Approval | **Created**: [Date]

## Test Coverage Strategy
Target: 90%+ coverage across all implementation areas

## Proposed Test Categories
### Business Logic Tests
- [ ] [Core functionality test covering requirement 1]
- [ ] [Validation test for acceptance criteria A]
- [ ] [Calculation/formatting test for scenario B]

### State Transition Tests  
- [ ] [Dialog flow test from state X to Y]
- [ ] [Command processing state changes]
- [ ] [Error recovery state transitions]

### Error Handling Tests
- [ ] [API failure scenario test]
- [ ] [Invalid input handling test]
- [ ] [Edge case boundary test]

### Integration Tests
- [ ] [External API interaction test]
- [ ] [Database operation test]
- [ ] [Third-party service integration test]

### User Interaction Tests
- [ ] [Command processing test]
- [ ] [Response formatting test]
- [ ] [User journey end-to-end test]

## Test-to-Requirement Mapping
- Business Requirement 1 → Tests: [list test names]
- Business Requirement 2 → Tests: [list test names]
```

**ACTION:** Present test plan to user with: "Do these tests adequately cover the business requirements before technical implementation begins? Type 'approve' to proceed or provide feedback."
**BLOCKING:** Cannot proceed to technical decomposition without explicit test plan approval

### GATE 3: Technical Decomposition Approval
After business and test plan approval, create technical task document and get approval before Plan Review.

### GATE 4: Technical Plan Review (MANDATORY)
**Must complete AFTER technical decomposition and BEFORE task splitting evaluation:**

**INITIAL REVIEW ACTION:** After technical requirements are created, automatically invoke Plan Reviewer agent to:
1. Review technical decomposition and implementation steps
2. Validate file paths, testing strategy, and acceptance criteria
3. Identify critical issues, clarifications, or improvements needed
4. Create comprehensive review document in task directory
5. Provide implementation readiness assessment

**ITERATIVE FEEDBACK LOOP:** When Plan Reviewer provides feedback requiring revisions:
1. **Address Feedback**: Make necessary updates to the task document based on feedback
2. **Re-submit for Review**: Automatically invoke Plan Reviewer agent again with:
   - Updated task document (full content with changes highlighted)
   - Path to the task document
   - Path to the previous plan review document for context
   - Clear summary of what was updated since last review
3. **Context Provision**: Provide comprehensive information to plan reviewer including:
   - Complete updated task content
   - Reference to original plan review feedback
   - Specific changes made to address each point
4. **Repeat Until Approved**: Continue this cycle until Plan Reviewer confirms approval

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

## DOCUMENT SPECIFICATIONS

### Directory Structure
```
tasks/
├── task-YYYY-MM-DD-[kebab-case]/
│   └── [Task Title].md           (Single document with both gates)
└── completed/                     (Archive after PR merge)
```

### Pre-Creation Discovery Requirements
1. Search existing documentation: `grep -r "relevant-terms" docs/`
2. Review codebase patterns: `find src/ -name "*.ts" -type f`
3. Document gaps found in task document under "Knowledge Gaps" section

## TECHNICAL TASK TEMPLATE

```markdown
# Task: [Name]
**Created**: [Date] | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
[Single clear statement of business need]

### Use Cases
1. [Specific scenario with acceptance criteria]
2. [Specific scenario with acceptance criteria]

### Success Metrics
- [ ] [Measurable business outcome]
- [ ] [User satisfaction indicator]

### Constraints
- [Dependencies, timelines, resources]

**APPROVAL GATE:** Present business section to user with: "Approve business requirements? [Yes/No]"
**After approval, update Status to: Ready for Implementation**

## Tracking & Progress
### Linear Issue
- **ID**: [Created after technical approval]
- **URL**: [Link]
- **Status Flow**: Business Review → Ready for Implementation → In Progress → In Review → Testing → Done
  - **Business Review**: Business requirements under review
  - **Ready for Implementation**: Business approved, technical plan reviewed by Plan Reviewer agent, Linear issue created, ready for development
  - **In Progress**: Developer actively working on implementation
  - **In Review**: PR created and under code review
  - **Testing**: User acceptance testing in progress
  - **Done**: PR merged to main and Linear issue closed

### PR Details
- **Branch**: [Name]
- **PR URL**: [Link]
- **Status**: [Draft/Review/Merged]

## Business Context
[One-line user value statement after approval]

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

## Testing Strategy
- [ ] Unit tests: [Components in tests/[specific-path]/]
- [ ] Integration tests: [Workflows in tests/integration/]

## Success Criteria
- [ ] All acceptance criteria met
- [ ] Tests pass (100% required)
- [ ] No regressions
- [ ] Code review approved
```

## LINEAR INTEGRATION PROTOCOL

### Issue Creation (After Task Splitting Evaluation)
```javascript
mcp__linear__create_issue({
  title: "[Task Name from document]",
  team: "ABasis",
  description: "[Business context + technical requirements]",
  priority: 0-4  // 0=None, 1=Urgent, 2=High, 3=Normal, 4=Low
})
```

**Note**: If task was split into sub-tasks, create separate Linear issues for each sub-task following the same format.

### Status Progression
1. **Ready for Implementation**: Business approved, technical plan iteratively reviewed and approved by Plan Reviewer agent, task automatically evaluated for splitting by Task Splitter agent, Linear issue(s) created, awaiting development
2. **In Progress**: Developer assigns self, begins work
3. **In Review**: PR created, code review requested
4. **Testing**: UAT/QA validation in progress
5. **Done**: PR merged, issue auto-closed

## VALIDATION REQUIREMENTS

### Before Business Approval
- [ ] User need clearly articulated
- [ ] Success metrics are measurable
- [ ] Use cases have acceptance criteria

### Before Technical Approval
- [ ] Every step has specific file paths
- [ ] All actions have verification commands
- [ ] Test locations specified with exact paths


## ERROR PREVENTION

### Common Failures & Solutions
| Issue | Prevention | Recovery |
|-------|------------|----------|
| PR creation fails | Always: `git push -u origin branch` first | Check branch exists remotely |
| Linear not updating | Verify webhook configured | Manual status update via API |
| Tests not found | Use absolute paths in test commands | Run `find tests/ -name "*.test.ts"` |