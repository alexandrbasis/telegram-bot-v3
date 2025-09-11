# User Stories

## Participant Management

**As an event organizer, I want to:**
- Add new participants quickly with `/add name room role`
- **Edit participant information when details change** ✅ *Implemented*
  - Access comprehensive editing interface from search results
  - Edit all 13 participant fields with appropriate input methods
  - Use button selection for predefined fields (Gender, Size, Role, Department, Payment Status)
  - Use text input for free text fields with validation
  - See Russian interface with clear field labels and prompts
  - Get validation errors in Russian with retry instructions
  - Save all changes at once or cancel without losing search context
- Remove participants who can't attend
- **View complete participant information** ✅ *Implemented*
  - See full participant profile with all field values
  - Access detailed view through "Подробнее" (Details) buttons in search results
  - Navigate between editing and viewing seamlessly

## Search & Discovery

**As an event organizer, I want to:**
- **Find participants by name with fuzzy matching** ✅ *Implemented*
  - Use `/search name` command or main menu "🔍 Поиск участников" button
  - Find participants with Russian or English names
  - See match quality indicators (Отличное совпадение, Хорошее совпадение, Частичное совпадение)
  - Access detailed participant information through "Подробнее" buttons
- **Search participants by room and floor** ✅ *Implemented*
  - Find all participants in a specific room with `/search_room number`
  - View all participants on a floor with `/search_floor number`
  - See structured Russian results with role and department information
  - Get room-by-room breakdown for floor searches
- **Access quick participant lists by role** ✅ *Implemented*
  - Click "📋 Получить список" from main menu for instant bulk access
  - View complete team member roster for logistics planning (clothing sizes, churches, dates)
  - Review candidate lists for administrative tasks and committee discussions
  - Navigate through large lists with advanced pagination that prevents skipping participants
  - Get 2-click access without requiring search queries
- Browse all participants with offset-based pagination that handles large datasets efficiently

## Payment Tracking

**As an event organizer, I want to:**
- Mark participants as paid with `/pay name amount`
- See payment status in search results
- Generate payment reports to track finances
- View payment history for each participant

## User Experience

**As a user, I want to:**
- Get clear help messages when I make mistakes
- See confirmation when actions complete successfully
- Navigate large lists easily with pagination
- Use intuitive commands without documentation