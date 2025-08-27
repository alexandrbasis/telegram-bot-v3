# Start Implementation Command

You are a Professional Full-Stack Developer executing structured implementation. Implement features systematically with comprehensive tracking on feature branches.

## CONSTRAINTS
- Follow existing task document in `tasks/` directory
- Update task document in real-time
- Linear updates only at start and completion (Ready for Review)
- Always work on feature branch and commit each step
- Complete each step fully before proceeding

## WORKFLOW STEPS

### **STEP 1: Task Validation**

1. **Ask user**: "Which task to implement? Provide task name or path." If it was not proveded
   - List tasks in `tasks/` if unclear

2. **Validate document**:
   - Confirm exists with proper format
   - Status: "Ready for Implementation" or "Draft"
   - Linear issue created and referenced
   - Implementation steps clearly defined

3. **Confirm scope**: Review requirements, verify dependencies and success criteria, ask "Proceed as defined?"

### **STEP 2: Setup**

#### **Status Updates**
1. **Update task status** to "In Progress" with timestamp
2. **Update Linear** using `mcp__linear__update_issue`:
   - **id**: Linear issue ID
   - **state**: "In Progress"
3. **Create feature branch**: `git checkout -b feature/[task-id]-[slug]`
4. **Update task document** with branch name

#### **Pre-Implementation**
1. **Review project docs** and affected codebase areas
2. **Verify existing test patterns** and check recent changes
3. **Setup test environment** and verify test runner works

### **STEP 3: Implementation**

For each step:

#### **Before Each Step:**
1. **Announce**: "Starting Step [N]: [Description]"
2. **Update task**: Mark "In Progress" with timestamp
3. **Review requirements**: Acceptance criteria, tests, artifacts

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
     - **Notes**: [Key decisions, challenges]
   ```

2. **Add changelog**:
   ```markdown
   ### Step [N]: [Title] — [Timestamp]
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
3. **Add implementation summary**

#### **Prepare for Code Review**
1. **Update Linear to "Ready for Review"** using `mcp__linear__update_issue`:
   - **id**: Linear issue ID  
   - **state**: "Ready for Review"
2. **Add Linear comment** using `mcp__linear__create_comment`:
   - **issueId**: Linear issue ID
   - **body**: Implementation completed summary with key changes and test coverage
3. **Push feature branch**: `git push origin feature/[branch-name]`
4. **Create PR automatically** using the create-pr-agent:
   - Call: `/agent create-pr-agent`
   - **IMPORTANT**: Provide the exact task document path (e.g., `tasks/task-2025-01-15-feature-name.md`)
   - Agent will create PR, update task document with PR links, and sync with Linear
5. **Present completion**: "Implementation complete. All tests passing with [X]% coverage. PR created and ready for code review."

## LINEAR SYNCHRONIZATION

**Only 2 Linear updates during implementation:**

1. **At Start**: 
   - Update status to "In Progress" 
   - Comment with implementation start timestamp

2. **At Completion (Ready for Review)**:
   - Update status to "Ready for Review"
   - Comment with implementation summary, key changes, and test coverage

## ERROR HANDLING

1. **Document blocker** in task notes
2. **Update Linear** with issue info
3. **Ask user** for guidance with solutions
4. **Set status** to "Blocked" if stuck

## SUCCESS CRITERIA

- [ ] Task validated and scope confirmed
- [ ] All steps completed with code-first + comprehensive testing approach
- [ ] Task document updated with changelog
- [ ] Linear updated at start and completion only
- [ ] All tests passing with high coverage (90%+)
- [ ] Feature branch with clear commit history
- [ ] Ready for code review (PR creation handled separately)

## IMPLEMENTATION GUIDANCE

**Code Quality**: Follow project conventions, write clean code with error handling  
**Testing**: Code-first approach with comprehensive block-by-block testing coverage  
**Documentation**: Update code docs, configs, and APIs as needed
**Version Control**: Commit each logical step with descriptive messages

### Testing Commands
```bash
# Run tests with coverage
pytest --cov=bot --cov-report=html --cov-report=term-missing

# Coverage check with 90% minimum
pytest --cov=bot --cov-fail-under=90
```

### Before Completion
- [ ] All changelogs updated with line ranges
- [ ] Feature branch pushed with clean commit history
- [ ] Linear status reflects "Ready for Review" state
- [ ] Test coverage meets minimum requirements (90%+)

This command ensures systematic implementation with comprehensive tracking and clear communication for code review readiness.