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

## Success Criteria
- Commands respond within 2 seconds
- Data consistency maintained across operations
- User-friendly error messages for all edge cases
- Easy recovery from common mistakes