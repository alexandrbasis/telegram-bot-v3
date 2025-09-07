# Create PR Command

You are an AI assistant that creates PRs for tasks and automatically links them to task documents and Linear issues.

## CONTEXT
Use when:
- Implementation is complete and ready for review
- Task document exists with completed work
- Feature branch has committed changes
- Ready to create PR and update documentation

## WORKFLOW

### **STEP 1: Input Validation**

1. **Ask user**: "Which task to create PR for? Provide task path."

2. **Validate task**:
   - Task document exists in `tasks/` directory
   - Linear issue ID referenced in task
   - Feature branch exists with changes
   - Implementation appears complete

3. **Confirm scope**: Review task requirements and verify all acceptance criteria met

### **STEP 2: Create PR**

1. **Generate PR details** from task document:
   - Title: Based on task title
   - Description: Include task overview, implementation details, testing notes
   - Link to task document and Linear issue

2. **Create PR** using `gh pr create`:
   ```bash
   gh pr create --title "[Task Title]" --body "$(cat <<'EOF'
   ## Summary
   [Brief description of changes]
   
   ## Task Reference
   - **Task**: [task document path]
   - **Linear**: [Linear issue URL]
   
   ## Implementation
   [Key changes and approach]
   
   ## Testing
   [Testing approach and coverage]
   
   🤖 Generated with Claude Code
   EOF
   )"
   ```

3. **Capture PR details**: URL, number, branch info

### **STEP 3: Update Task Document**

1. **Add PR section** to task document:
   ```markdown
   ## PR Traceability
   - **PR URL**: [GitHub PR URL]
   - **PR Number**: #[number]
   - **Branch**: [feature branch name]
   - **Status**: 🔄 Ready for Review
   - **Created**: [timestamp]
   ```

2. **Update task status** to "Ready for Review"

### **STEP 4: Link to Linear**

1. **Add PR comment** to Linear issue using `mcp__linear__create_comment`:
   ```markdown
   🚀 PR Created and Ready for Review
   
   **PR**: [GitHub PR URL]
   **Branch**: [branch name]
   **Status**: Ready for Review
   **Next**: Awaiting code review
   
   **Summary**: [brief implementation summary]
   ```

2. **Update Linear status** using `mcp__linear__update_issue`:
   - **state**: "In Review"

### **STEP 5: Confirmation**

Notify user:
```markdown
🚀 PR created successfully!

**Task**: [task title]
**PR**: [PR URL] 
**Linear**: Updated with PR link and status
**Status**: Ready for Review

**Next Steps**:
- Request code review
- Address any feedback
- Run final tests before merge
```

## ERROR HANDLING

**Branch Issues**: Check current branch, verify changes committed, guide user to fix

**Linear Fails**: Create PR anyway, alert user, provide manual Linear update steps

**Task Document Missing**: Guide user to create proper task document first

## SUCCESS CRITERIA

- [ ] PR created with proper title and description
- [ ] PR URL added to task document 
- [ ] Task status updated to "Ready for Review"
- [ ] Linear issue updated with PR link
- [ ] Linear status changed to "In Review"
- [ ] User notified with PR details and next steps

## PR TEMPLATE STRUCTURE

**Title Format**: `[Feature/Fix/Enhancement]: [Brief Description]`

**Description Includes**:
- Task and Linear issue references
- Implementation summary
- Testing approach
- Any special deployment notes