# Business Requirements

## Project Overview
Telegram bot for managing Tres Dias event participants with focus on simplicity and maintainability.

## Core Business Functions

### 1. Participant Management
- Add new participants with required information
- Update existing participant details
- Remove participants when necessary
- Validate participant data integrity

### 2. Search & Discovery
- Search by name (partial matching)
- Filter by room assignment
- Filter by role (pilgrim, team member, etc.)
- List all participants with pagination

### 3. Payment Tracking
- Mark participants as paid/unpaid
- Track payment amounts and dates
- View payment status in search results
- Generate payment reports

## Business Rules
- Each participant must have: name, room, role
- Names must be unique within the system
- Payment amounts must be positive numbers
- Room assignments must be valid room numbers/names

## Implementation Status

### Phase 1: Foundation (COMPLETED)
- Project structure fully established per PROJECT_PLAN.md
- 3-layer architecture implemented (Bot → Services → Data)
- Python package structure with proper imports
- Testing framework and development environment configured
- Configuration management with environment variables
- All foundation requirements validated and tested

### Upcoming Phases
- **Phase 2**: Core Features - Search and participant management
- **Phase 3**: Payment Tracking - Complete payment management system
- **Phase 4**: Polish & Enhancement - Production-ready features

## Success Criteria
- Commands respond within 2 seconds
- Data consistency maintained across operations
- User-friendly error messages for all edge cases
- Easy recovery from common mistakes