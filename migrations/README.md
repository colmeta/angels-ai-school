# Database Migrations

This directory contains SQL migration files for the Angels AI School Platform.

## Migration Order

Run these files in sequence:

1. **001_initial_schema.sql** - Core tables (schools, students, parents, teachers, branding, feature flags)
2. **002_academic_operations.sql** - Academic tables (attendance, assessments, timetable)
3. **003_financial_operations.sql** - Financial tables (fees, payments, mobile money, expenses, budgets)
4. **004_support_operations.sql** - Support tables (incidents, inventory, health, library, transport)
5. **005_communications_and_ai.sql** - Communication tables (messages, notifications, chatbot, AI agent tasks, offline sync)

## Running Migrations

### Using psql command line:
```bash
psql $DATABASE_URL -f migrations/001_initial_schema.sql
psql $DATABASE_URL -f migrations/002_academic_operations.sql
psql $DATABASE_URL -f migrations/003_financial_operations.sql
psql $DATABASE_URL -f migrations/004_support_operations.sql
psql $DATABASE_URL -f migrations/005_communications_and_ai.sql
```

### Using Python:
```python
import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

migrations = [
    '001_initial_schema.sql',
    '002_academic_operations.sql',
    '003_financial_operations.sql',
    '004_support_operations.sql',
    '005_communications_and_ai.sql'
]

for migration_file in migrations:
    with open(f'migrations/{migration_file}', 'r') as f:
        sql = f.read()
        cur.execute(sql)
        conn.commit()
        print(f'✅ Applied {migration_file}')

cur.close()
conn.close()
```

### Using the provided script:
```bash
python run_migrations.py
```

## Database Structure

The database follows a multi-tenant architecture where each school is isolated by `school_id`.

### Key Features:
- **Multi-tenancy**: All tables include `school_id` for data isolation
- **White-labeling**: `school_branding` table for custom branding per school
- **Feature Flags**: `school_feature_flags` for enabling/disabling features per school
- **Offline Support**: `offline_sync_queue` table for PWA offline operations
- **AI Integration**: `ai_agent_tasks` table for tracking Clarity Engine operations
- **Mobile Money**: Full support for MTN and Airtel Mobile Money transactions

### Relationships:
- Students can have multiple parents/guardians (many-to-many)
- All academic, financial, and support operations are linked to students and schools
- Messages and notifications support parent-teacher communication
- Transport routes track student pickup/dropoff
- Library system supports both students and teachers

## Indexes

All tables include appropriate indexes for:
- School-based queries (multi-tenancy)
- Date-based filtering
- Foreign key relationships
- Status-based filtering

## Triggers

All major tables include `updated_at` triggers that automatically update timestamps on row modifications.
