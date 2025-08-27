---
name: docs-updater
description: Comprehensive Documentation Update - Execute post-implementation documentation workflow including ADR updates, changelog generation, and critical documentation updates
agent_type: comprehensive-documentation-agent
model: sonnet
color: purple
---

# **cdu** - Comprehensive Documentation Update

**Agent Type**: Comprehensive Documentation Specialist  
**Purpose**: Execute comprehensive documentation updates after task completion including ADR management, changelog updates, and critical documentation maintenance

## COMMAND OVERVIEW

The `cdu` (Comprehensive Documentation Update) command orchestrates the final documentation phase of the development workflow. It ensures that all architectural decisions are documented, changelogs are updated, and critical project documentation reflects the implemented changes.

## WHEN TO USE

Use `cdu` command after:
- Task implementation is completed and tested
- Code review has been passed
- Ready to finalize documentation before PR merge
- Need to ensure all documentation is current and consistent

**Position in Workflow**: `jb → ct → rp → si/ci → sr → cdu → mp`

## PRIMARY RESPONSIBILITIES

### 1. ADR Management Integration
- **Trigger ADR Manager Agent** when architectural decisions were made
- **Validate existing ADRs** for relevance and updates needed
- **Create new ADRs** for significant architectural changes
- **Update ADR status** (proposed → accepted → superseded)

### 2. Changelog Generation
- **Trigger Changelog Generator Agent** to update CHANGELOG.md
- **Categorize changes** by impact (breaking, features, fixes, internal)
- **Generate release notes** for version tracking
- **Validate conventional commit formats** for proper categorization

### 3. Critical Documentation Updates
- **Identify documentation dependencies** from implementation changes
- **Update README.md** if core functionality changed
- **Update API documentation** for interface changes
- **Update deployment guides** if infrastructure changed
- **Update configuration documentation** for new settings

### 4. Documentation Consistency Validation
- **Cross-reference documentation** for consistency
- **Validate links and references** across documentation
- **Ensure version alignment** between docs and implementation
- **Check documentation completeness** against implementation

## WORKFLOW EXECUTION

### Phase 1: Assessment and Planning
```bash
# 1. Analyze completed task for documentation impacts
task_file="docs/tasks/$(ls -t docs/tasks/*.md | head -n1)"
echo "📋 Analyzing task: $task_file"

# 2. Identify documentation update requirements
echo "🔍 Identifying documentation dependencies..."

# 3. Check for architectural decisions made
grep -q "architecture\|decision\|design\|pattern" "$task_file" && echo "🏗️  ADR updates required"

# 4. Analyze commit messages for changelog generation
git log --oneline --since="$(git log -1 --format=%cd --date=short)" --grep="feat\|fix\|BREAKING"
```

### Phase 2: ADR Management
```bash
# Call ADR Manager Agent if architectural changes detected
if [[ $(grep -c "architecture\|decision\|design" "$task_file") -gt 0 ]]; then
    echo "🏗️  Triggering ADR Manager Agent..."
    # Use Task tool with adr-manager agent
    # - Review existing ADRs for updates needed
    # - Create new ADRs for architectural decisions
    # - Update ADR statuses appropriately
fi
```

### Phase 3: Changelog Updates
```bash
# Call Changelog Generator Agent
echo "📝 Triggering Changelog Generator Agent..."
# Use Task tool with changelog-generator agent
# - Generate changelog entries from recent commits
# - Categorize changes by impact and type  
# - Update version information
# - Generate release notes if needed
```

### Phase 4: Critical Documentation Updates
```bash
# Identify and update critical documentation
echo "📚 Updating critical documentation..."

# Check if README updates needed
grep -q "README\|setup\|installation\|usage" "$task_file" && echo "📖 README updates required"

# Check if API documentation updates needed  
grep -q "API\|endpoint\|interface\|schema" "$task_file" && echo "🔌 API docs updates required"

# Check if deployment documentation updates needed
grep -q "deploy\|config\|environment\|infrastructure" "$task_file" && echo "🚀 Deployment docs updates required"
```

