# 🔄 MULTI-ROLE & MULTI-SCHOOL SCENARIOS - COMPLETE GUIDE

**Your Questions Answered**: How the platform handles complex real-world scenarios

---

## ✅ SCENARIO 1: PARENT WITH MULTIPLE CHILDREN IN SAME SCHOOL

### **Current Implementation** ✅ FULLY SUPPORTED

#### **Database Design**
```sql
-- student_parents table (many-to-many relationship)
CREATE TABLE student_parents (
    student_id UUID REFERENCES students(id),
    parent_id UUID REFERENCES parents(id),
    is_primary BOOLEAN,
    can_pickup BOOLEAN,
    relationship VARCHAR(50)  -- father, mother, guardian
);

-- A parent can have UNLIMITED children
-- Each child can have MULTIPLE parents/guardians
```

#### **How It Works**

**Example**: Mrs. Nakato has 3 children at the same school:
- Mary (Class 5A)
- John (Primary 3)
- Peter (Baby Class)

**What Mrs. Nakato Sees in Parent Portal**:

```json
{
  "parent_id": "parent-123",
  "name": "Sarah Nakato",
  "children": [
    {
      "id": "student-001",
      "name": "Mary Nakato",
      "class": "Class 5A",
      "attendance_today": "present",
      "fee_balance": 50000,
      "recent_grades": [...]
    },
    {
      "id": "student-002",
      "name": "John Nakato",
      "class": "Primary 3",
      "attendance_today": "present",
      "fee_balance": 75000,
      "recent_grades": [...]
    },
    {
      "id": "student-003",
      "name": "Peter Nakato",
      "class": "Baby Class",
      "attendance_today": "absent",
      "fee_balance": 0,
      "recent_grades": []
    }
  ],
  "total_fee_balance": 125000,
  "notifications": [
    "Mary: Scored 85/100 in Math",
    "John: Present today",
    "Peter: Absent today - please confirm"
  ]
}
```

#### **Features That Work**:
1. ✅ **Single Login** - One account to see all children
2. ✅ **Unified Dashboard** - All children at a glance
3. ✅ **Child Switching** - Tap a child to see detailed view
4. ✅ **Combined Notifications** - All children's updates in one place
5. ✅ **Bulk Payments** - Pay fees for multiple children at once
6. ✅ **Per-Child Details** - Detailed reports for each child

#### **API Endpoint**:
```bash
GET /api/{school_id}/parent/{parent_id}/dashboard

Response:
{
  "children": [
    {"id": "...", "name": "Mary", "class": "5A", ...},
    {"id": "...", "name": "John", "class": "P3", ...},
    {"id": "...", "name": "Peter", "class": "Baby", ...}
  ]
}
```

#### **Notifications Example**:
When teacher marks attendance:
```
Teacher: "Mark all Class 5A as present"
↓
System finds Mary in Class 5A
↓
System finds Mary's parents (Mr. & Mrs. Nakato)
↓
Both parents get notification:
"Mary marked present today at 8:00 AM"
```

---

## ✅ SCENARIO 2: TEACHER WHO ALSO MANAGES INVENTORY

### **Current Implementation** ✅ FULLY SUPPORTED

#### **Database Design**
```sql
-- users table (authentication)
CREATE TABLE users (
    id UUID PRIMARY KEY,
    school_id UUID,
    email VARCHAR(255),
    role VARCHAR(50)  -- Can be: teacher, admin, staff
);

-- user_links table (multi-role support)
CREATE TABLE user_links (
    user_id UUID REFERENCES users(id),
    entity_type VARCHAR(50),  -- teacher, parent, inventory_manager
    entity_id UUID,
    is_primary BOOLEAN
);

-- A user can have MULTIPLE roles simultaneously
-- Example: User is both a teacher AND inventory manager
```

#### **How It Works**

**Example**: Mr. Mukasa is:
- Science teacher for Class 5A
- Inventory manager for school supplies

**Setup in Database**:
```sql
-- 1. Create user account
INSERT INTO users (id, school_id, email, role)
VALUES ('user-123', 'school-abc', 'mukasa@school.com', 'teacher');

-- 2. Link to teacher entity
INSERT INTO user_links (user_id, entity_type, entity_id, is_primary)
VALUES ('user-123', 'teacher', 'teacher-456', true);

-- 3. Link to inventory manager role
INSERT INTO user_links (user_id, entity_type, entity_id, is_primary)
VALUES ('user-123', 'inventory_manager', 'inventory-mgr-789', false);
```

**What Mr. Mukasa Sees**:

His dashboard has **role switcher**:
```
┌─────────────────────────────┐
│  👤 Mr. Mukasa              │
│  📧 mukasa@school.com       │
├─────────────────────────────┤
│  🎓 Teacher Mode     [•]    │  ← Currently active
│  📦 Inventory Mode   [ ]    │
└─────────────────────────────┘
```

