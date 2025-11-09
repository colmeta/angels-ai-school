-- Migration 010: Top 6 Critical Features
-- 1. USSD Support
-- 2. WhatsApp Integration
-- 3. Multi-Language
-- 4. UNEB Integration
-- 5. Sibling Discounts & Payment Plans
-- 6. Library Management

-- ============================================================================
-- 1. USSD SUPPORT (Basic Phone Access)
-- ============================================================================

-- USSD sessions (track user interactions)
CREATE TABLE IF NOT EXISTS ussd_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    current_menu VARCHAR(100),
    menu_history JSONB DEFAULT '[]'::jsonb,
    user_input TEXT,
    session_data JSONB DEFAULT '{}'::jsonb, -- Store context between requests
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'expired', 'error')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP + INTERVAL '5 minutes',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- USSD analytics (track usage)
CREATE TABLE IF NOT EXISTS ussd_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) REFERENCES ussd_sessions(session_id) ON DELETE CASCADE,
    phone_number VARCHAR(20),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    menu_accessed VARCHAR(100),
    action_taken VARCHAR(100),
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    duration_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 2. WHATSAPP INTEGRATION
-- ============================================================================

-- WhatsApp message queue
CREATE TABLE IF NOT EXISTS whatsapp_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    recipient_type VARCHAR(50) NOT NULL CHECK (recipient_type IN ('individual', 'group', 'broadcast')),
    recipient_phone VARCHAR(20) NOT NULL,
    recipient_name VARCHAR(255),
    message_type VARCHAR(50) NOT NULL CHECK (message_type IN ('text', 'image', 'document', 'template', 'interactive')),
    message_content TEXT NOT NULL,
    media_url TEXT,
    template_name VARCHAR(100),
    template_params JSONB,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'delivered', 'read', 'failed')),
    whatsapp_message_id VARCHAR(255),
    error_message TEXT,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- WhatsApp incoming messages (for chatbot)
CREATE TABLE IF NOT EXISTS whatsapp_incoming (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    sender_phone VARCHAR(20) NOT NULL,
    sender_name VARCHAR(255),
    message_type VARCHAR(50),
    message_content TEXT,
    media_url TEXT,
    whatsapp_message_id VARCHAR(255) UNIQUE,
    is_processed BOOLEAN DEFAULT false,
    processed_at TIMESTAMP WITH TIME ZONE,
    response_sent BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- WhatsApp templates (pre-approved messages)
CREATE TABLE IF NOT EXISTS whatsapp_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL CHECK (category IN ('attendance', 'fees', 'grades', 'general', 'emergency')),
    language VARCHAR(10) DEFAULT 'en',
    template_text TEXT NOT NULL,
    parameters JSONB DEFAULT '[]'::jsonb,
    is_approved BOOLEAN DEFAULT false,
    approved_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(school_id, name, language)
);

-- ============================================================================
-- 3. MULTI-LANGUAGE SUPPORT
-- ============================================================================

-- Language preferences
CREATE TABLE IF NOT EXISTS user_language_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    phone_number VARCHAR(20),
    preferred_language VARCHAR(10) NOT NULL DEFAULT 'en',
    auto_detect BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id),
    UNIQUE(phone_number)
);

-- Translation cache (avoid re-translating same content)
CREATE TABLE IF NOT EXISTS translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text_key VARCHAR(255) NOT NULL,
    source_language VARCHAR(10) NOT NULL DEFAULT 'en',
    target_language VARCHAR(10) NOT NULL,
    source_text TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    translation_service VARCHAR(50), -- google, clarity, manual
    confidence_score DECIMAL(3, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(text_key, source_language, target_language)
);

-- ============================================================================
-- 4. UNEB INTEGRATION (Uganda National Examinations Board)
-- ============================================================================

-- UNEB registration (candidate registration)
CREATE TABLE IF NOT EXISTS uneb_registrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    exam_type VARCHAR(50) NOT NULL CHECK (exam_type IN ('PLE', 'UCE', 'UACE')),
    exam_year INTEGER NOT NULL,
    index_number VARCHAR(50) UNIQUE,
    center_number VARCHAR(50),
    registration_date DATE,
    subjects JSONB NOT NULL, -- Array of subjects registered
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'registered', 'confirmed', 'cancelled')),
    submitted_to_uneb BOOLEAN DEFAULT false,
    submitted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- UNEB results (exam results from UNEB)
