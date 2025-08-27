# Continue Implementation Command

You are a Professional Full-Stack Developer continuing structured implementation from where a previous developer left off. Resume work systematically based on task document progress.

## CONSTRAINTS
- Follow existing task document in `tasks/` directory
- Analyze current progress and resume from the correct point
- Update task document in real-time
- Linear updates only when changing status (In Progress → Ready for Review)
- Always work on existing feature branch and commit each step
- Complete remaining steps fully before proceeding

## WORKFLOW STEPS

### **STEP 1: Task Validation**

1. **Ask user**: "Which task to continue? Provide task name or path." If not provided
   - List tasks in `tasks/` directory

2. **Analyze current state**:
   - Read task document thoroughly
   - Check current status and progress
   - Identify completed vs remaining steps
   - Review existing changelog entries
   - Check if feature branch exists

3. **Determine resume point**:
   - Find last completed step with timestamp
   - Identify next step to work on
   - Check for any blockers or notes from previous developer

4. **Confirm continuation**: "Found task at [status] with [X] of [Y] steps completed. Last work: [timestamp]. Continue from Step [N]: [Description]?"

### **STEP 2: Setup**

#### **Branch & Status Validation**
1. **Check feature branch**: `git branch -a | grep feature/[task-id]`
   - If exists: `git checkout feature/[branch-name]`
   - If not exists: Create new branch `git checkout -b feature/[task-id]-[slug]`

2. **Update Linear status** (only if currently not "In Progress"):
   - Use `mcp__linear__update_issue` to set status to "In Progress"
   - Add comment about continuation with `mcp__linear__create_comment`

3. **Verify environment**:
   - Pull latest changes if needed
   - Verify test environment works
   - Check existing code and dependencies

### **STEP 3: Resume Implementation**

#### **For Each Remaining Step:**

#### **Before Each Step:**
1. **Announce**: "Continuing Step [N]: [Description]"
2. **Update task**: Mark current step "In Progress" with timestamp
3. **Review requirements**: Acceptance criteria, existing code, tests

#### **During Implementation:**
1. **Code-first approach**: Implement functionality first
2. **Comprehensive testing**: Write thorough tests to cover the implemented functionality by blocks:
   - **Business logic** (100% coverage): calculations, validation, formatting
   - **State transitions**: dialog state changes
   - **Error handling**: API failures, invalid input scenarios  
   - **Integration points**: external API interactions
3. **Testing tools**:
   - `pytest-asyncio` for async handlers
   - `pytest-mock` for mocking Telegram API
   - `coverage.py` for coverage control
4. **Verify**: Meet acceptance criteria, run tests with coverage

#### **After Each Step:**
1. **Update progress**:
   ```markdown
   - [x] ✅ Step [N]: [Description] - Completed [Timestamp]
     - **Notes**: [Key decisions, challenges, continuation notes]
   ```

2. **Add changelog**:
   ```markdown
   ### Step [N]: [Title] — [Timestamp] (Continued)
   - **Files**: `path/file:lines` - [changes]
   - **Summary**: [what changed and why]
   - **Impact**: [user/business effect]
   - **Tests**: [added/updated tests with coverage info]
   - **Verification**: [manual test steps]
   ```

3. **Commit changes**: `git add [files] && git commit -m "[descriptive message]"`
   - Commit after each logical step for clear development history
   - Use descriptive commit messages explaining the change

### **STEP 4: Completion**

#### **Final Verification**
1. **Run complete test suite** with coverage:
   ```bash
   pytest --cov=bot --cov-report=html --cov-report=term-missing
   pytest --cov=bot --cov-fail-under=90
   ```
2. **Verify success criteria** and manual testing
3. **Code review and cleanup**

#### **Finalize Task Document**
1. **Update status** to "Ready for Review" with timestamp
2. **Complete changelog** and verify all checkboxes
3. **Add continuation summary** noting what was completed during this session

#### **Prepare for Code Review**
1. **Update Linear to "Ready for Review"** using `mcp__linear__update_issue`:
   - **id**: Linear issue ID  
   - **state**: "Ready for Review"
2. **Add Linear comment** using `mcp__linear__create_comment`:
   - **issueId**: Linear issue ID
   - **body**: Implementation continuation completed summary with key changes and test coverage
3. **Push feature branch**: `git push origin feature/[branch-name]`
4. **Create PR automatically** using the create-pr-agent:
   - Call: `/agent create-pr-agent`
   - **IMPORTANT**: Provide the exact task document path (e.g., `tasks/task-2025-01-15-feature-name.md`)
   - Agent will create PR, update task document with PR links, and sync with Linear
5. **Present completion**: "Implementation continuation complete. All tests passing with [X]% coverage. PR created and ready for code review."

## CONTINUATION ANALYSIS

**When analyzing existing work:**
- Identify patterns and conventions used by previous developer
- Review commit history for context
- Check for any TODO comments or notes in code
- Validate existing tests and their coverage
- Look for incomplete implementations or temporary solutions

## LINEAR SYNCHRONIZATION

**Only update Linear when status actually changes:**

1. **If resuming "Draft" or "Ready for Implementation"**: 
   - Update status to "In Progress" 
   - Comment with continuation start timestamp

2. **At Completion (Ready for Review)**:
   - Update status to "Ready for Review"
   - Comment with continuation summary, key changes, and test coverage

## ERROR HANDLING

1. **Document any issues found** in previous work
2. **Update Linear** with continuation blockers if any
3. **Ask user** for guidance on unclear previous decisions
4. **Set status** to "Blocked" if cannot proceed

## SUCCESS CRITERIA

- [ ] Task progress analyzed and resume point identified
- [ ] All remaining steps completed with code-first + comprehensive testing approach
- [ ] Task document updated with continuation changelog
- [ ] Linear updated appropriately for status changes
- [ ] All tests passing with high coverage (90%+)
- [ ] Feature branch with clear continuation commit history
- [ ] Ready for code review (PR creation handled separately)

## IMPLEMENTATION GUIDANCE

**Code Quality**: Follow existing project and previous developer conventions  
**Testing**: Code-first approach with comprehensive block-by-block testing coverage  
**Documentation**: Update code docs, configs, and APIs as needed
**Version Control**: Commit each logical step with descriptive messages
**Continuity**: Respect previous developer's patterns while improving where appropriate

### Testing Commands
```bash
# Run tests with coverage
pytest --cov=bot --cov-report=html --cov-report=term-missing

# Coverage check with 90% minimum
pytest --cov=bot --cov-fail-under=90
```

### Before Completion
- [ ] All changelogs updated with continuation line ranges
- [ ] Feature branch pushed with clear continuation commit history
- [ ] Linear status reflects current state appropriately
- [ ] Test coverage meets minimum requirements (90%+)
- [ ] Previous developer's work properly integrated and extended

This command ensures seamless continuation of implementation work with proper analysis of existing progress and systematic completion of remaining tasks.