**In Teacher Mode**:
- Mark attendance
- Record grades
- Upload photos
- Chat with parents
- View timetable

**In Inventory Mode** (switch by clicking):
- Manage stock
- Record supplies in/out
- Generate inventory reports
- Order new supplies
- Track expenses

#### **API Endpoints**:
```bash
# Get user's roles
GET /api/users/{user_id}/roles

Response:
{
  "user_id": "user-123",
  "primary_role": "teacher",
  "additional_roles": ["inventory_manager"],
  "permissions": [
    "mark_attendance",
    "record_grades",
    "manage_inventory",
    "order_supplies"
  ]
}

# Switch role
POST /api/users/{user_id}/switch-role
{
  "role": "inventory_manager"
}
```

#### **Permissions System**:
```python
# Each role has specific permissions
ROLE_PERMISSIONS = {
    "teacher": [
        "mark_attendance",
        "record_grades",
        "view_students",
        "upload_photos"
    ],
    "inventory_manager": [
        "manage_inventory",
        "order_supplies",
        "record_stock",
        "view_expenses"
    ]
}

# User with multiple roles gets COMBINED permissions
user_permissions = []
for role in user.roles:
    user_permissions.extend(ROLE_PERMISSIONS[role])

# Mr. Mukasa can do BOTH teacher AND inventory tasks
```

#### **Real Example**:
```
Morning: Mr. Mukasa teaches Class 5A
↓
Action: Marks attendance for 40 students
Mode: Teacher Mode

Afternoon: Lab needs supplies
↓
Action: Records 50 test tubes taken from inventory
Mode: Inventory Mode

Evening: Uploads exam results
↓
Action: Bulk uploads grades via CSV
Mode: Teacher Mode
```

---

## ✅ SCENARIO 3: PARENT WITH CHILDREN IN DIFFERENT SCHOOLS

### **Current Implementation** ⚠️ PARTIALLY SUPPORTED (NEEDS ENHANCEMENT)

#### **The Challenge**
Mrs. Nakato has:
- Mary at **Angels Primary School** (Kampala)
- John at **St. Joseph Secondary** (Entebbe)
- Both schools use our AI platform

**What Mrs. Nakato Wants**:
- One login for both schools
- Switch between schools easily
- Combined view of all children
- Separate notifications per school

#### **Solution: Cross-School User Accounts**

**Option A: Single Account, Multiple Schools (RECOMMENDED)**

```sql
-- Enhanced users table
CREATE TABLE users (
    id UUID PRIMARY KEY,  -- Same user across schools
    email VARCHAR(255) UNIQUE,  -- Same email
    phone VARCHAR(50)
);

-- School-specific user data
CREATE TABLE user_school_access (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    school_id UUID REFERENCES schools(id),
    role VARCHAR(50),  -- parent, teacher, admin
    is_active BOOLEAN,
    UNIQUE(user_id, school_id)
);

-- Parent-child links (cross-school)
CREATE TABLE parent_children_global (
    parent_user_id UUID REFERENCES users(id),
    child_student_id UUID REFERENCES students(id),
    school_id UUID REFERENCES schools(id)
);
```

**How It Works**:

1. **Registration**:
```
Mrs. Nakato registers at Angels Primary:
- Email: nakato@gmail.com
- Creates account (user-123)
- Linked to Mary at Angels Primary

Later, at St. Joseph Secondary:
- Same email: nakato@gmail.com
- System detects existing account
- Links John to same account (user-123)
- Now has access to BOTH schools
```

2. **Login Experience**:
```
Mrs. Nakato logs in:
↓
System shows:
┌─────────────────────────────────┐
│  👤 Sarah Nakato                │
│  📧 nakato@gmail.com            │
├─────────────────────────────────┤
│  Select School:                 │
│                                 │
│  🏫 Angels Primary School       │
│     └─ Mary (Class 5A)          │
│     [View Dashboard]            │
│                                 │
│  🏫 St. Joseph Secondary        │
│     └─ John (Form 2)            │
│     [View Dashboard]            │
│                                 │
│  📊 Combined View (All)         │
│     [View All Children]         │
└─────────────────────────────────┘
```

3. **Dashboard Options**:

**Option 1: School-Specific View**
```
Selected: Angels Primary School
↓
Shows:
- Mary's attendance
- Mary's grades
- Mary's fees
- Angels Primary notifications
```

**Option 2: Combined View (ALL CHILDREN)**
```
Selected: All Schools
↓
Shows:
┌─────────────────────────────┐
│  Angels Primary School      │
│  └─ Mary (Class 5A)         │
│     ✅ Present today        │
│     💰 Fees: 50,000 UGX    │
│     📚 Recent: 85% in Math │
└─────────────────────────────┘

┌─────────────────────────────┐
│  St. Joseph Secondary       │
│  └─ John (Form 2)           │
│     ✅ Present today        │
│     💰 Fees: 150,000 UGX   │
│     📚 Recent: 78% in Chem │
└─────────────────────────────┘

Total Fees Due: 200,000 UGX
```