CREATE TABLE IF NOT EXISTS uneb_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    registration_id UUID REFERENCES uneb_registrations(id) ON DELETE CASCADE,
    exam_type VARCHAR(50) NOT NULL,
    exam_year INTEGER NOT NULL,
    index_number VARCHAR(50),
    subject_results JSONB NOT NULL, -- {subject: grade} e.g., {"English": "D1", "Math": "D2"}
    aggregate INTEGER, -- Total aggregate score
    division VARCHAR(20), -- Division 1, 2, 3, 4, or Fail
    distinction_count INTEGER DEFAULT 0,
    credit_count INTEGER DEFAULT 0,
    pass_count INTEGER DEFAULT 0,
    fail_count INTEGER DEFAULT 0,
    best_8_aggregate INTEGER, -- For UCE
    best_6_aggregate INTEGER, -- For UACE (2 principals + 4 subsidiaries)
    remarks TEXT,
    result_slip_url TEXT,
    imported_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, exam_type, exam_year)
);

-- UNEB grade mapping (D1, D2, C3, etc.)
CREATE TABLE IF NOT EXISTS uneb_grade_mapping (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_type VARCHAR(50) NOT NULL,
    grade VARCHAR(10) NOT NULL,
    min_marks INTEGER NOT NULL,
    max_marks INTEGER NOT NULL,
    points INTEGER NOT NULL, -- For aggregate calculation
    description VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(exam_type, grade)
);

-- ============================================================================
-- 5. SIBLING DISCOUNTS & PAYMENT PLANS
-- ============================================================================

-- Fee discount rules
CREATE TABLE IF NOT EXISTS fee_discount_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    rule_name VARCHAR(100) NOT NULL,
    discount_type VARCHAR(50) NOT NULL CHECK (discount_type IN ('sibling', 'early_payment', 'scholarship', 'staff_child', 'other')),
    calculation_method VARCHAR(50) NOT NULL CHECK (calculation_method IN ('percentage', 'fixed_amount')),
    discount_value DECIMAL(12, 2) NOT NULL,
    conditions JSONB, -- {child_position: 2, percentage: 10} for 2nd child gets 10%
    applicable_to VARCHAR(50) DEFAULT 'all' CHECK (applicable_to IN ('all', 'specific_class', 'specific_term')),
    target_class VARCHAR(50),
    term VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 1, -- If multiple discounts apply, which one first
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Student discounts applied
CREATE TABLE IF NOT EXISTS student_discounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    discount_rule_id UUID REFERENCES fee_discount_rules(id) ON DELETE CASCADE,
    fee_id UUID REFERENCES student_fees(id) ON DELETE CASCADE,
    discount_type VARCHAR(50),
    discount_amount DECIMAL(12, 2) NOT NULL,
    reason TEXT,
    applied_by UUID REFERENCES users(id),
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    term VARCHAR(20),
    academic_year VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Payment plans
CREATE TABLE IF NOT EXISTS payment_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES parents(id) ON DELETE CASCADE,
    total_amount DECIMAL(12, 2) NOT NULL,
    amount_paid DECIMAL(12, 2) DEFAULT 0,
    balance DECIMAL(12, 2) NOT NULL,
    installment_count INTEGER NOT NULL,
    installment_amount DECIMAL(12, 2) NOT NULL,
    installment_frequency VARCHAR(50) DEFAULT 'monthly' CHECK (installment_frequency IN ('weekly', 'bi-weekly', 'monthly', 'custom')),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'defaulted', 'cancelled')),
    auto_reminders BOOLEAN DEFAULT true,
    late_fee_amount DECIMAL(12, 2) DEFAULT 0,
    grace_period_days INTEGER DEFAULT 0,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Payment plan installments
CREATE TABLE IF NOT EXISTS payment_plan_installments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_plan_id UUID NOT NULL REFERENCES payment_plans(id) ON DELETE CASCADE,
    installment_number INTEGER NOT NULL,
    due_date DATE NOT NULL,
    amount_due DECIMAL(12, 2) NOT NULL,
    amount_paid DECIMAL(12, 2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'partial', 'overdue', 'waived')),
    paid_at TIMESTAMP WITH TIME ZONE,
    reminder_sent BOOLEAN DEFAULT false,
    reminder_sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(payment_plan_id, installment_number)
);

-- ============================================================================
-- 6. LIBRARY MANAGEMENT
-- ============================================================================

