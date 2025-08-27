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
**BLOCKING:** Cannot proceed to technical decomposition without explicit approval

### GATE 2: Technical Decomposition Approval
After business approval, create technical task document and get approval before Plan Review.

### GATE 3: Technical Plan Review (MANDATORY)
**Must complete AFTER technical decomposition and BEFORE task splitting evaluation:**

**ACTION:** After technical requirements are created, automatically invoke Plan Reviewer agent to:
1. Review technical decomposition and implementation steps
2. Validate file paths, testing strategy, and acceptance criteria
3. Identify critical issues, clarifications, or improvements needed
4. Create comprehensive review document in task directory
5. Provide implementation readiness assessment

**BLOCKING:** Cannot proceed to task splitting evaluation without Plan Reviewer approval
**DECISION OUTCOMES:**
- ✅ **APPROVED**: Proceed to task splitting evaluation
- ❌ **NEEDS REVISIONS**: Address critical issues before resubmitting 
- 🔄 **NEEDS CLARIFICATIONS**: Make minor updates then proceed

**INTEGRATION:** Use `Task` tool with `plan-reviewer` agent type after technical decomposition is complete

### GATE 4: Task Splitting Evaluation (MANDATORY)
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
  team: "[AGB]",
  description: "[Business context + technical requirements]",
  priority: 0-4  // 0=None, 1=Urgent, 2=High, 3=Normal, 4=Low
})
```

**Note**: If task was split into sub-tasks, create separate Linear issues for each sub-task following the same format.

### Status Progression
1. **Ready for Implementation**: Business approved, technical plan reviewed by Plan Reviewer agent, task automatically evaluated for splitting by Task Splitter agent, Linear issue(s) created, awaiting development
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