4. **Notifications**:
```
All notifications in one place, tagged by school:

🏫 Angels Primary
- Mary marked present (8:00 AM)
- Mary scored 85/100 in Math

🏫 St. Joseph Secondary
- John marked present (7:30 AM)
- Fees due for John: 150,000 UGX
```

#### **API Endpoints** (NEW - NEED TO BUILD):

```bash
# Get user's schools
GET /api/users/{user_id}/schools

Response:
{
  "user_id": "user-123",
  "schools": [
    {
      "school_id": "school-abc",
      "school_name": "Angels Primary",
      "children": [
        {"id": "...", "name": "Mary", "class": "5A"}
      ]
    },
    {
      "school_id": "school-xyz",
      "school_name": "St. Joseph Secondary",
      "children": [
        {"id": "...", "name": "John", "class": "Form 2"}
      ]
    }
  ]
}

# Get combined dashboard (all schools)
GET /api/users/{user_id}/dashboard/combined

Response:
{
  "schools": [
    {
      "school": "Angels Primary",
      "children": [...],
      "notifications": [...],
      "total_fees": 50000
    },
    {
      "school": "St. Joseph Secondary",
      "children": [...],
      "notifications": [...],
      "total_fees": 150000
    }
  ],
  "total_fees_all_schools": 200000
}
```

---

## 🛠️ WHAT WE NEED TO BUILD

### **Already Works** ✅
1. ✅ Parent with multiple children in same school
2. ✅ Teacher with multiple roles (teacher + inventory)
3. ✅ Multi-role permission system

### **Needs Enhancement** 🔨
1. **Cross-School Parent Accounts**
   - User can link to multiple schools
   - Combined dashboard view
   - School switcher in UI
   - Unified notifications

**Estimated Time**: 4-6 hours

**Files to Create/Update**:
- `migrations/008_cross_school_access.sql` (new)
- `api/services/multi_school.py` (new)
- `api/routes/multi_school.py` (new)
- `webapp/src/components/SchoolSwitcher.tsx` (new)
- Update Parent Portal to show school selector

---

## 💡 IMPLEMENTATION PRIORITY

### **Priority 1: Cross-School Parent Access** (Most Requested)
**Why**: Many parents have children in different schools
**Impact**: HIGH - Increases platform stickiness
**Time**: 4-6 hours

### **Priority 2: Enhanced Role Switcher UI**
**Why**: Make it easier for multi-role users
**Impact**: MEDIUM - Better UX
**Time**: 2-3 hours

### **Priority 3: Global Search (Across Schools)**
**Why**: Parents/admins want to search across all their schools
**Impact**: MEDIUM - Nice to have
**Time**: 3-4 hours

---

## 📊 USE CASE EXAMPLES

### **Example 1: Mrs. Nakato (Multi-Child, Same School)**
```
School: Angels Primary
Children: Mary (5A), John (P3), Peter (Baby)

Mrs. Nakato opens app:
↓
Sees dashboard with all 3 children
Notification: "Mary marked present"
Clicks Mary → See Mary's full report
Clicks "Pay Fees" → Pays for all 3 at once
```

### **Example 2: Mr. Mukasa (Teacher + Inventory Manager)**
```
School: Angels Primary
Roles: Teacher (Science), Inventory Manager

Mr. Mukasa opens app:
↓
Morning: Teacher Mode
- Marks attendance for Class 5A
- Uploads exam results

Afternoon: Switches to Inventory Mode
- Records 50 test tubes used
- Orders new supplies
```

### **Example 3: Mrs. Nakato (Cross-School Parent)**
```
Schools: Angels Primary + St. Joseph Secondary
Children: Mary (Angels), John (St. Joseph)

Mrs. Nakato logs in:
↓
Sees school selector
Selects "All Schools" (combined view)
↓
Dashboard shows:
- Mary's data from Angels Primary
- John's data from St. Joseph
- Combined fee balance
- All notifications from both schools

OR

Selects specific school → See only that school's data
```

---

## ✅ SUMMARY

| Scenario | Status | Notes |
|----------|--------|-------|
| **Parent with multiple children (same school)** | ✅ WORKS NOW | Fully implemented |
| **Teacher with multiple roles** | ✅ WORKS NOW | user_links table supports it |
| **Parent with children in different schools** | 🔨 NEEDS 4-6 HOURS | Doable, just need to build UI + API |

**Recommendation**: 
- ✅ Scenarios 1 & 2 are production-ready
- 🔨 Scenario 3 needs 4-6 hours work (but the architecture supports it!)

---

**Want me to build the cross-school functionality now?** 🚀
