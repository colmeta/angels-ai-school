-- Migration 009: School Requirements & Multi-Role Enhancements
-- Tracks school supplies (toilet paper, brooms, etc.) brought by students
-- Tracks trip fees, exam fees, and other non-tuition fees
-- Enhances multi-role support (teacher + parent)

-- ============================================================================
-- SCHOOL REQUIREMENTS TRACKING
-- ============================================================================

-- Requirement categories (supplies, trips, events, exams, etc.)
CREATE TABLE IF NOT EXISTS requirement_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL, -- Supplies, Trip Fees, Exam Fees, Events
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(school_id, name)
);

-- School requirements (items/fees required from students)
CREATE TABLE IF NOT EXISTS school_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    category_id UUID REFERENCES requirement_categories(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL, -- Toilet Paper, Broom, Trip to Museum, Exam Fee
    description TEXT,
    requirement_type VARCHAR(50) NOT NULL CHECK (requirement_type IN ('supply', 'fee', 'both')),
    
    -- For supplies (quantity-based)
    quantity_required INTEGER, -- e.g., 2 rolls of toilet paper
    unit VARCHAR(50), -- rolls, pieces, bars, bottles
    
    -- For fees (monetary)
    amount_required DECIMAL(12, 2), -- e.g., 20,000 UGX for trip
    currency VARCHAR(10) DEFAULT 'UGX',
    
    -- Targeting
    applies_to VARCHAR(50) NOT NULL CHECK (applies_to IN ('all_students', 'specific_class', 'specific_students')),
    target_class VARCHAR(50), -- If applies_to = 'specific_class'
    
    -- Timing
    due_date DATE,
    term VARCHAR(20), -- Term 1, Term 2, Term 3
    academic_year VARCHAR(20),
    
    -- Status
    is_mandatory BOOLEAN DEFAULT true,
    is_active BOOLEAN DEFAULT true,
    
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Student requirement submissions (what each student brought/paid)
CREATE TABLE IF NOT EXISTS student_requirement_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    requirement_id UUID NOT NULL REFERENCES school_requirements(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    
    -- For supplies
    quantity_submitted INTEGER,
    submission_date DATE,
    condition VARCHAR(50), -- new, used, acceptable, poor
    
    -- For fees
    amount_paid DECIMAL(12, 2),
    payment_method VARCHAR(50), -- cash, mobile_money, bank_transfer
    payment_reference VARCHAR(255),
    payment_date DATE,
    
    -- Verification
    verified BOOLEAN DEFAULT false,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMP WITH TIME ZONE,
    
    -- Notes
    notes TEXT,
    photo_url TEXT, -- Photo of item brought (for verification)
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(requirement_id, student_id)
);

-- Requirement reminders and notifications
CREATE TABLE IF NOT EXISTS requirement_reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    requirement_id UUID NOT NULL REFERENCES school_requirements(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id) ON DELETE CASCADE, -- NULL = all students
    reminder_type VARCHAR(50) NOT NULL CHECK (reminder_type IN ('initial', 'reminder', 'final', 'overdue')),
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sent_via VARCHAR(50), -- sms, email, app, whatsapp
    status VARCHAR(50) DEFAULT 'sent' CHECK (status IN ('sent', 'delivered', 'failed', 'read')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MULTI-ROLE ENHANCEMENTS (Teacher + Parent)
-- ============================================================================

-- User role preferences (which role to show by default at a school)
CREATE TABLE IF NOT EXISTS user_role_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    preferred_role VARCHAR(50) NOT NULL CHECK (preferred_role IN ('teacher', 'parent', 'admin', 'staff', 'student')),
    last_used_role VARCHAR(50),
    role_switch_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, school_id)
);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Requirements completion summary
CREATE OR REPLACE VIEW requirement_completion_summary AS
SELECT 
    sr.id as requirement_id,
    sr.school_id,
    sr.name as requirement_name,
    sr.requirement_type,
    sr.due_date,
    COUNT(DISTINCT s.id) as total_students,
    COUNT(DISTINCT srs.student_id) as submitted_count,
    COUNT(DISTINCT s.id) - COUNT(DISTINCT srs.student_id) as pending_count,
    ROUND(
        (COUNT(DISTINCT srs.student_id)::DECIMAL / NULLIF(COUNT(DISTINCT s.id), 0)) * 100, 
        2
    ) as completion_percentage
FROM school_requirements sr
LEFT JOIN students s ON (
    s.school_id = sr.school_id 
    AND s.status = 'active'
    AND (
        sr.applies_to = 'all_students' 
        OR (sr.applies_to = 'specific_class' AND s.class_name = sr.target_class)
    )
)
LEFT JOIN student_requirement_submissions srs ON (
    srs.requirement_id = sr.id 
    AND srs.student_id = s.id
    AND (srs.verified = true OR sr.requirement_type = 'fee')
)
WHERE sr.is_active = true
GROUP BY sr.id, sr.school_id, sr.name, sr.requirement_type, sr.due_date;

