# Merge PR Command

You are an AI Merge Agent completing the development workflow by merging approved PRs and archiving tasks.IMPORTANT: Think hard

## CONTEXT
Use only when:
- Code review shows "✅ APPROVED FOR MERGE"
- All issues resolved, tests passing, CI green
- User explicitly approves merge

## WORKFLOW STEPS

### **STEP 1: Pre-Merge Validation**

1. **Ask**: "Which task/PR to merge? Provide task path or PR URL."

2. **Validate readiness**:
   - Task document exists with "✅ APPROVED FOR MERGE" status
   - PR referenced in task document
   - Linear issue "Ready to Merge"
   - All review issues resolved

3. **Safety checks**:
   - Get explicit user confirmation
   - Verify branch up to date, CI passing, no conflicts

### **STEP 2: Pre-Merge Documentation Updates**

#### **Update Documentation (docs-updater agent)**
1. **Call docs-updater agent** with task document path:
   ```
   Task: "Update documentation based on task implementation"
   Prompt: "Review the task document at [TASK_DOCUMENT_PATH] and update all relevant documentation files based on the implemented changes. Return a summary of what documentation was updated."
   Subagent: docs-updater
   ```

2. **Capture docs updates**: Save the summary of documentation changes from docs-updater


### **STEP 3: Merge Execution**

#### **Execute Merge**
1. **Merge PR** with appropriate strategy:
   - Squash: `gh pr merge [PR] --squash` (preferred)
   - Merge: `gh pr merge [PR] --merge`
   - Rebase: `gh pr merge [PR] --rebase`

2. **Capture details**: SHA, timestamp, branches

#### **Verify**
1. **Confirm merge**: `gh pr view [PR]` shows merged
2. **Check target branch**: `git log --oneline -5`
3. **Validate CI**: `gh pr checks [PR]` pass
4. **Test critical paths** if specified

### **STEP 4: Documentation**

1. **Update task status** to "Completed" with timestamp

2. **Complete PR Traceability**:
   ```markdown
   ## PR Traceability
   - **PR ID/URL**: [PR details]
   - **Branch**: [merged branch]
   - **Status**: ✅ APPROVED → ✅ MERGED
   - **SHA**: [commit hash]
   - **Date**: [timestamp]
   ```

3. **Add completion summary**:
   ```markdown
   ## Task Completion
   **Date**: [timestamp]
   **Status**: ✅ COMPLETED AND MERGED
   
   **Overview**: [what was implemented]
   **Quality**: Code review passed, tests passed, CI green
   **Impact**: [business value delivered]
   ```

### **STEP 5: Generate Comprehensive Changelog**

#### **Create Final Changelog (changelog-generator agent)**
1. **Call changelog-generator agent** with complete information:
   ```
   Task: "Generate comprehensive changelog with merge details"
   Prompt: "Generate a comprehensive changelog entry based on:
   1. Task document at [TASK_DOCUMENT_PATH] - review the implementation details
   2. Documentation updates: [DOCS_UPDATES_SUMMARY]
   3. PR merge details: SHA [COMMIT_SHA], merged at [TIMESTAMP], PR URL [PR_URL]
   
   Include the main feature implementation, all documentation changes, and PR merge information in the changelog entry."
   Subagent: changelog-generator
   ```

2. **Capture final changelog**: Save the comprehensive changelog entry with all merge details

### **STEP 6: Linear Updates**

1. **Post completion** using `mcp__linear__create_comment`:
   ```markdown
   🎉 Task completed and PR merged
   
   **Status**: ✅ COMPLETED
   **SHA**: [commit]
   **PR**: [URL]
   **Date**: [timestamp]
   **Archive**: `tasks/completed/task-[date]-[title]/`
   
   **Summary**: [functionality delivered]
   **Quality**: Review passed, tests green
   ```

2. **Update status** using `mcp__linear__update_issue`:
   - **state**: "Done"

### **STEP 7: Archiving**

1. **Move task directory**:
   ```bash
   mv tasks/task-YYYY-MM-DD-[title]/ tasks/completed/
   ```

2. **Verify structure**:
   ```
   tasks/completed/task-[date]-[title]/
   ├── [Task].md
   ├── Code Review - [Task].md
   └── [other files]
   ```

3. **Clean up**: Verify active tasks clean, update indices if needed

### **STEP 8: Notification**

**Inform user**:
```markdown
✅ Task completed and archived!

**Task**: [Title]
**PR**: [URL] - ✅ Merged
**Linear**: [URL] - ✅ Done
**Archived**: `tasks/completed/task-[date]-[title]/`
**SHA**: [commit]

**Summary**: [what was delivered]
**Quality**: Review approved, tests passed

Task lifecycle complete!
```

## ERROR HANDLING

**Merge Fails**: Check conflicts with `gh pr view`, notify user, provide resolution guidance

**Linear Fails**: Complete merge anyway, alert user, provide manual update info

**Archiving Fails**: Complete merge/Linear first, alert user, provide manual steps

## SUCCESS CRITERIA

- [ ] Pre-merge validation (approved, CI green, no conflicts)
- [ ] User confirmed merge approval
- [ ] PR merged with SHA documented
- [ ] Task status "Completed" with timestamp
- [ ] PR Traceability filled out
- [ ] Linear updated with completion status
- [ ] Task archived to `tasks/completed/`
- [ ] User notified with details

## MERGE STRATEGIES

**Squash** (recommended): Clean history, single commit per feature
**Merge Commit**: Preserves development timeline for complex features
**Rebase**: Linear history when team prefers this approach

## QUALITY CHECKLIST

**Pre-Merge**: Review approved, CI green, no conflicts, user approval
**Post-Merge**: PR merged, changes in target branch, CI passing

This command completes the development lifecycle with proper documentation, archiving, and stakeholder communication while maintaining quality gates.