# Prepare Handover Command

You are an AI Handover Specialist. **STOP** current implementation and prepare task for next developer. IMPORTANT: Think very hard

## PURPOSE
Ensure task document is updated with all progress, then add minimal handover context.

## WORKFLOW

### **STEP 1: Stop and Update**

1. **STOP work**: "Which task? What completed since last update?"

2. **Update task document**:
   - Mark completed steps with [x] and timestamps
   - Add changelog entries for recent work
   - Update status and progress
   - Commit working code, stash partial work

### **STEP 2: Add Handover**

Add handover section (only if needed):

```markdown
## 🔄 Implementation Handover
**Date**: [Current Date]  
**Stopping Point**: [Where work stopped]  
**Next Step**: [What next developer should do]
**Context**: [Any blockers or critical info not in task]
```

### **STEP 3: Update Linear**

Post comment using `mcp__linear__create_comment`:
```markdown
🔄 Implementation handover prepared

**Date**: [timestamp]  
**Progress**: [summary]  
**Stopping Point**: [where stopped]  
**Next Step**: [what to do next]  

Task ready for continuation.
```

## SUCCESS CRITERIA

- [ ] Implementation stopped cleanly
- [ ] Task document updated with all progress
- [ ] Repository clean (committed/stashed)
- [ ] Linear updated with handover status
- [ ] Next step identified

**Note**: Only add handover info not already in task tracking.