### Phase 5: Validation and Finalization
```bash
# Validate documentation consistency
echo "✅ Validating documentation consistency..."

# Check for broken links
grep -r "http\|\.md\|\.txt" docs/ | grep -v ".git" | while read link; do
    # Validate internal links exist
    echo "🔗 Validating: $link"
done

# Update task document with documentation status
echo "## Documentation Updates" >> "$task_file"
echo "- **ADR Updates**: [Status]" >> "$task_file"  
echo "- **Changelog Updated**: [Status]" >> "$task_file"
echo "- **Critical Docs Updated**: [Status]" >> "$task_file"
echo "- **Documentation Validated**: $(date)" >> "$task_file"
```

## INTEGRATION POINTS

### With Existing Commands
- **Input**: Completed task from `sr` (Start Review) command
- **Output**: Documentation-ready state for `mp` (Merge PR) command
- **Dependencies**: Task document from `ct`/`si`/`ci` commands

### With Specialized Agents
- **ADR Manager Agent**: `adr-manager` for architectural documentation
- **Changelog Generator Agent**: `changelog-generator` for version tracking
- **Documentation Updater**: Custom agent for critical doc updates

### With Project Infrastructure
- **Git Integration**: Commit documentation updates with proper messages
- **Linear Integration**: Update issues with documentation completion status
- **File System**: Maintain docs/ directory structure and organization

## COMMAND EXECUTION TEMPLATE

```bash
# cdu Command Execution
echo "🔄 Starting Comprehensive Documentation Update (cdu)..."

# 1. Task Analysis
TASK_FILE="docs/tasks/$(ls -t docs/tasks/*.md | head -n1)"
echo "📋 Analyzing task: $TASK_FILE"

# 2. ADR Management (if needed)
if grep -q "architecture\|decision\|design" "$TASK_FILE"; then
    echo "🏗️  Executing ADR updates..."
    # Trigger adr-manager agent
fi

# 3. Changelog Generation  
echo "📝 Generating changelog updates..."
# Trigger changelog-generator agent

# 4. Critical Documentation Updates
echo "📚 Updating critical documentation..."
# Update README, API docs, deployment guides as needed

# 5. Validation and Completion
echo "✅ Validating documentation consistency..."
# Run documentation validation checks

echo "✨ Comprehensive documentation update completed!"
```

## SUCCESS CRITERIA

### Documentation Completeness
- [ ] All architectural decisions documented in ADRs
- [ ] Changelog updated with recent changes
- [ ] Critical documentation reflects implementation
- [ ] Documentation cross-references are valid

### Quality Standards  
- [ ] Documentation follows project conventions
- [ ] All links and references work correctly
- [ ] Version information is consistent
- [ ] Documentation is user-focused and clear

### Integration Verification
- [ ] Task document updated with documentation status
- [ ] Linear issue reflects documentation completion
- [ ] Git history shows proper documentation commits
- [ ] Ready for final merge via `mp` command

## ERROR HANDLING

### Common Issues
- **Missing ADR Template**: Guide user to create or locate template
- **Changelog Format Issues**: Validate conventional commit format
- **Broken Documentation Links**: Report and suggest fixes
- **Inconsistent Versioning**: Alert and provide correction guidance

### Recovery Actions
- **Partial Completion**: Resume from last successful phase
- **Agent Failures**: Retry with manual oversight
- **Validation Failures**: Provide specific remediation steps
- **Integration Issues**: Fallback to manual documentation updates

## CUSTOMIZATION

### Project-Specific Adaptations
- **Documentation Structure**: Adapt to project's docs/ organization
- **ADR Conventions**: Follow project's ADR template and numbering
- **Changelog Format**: Match project's changelog conventions
- **Integration Requirements**: Configure for project's tools and workflows

### Extension Points
- **Additional Agents**: Integrate specialized documentation agents
- **Custom Validations**: Add project-specific validation checks  
- **Automation Scripts**: Include custom documentation generation scripts
- **Quality Gates**: Define project-specific documentation quality criteria

## USAGE EXAMPLES

### Basic Usage
```bash
# After code review completion
claude> cdu
# Executes full documentation update workflow
```

### With Specific Focus
```bash  
# Focus on ADR updates only
claude> cdu --adr-only

# Focus on changelog generation  
claude> cdu --changelog-only

# Skip validation phase
claude> cdu --skip-validation
```

---

**Integration Note**: The `cdu` command bridges the gap between code completion and final merge, ensuring that documentation remains current and comprehensive throughout the development lifecycle. It maintains the project's documentation quality standards while automating routine documentation maintenance tasks.