-- Books catalog
CREATE TABLE IF NOT EXISTS library_books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    isbn VARCHAR(20),
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255),
    publisher VARCHAR(255),
    publication_year INTEGER,
    category VARCHAR(100), -- Fiction, Science, History, etc.
    subject VARCHAR(100), -- Math, English, Biology, etc.
    language VARCHAR(50) DEFAULT 'English',
    total_copies INTEGER DEFAULT 1,
    available_copies INTEGER DEFAULT 1,
    borrowed_copies INTEGER DEFAULT 0,
    damaged_copies INTEGER DEFAULT 0,
    lost_copies INTEGER DEFAULT 0,
    location VARCHAR(100), -- Shelf/rack location
    purchase_date DATE,
    purchase_price DECIMAL(12, 2),
    condition VARCHAR(50) DEFAULT 'good' CHECK (condition IN ('excellent', 'good', 'fair', 'poor', 'damaged')),
    cover_image_url TEXT,
    description TEXT,
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Book borrowing transactions
CREATE TABLE IF NOT EXISTS library_borrowings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    book_id UUID NOT NULL REFERENCES library_books(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id) ON DELETE SET NULL,
    teacher_id UUID REFERENCES teachers(id) ON DELETE SET NULL,
    borrowed_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    return_date DATE,
    status VARCHAR(50) DEFAULT 'borrowed' CHECK (status IN ('borrowed', 'returned', 'overdue', 'lost', 'damaged')),
    condition_on_borrow VARCHAR(50),
    condition_on_return VARCHAR(50),
    fine_amount DECIMAL(12, 2) DEFAULT 0,
    fine_paid BOOLEAN DEFAULT false,
    fine_paid_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    issued_by UUID REFERENCES users(id),
    returned_to UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Library fines configuration
CREATE TABLE IF NOT EXISTS library_fine_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    rule_name VARCHAR(100),
    fine_type VARCHAR(50) NOT NULL CHECK (fine_type IN ('overdue', 'lost', 'damaged')),
    amount_per_day DECIMAL(12, 2), -- For overdue
    fixed_amount DECIMAL(12, 2), -- For lost/damaged
    grace_period_days INTEGER DEFAULT 0,
    max_fine_amount DECIMAL(12, 2),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- USSD
CREATE INDEX IF NOT EXISTS idx_ussd_sessions_phone ON ussd_sessions(phone_number);
CREATE INDEX IF NOT EXISTS idx_ussd_sessions_session_id ON ussd_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_ussd_sessions_status ON ussd_sessions(status);
CREATE INDEX IF NOT EXISTS idx_ussd_analytics_school ON ussd_analytics(school_id);

