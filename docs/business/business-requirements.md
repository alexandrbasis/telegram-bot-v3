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
- Search by name (partial matching with fuzzy matching)
- Search by room number (alphanumeric room identifiers)
- Search by floor (with room-by-room breakdown)
- Filter by role (candidate, team member)
- Quick bulk list access by role (Get List feature)
- List all participants with offset-based pagination
- Interactive participant editing from search results

### 3. Quick List Access (Get List Feature)
- **Team Member Lists**: Instant access to complete team member roster with clothing sizes and logistics information
- **Candidate Lists**: Quick candidate review with complete information for administrative tasks
- **Bulk Information Retrieval**: No search queries required - direct access to categorized participant lists
- **Logistics Support**: Formatted display with sizes, churches, and dates for event planning
- **Administrative Efficiency**: 2-click access from main menu to complete participant categories

### 4. Payment Tracking
- Mark participants as paid/unpaid
- Track payment amounts and dates
- View payment status in search results
- Generate payment reports

## Business Rules
- Each participant must have: name, room, role
- Names must be unique within the system
- Payment amounts must be positive numbers
- Room assignments must be valid room numbers/names

## Success Criteria
- Commands respond within 2 seconds
- Data consistency maintained across operations
- User-friendly error messages for all edge cases
- Easy recovery from common mistakes