-- View: Student requirements status
CREATE OR REPLACE VIEW student_requirements_status AS
SELECT 
    s.id as student_id,
    s.first_name,
    s.last_name,
    s.class_name,
    s.school_id,
    sr.id as requirement_id,
    sr.name as requirement_name,
    sr.requirement_type,
    sr.due_date,
    sr.is_mandatory,
    CASE 
        WHEN srs.id IS NOT NULL THEN 'submitted'
        WHEN sr.due_date < CURRENT_DATE THEN 'overdue'
        WHEN sr.due_date >= CURRENT_DATE THEN 'pending'
        ELSE 'pending'
    END as status,
    srs.quantity_submitted,
    srs.amount_paid,
    srs.verified
FROM students s
CROSS JOIN school_requirements sr
LEFT JOIN student_requirement_submissions srs ON (
    srs.requirement_id = sr.id 
    AND srs.student_id = s.id
)
WHERE 
    s.status = 'active'
    AND sr.is_active = true
    AND sr.school_id = s.school_id
    AND (
        sr.applies_to = 'all_students' 
        OR (sr.applies_to = 'specific_class' AND s.class_name = sr.target_class)
    );

-- View: User roles at school (for multi-role switching)
CREATE OR REPLACE VIEW user_roles_at_school AS
SELECT 
    u.id as user_id,
    u.email,
    u.first_name,
    u.last_name,
    usa.school_id,
    s.name as school_name,
    array_agg(DISTINCT usa.role) as roles,
    COUNT(DISTINCT usa.role) as role_count
FROM users u
JOIN user_school_access usa ON usa.user_id = u.id
JOIN schools s ON s.id = usa.school_id
WHERE usa.is_active = true
GROUP BY u.id, u.email, u.first_name, u.last_name, usa.school_id, s.name;

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_requirement_categories_school ON requirement_categories(school_id);
CREATE INDEX IF NOT EXISTS idx_school_requirements_school ON school_requirements(school_id);
CREATE INDEX IF NOT EXISTS idx_school_requirements_category ON school_requirements(category_id);
CREATE INDEX IF NOT EXISTS idx_school_requirements_type ON school_requirements(requirement_type);
CREATE INDEX IF NOT EXISTS idx_school_requirements_class ON school_requirements(target_class);
CREATE INDEX IF NOT EXISTS idx_student_submissions_requirement ON student_requirement_submissions(requirement_id);
CREATE INDEX IF NOT EXISTS idx_student_submissions_student ON student_requirement_submissions(student_id);
CREATE INDEX IF NOT EXISTS idx_student_submissions_verified ON student_requirement_submissions(verified);
CREATE INDEX IF NOT EXISTS idx_requirement_reminders_requirement ON requirement_reminders(requirement_id);
CREATE INDEX IF NOT EXISTS idx_requirement_reminders_student ON requirement_reminders(student_id);
CREATE INDEX IF NOT EXISTS idx_user_role_preferences_user_school ON user_role_preferences(user_id, school_id);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE TRIGGER update_requirement_categories_updated_at
    BEFORE UPDATE ON requirement_categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_school_requirements_updated_at
    BEFORE UPDATE ON school_requirements
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_student_requirement_submissions_updated_at
    BEFORE UPDATE ON student_requirement_submissions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_role_preferences_updated_at
    BEFORE UPDATE ON user_role_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SEED DATA (Example Categories)
-- ============================================================================

INSERT INTO requirement_categories (school_id, name, description)
SELECT id, 'Supplies', 'School supplies and cleaning materials'
FROM schools
WHERE NOT EXISTS (
    SELECT 1 FROM requirement_categories 
    WHERE school_id = schools.id AND name = 'Supplies'
)
ON CONFLICT (school_id, name) DO NOTHING;

INSERT INTO requirement_categories (school_id, name, description)
SELECT id, 'Trip Fees', 'Educational trips and excursions'
FROM schools
WHERE NOT EXISTS (
    SELECT 1 FROM requirement_categories 
    WHERE school_id = schools.id AND name = 'Trip Fees'
)
ON CONFLICT (school_id, name) DO NOTHING;

INSERT INTO requirement_categories (school_id, name, description)
SELECT id, 'Exam Fees', 'Examination and assessment fees'
FROM schools
WHERE NOT EXISTS (
    SELECT 1 FROM requirement_categories 
    WHERE school_id = schools.id AND name = 'Exam Fees'
)
ON CONFLICT (school_id, name) DO NOTHING;

INSERT INTO requirement_categories (school_id, name, description)
SELECT id, 'Events', 'Sports day, concerts, and other events'
FROM schools
WHERE NOT EXISTS (
    SELECT 1 FROM requirement_categories 
    WHERE school_id = schools.id AND name = 'Events'
)
ON CONFLICT (school_id, name) DO NOTHING;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE requirement_categories IS 'Categories of school requirements (Supplies, Trip Fees, etc.)';
COMMENT ON TABLE school_requirements IS 'Items or fees required from students (toilet paper, brooms, trip fees, etc.)';
COMMENT ON TABLE student_requirement_submissions IS 'Records what each student brought or paid';
COMMENT ON TABLE requirement_reminders IS 'Tracks reminders sent to parents about requirements';
COMMENT ON TABLE user_role_preferences IS 'User preferences for multi-role switching (teacher + parent)';
COMMENT ON VIEW requirement_completion_summary IS 'Summary of requirement completion rates';
COMMENT ON VIEW student_requirements_status IS 'Status of each student for each requirement';
COMMENT ON VIEW user_roles_at_school IS 'All roles a user has at each school';