-- WhatsApp
CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_school ON whatsapp_messages(school_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_phone ON whatsapp_messages(recipient_phone);
CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_status ON whatsapp_messages(status);
CREATE INDEX IF NOT EXISTS idx_whatsapp_incoming_phone ON whatsapp_incoming(sender_phone);
CREATE INDEX IF NOT EXISTS idx_whatsapp_incoming_processed ON whatsapp_incoming(is_processed);

-- Multi-Language
CREATE INDEX IF NOT EXISTS idx_user_language_user ON user_language_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_language_phone ON user_language_preferences(phone_number);
CREATE INDEX IF NOT EXISTS idx_translations_key ON translations(text_key, target_language);

-- UNEB
CREATE INDEX IF NOT EXISTS idx_uneb_registrations_student ON uneb_registrations(student_id);
CREATE INDEX IF NOT EXISTS idx_uneb_registrations_school ON uneb_registrations(school_id);
CREATE INDEX IF NOT EXISTS idx_uneb_registrations_year ON uneb_registrations(exam_year);
CREATE INDEX IF NOT EXISTS idx_uneb_results_student ON uneb_results(student_id);
CREATE INDEX IF NOT EXISTS idx_uneb_results_index ON uneb_results(index_number);

-- Discounts & Payment Plans
CREATE INDEX IF NOT EXISTS idx_discount_rules_school ON fee_discount_rules(school_id);
CREATE INDEX IF NOT EXISTS idx_student_discounts_student ON student_discounts(student_id);
CREATE INDEX IF NOT EXISTS idx_payment_plans_student ON payment_plans(student_id);
CREATE INDEX IF NOT EXISTS idx_payment_plan_installments_plan ON payment_plan_installments(payment_plan_id);
CREATE INDEX IF NOT EXISTS idx_payment_plan_installments_due ON payment_plan_installments(due_date);

-- Library
CREATE INDEX IF NOT EXISTS idx_library_books_school ON library_books(school_id);
CREATE INDEX IF NOT EXISTS idx_library_books_title ON library_books(title);
CREATE INDEX IF NOT EXISTS idx_library_books_category ON library_books(category);
CREATE INDEX IF NOT EXISTS idx_library_borrowings_book ON library_borrowings(book_id);
CREATE INDEX IF NOT EXISTS idx_library_borrowings_student ON library_borrowings(student_id);
CREATE INDEX IF NOT EXISTS idx_library_borrowings_status ON library_borrowings(status);
CREATE INDEX IF NOT EXISTS idx_library_borrowings_due ON library_borrowings(due_date);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE TRIGGER update_whatsapp_messages_updated_at
    BEFORE UPDATE ON whatsapp_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_whatsapp_templates_updated_at
    BEFORE UPDATE ON whatsapp_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_language_preferences_updated_at
    BEFORE UPDATE ON user_language_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_uneb_registrations_updated_at
    BEFORE UPDATE ON uneb_registrations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fee_discount_rules_updated_at
    BEFORE UPDATE ON fee_discount_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payment_plans_updated_at
    BEFORE UPDATE ON payment_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payment_plan_installments_updated_at
    BEFORE UPDATE ON payment_plan_installments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_library_books_updated_at
    BEFORE UPDATE ON library_books
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_library_borrowings_updated_at
    BEFORE UPDATE ON library_borrowings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SEED DATA
-- ============================================================================

-- UNEB Grade Mapping (Standard grades)
INSERT INTO uneb_grade_mapping (exam_type, grade, min_marks, max_marks, points, description) VALUES
-- PLE Grades
('PLE', 'D1', 85, 100, 1, 'Distinction 1'),
('PLE', 'D2', 75, 84, 2, 'Distinction 2'),
('PLE', 'C3', 65, 74, 3, 'Credit 3'),
('PLE', 'C4', 55, 64, 4, 'Credit 4'),
('PLE', 'C5', 45, 54, 5, 'Credit 5'),
('PLE', 'C6', 35, 44, 6, 'Credit 6'),
('PLE', 'P7', 25, 34, 7, 'Pass 7'),
('PLE', 'P8', 20, 24, 8, 'Pass 8'),
('PLE', 'F9', 0, 19, 9, 'Fail 9'),

-- UCE/UACE Grades
('UCE', 'D1', 80, 100, 1, 'Distinction 1'),
('UCE', 'D2', 70, 79, 2, 'Distinction 2'),
('UCE', 'C3', 60, 69, 3, 'Credit 3'),
('UCE', 'C4', 50, 59, 4, 'Credit 4'),
('UCE', 'C5', 45, 49, 5, 'Credit 5'),
('UCE', 'C6', 40, 44, 6, 'Credit 6'),
('UCE', 'P7', 35, 39, 7, 'Pass 7'),
('UCE', 'P8', 30, 34, 8, 'Pass 8'),
('UCE', 'F9', 0, 29, 9, 'Fail 9'),

('UACE', 'A', 80, 100, 6, 'Principal Pass A'),
('UACE', 'B', 70, 79, 5, 'Principal Pass B'),
('UACE', 'C', 60, 69, 4, 'Principal Pass C'),
('UACE', 'D', 50, 59, 3, 'Principal Pass D'),
('UACE', 'E', 45, 49, 2, 'Principal Pass E'),
('UACE', 'O', 40, 44, 1, 'Subsidiary Pass O'),
('UACE', 'F', 0, 39, 0, 'Fail F')
ON CONFLICT (exam_type, grade) DO NOTHING;

-- Default library fine rules
INSERT INTO library_fine_rules (school_id, rule_name, fine_type, amount_per_day, fixed_amount, grace_period_days, max_fine_amount)
SELECT 
    id,
    'Overdue Book Fine',
    'overdue',
    500, -- 500 UGX per day
    NULL,
    3, -- 3 days grace period
    10000 -- Max 10,000 UGX
FROM schools
WHERE NOT EXISTS (
    SELECT 1 FROM library_fine_rules 
    WHERE school_id = schools.id AND fine_type = 'overdue'
);

INSERT INTO library_fine_rules (school_id, rule_name, fine_type, amount_per_day, fixed_amount)
SELECT 
    id,
    'Lost Book Fine',
    'lost',
    NULL,
    20000 -- 20,000 UGX flat fee
FROM schools
WHERE NOT EXISTS (
    SELECT 1 FROM library_fine_rules 
    WHERE school_id = schools.id AND fine_type = 'lost'
);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE ussd_sessions IS 'USSD sessions for basic phone access (*123# interface)';
COMMENT ON TABLE whatsapp_messages IS 'WhatsApp message queue for sending notifications';
COMMENT ON TABLE whatsapp_incoming IS 'Incoming WhatsApp messages for chatbot';
COMMENT ON TABLE user_language_preferences IS 'User language preferences (Luganda, Swahili, English)';
COMMENT ON TABLE translations IS 'Translation cache to avoid re-translating';
COMMENT ON TABLE uneb_registrations IS 'UNEB candidate registrations (PLE, UCE, UACE)';
COMMENT ON TABLE uneb_results IS 'UNEB examination results from national exams';
COMMENT ON TABLE fee_discount_rules IS 'Discount rules (sibling discounts, early payment, etc.)';
COMMENT ON TABLE payment_plans IS 'Fee payment plans (installments)';
COMMENT ON TABLE library_books IS 'School library book catalog';
COMMENT ON TABLE library_borrowings IS 'Book borrowing transactions';
