-- Migration 011: ALL 25 FEATURES FROM FIELD RESEARCH
-- Comprehensive school management for Uganda/Africa

-- ============================================================================
-- 5. SCHOOL TRANSPORT (NO GPS - just schedules/routes)
-- ============================================================================

CREATE TABLE IF NOT EXISTS transport_routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    route_name VARCHAR(100) NOT NULL,
    bus_number VARCHAR(50),
    driver_name VARCHAR(100),
    driver_phone VARCHAR(20),
    capacity INTEGER,
    pickup_time TIME,
    drop_off_time TIME,
    stops JSONB, -- [{name: "Shell Station", time: "06:45"}, ...]
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student_transport (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    route_id UUID NOT NULL REFERENCES transport_routes(id) ON DELETE CASCADE,
    pickup_stop VARCHAR(255),
    drop_off_stop VARCHAR(255),
    transport_fee DECIMAL(12, 2),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, route_id)
);

-- ============================================================================
-- 6. BOARDING SCHOOL MANAGEMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS dormitories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'mixed')),
    capacity INTEGER,
    occupied INTEGER DEFAULT 0,
    matron_id UUID REFERENCES teachers(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dormitory_beds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dormitory_id UUID NOT NULL REFERENCES dormitories(id) ON DELETE CASCADE,
    bed_number VARCHAR(50) NOT NULL,
    student_id UUID REFERENCES students(id) ON DELETE SET NULL,
    is_occupied BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(dormitory_id, bed_number)
);

CREATE TABLE IF NOT EXISTS boarding_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    item_name VARCHAR(100),
    quantity INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'brought' CHECK (status IN ('brought', 'pending', 'missing')),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS exeat_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    request_date DATE NOT NULL,
    return_date DATE NOT NULL,
    reason TEXT,
    approved BOOLEAN DEFAULT false,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 7. GOVERNMENT REPORTING (UPE/USE)
-- ============================================================================

CREATE TABLE IF NOT EXISTS government_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL CHECK (report_type IN ('enrollment', 'teacher_qualification', 'infrastructure', 'capitation')),
    quarter VARCHAR(10), -- Q1, Q2, Q3, Q4
    year INTEGER NOT NULL,
    data JSONB NOT NULL,
    submitted BOOLEAN DEFAULT false,
    submitted_at TIMESTAMP WITH TIME ZONE,
    submitted_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 8. HEALTH RECORDS & VACCINATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS student_health_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    blood_type VARCHAR(10),
    allergies TEXT,
    medical_conditions TEXT,
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relationship VARCHAR(50),
    doctor_name VARCHAR(100),
    doctor_phone VARCHAR(20),
    hospital_name VARCHAR(100),
    insurance_provider VARCHAR(100),
    insurance_number VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id)
);

CREATE TABLE IF NOT EXISTS vaccinations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    vaccine_name VARCHAR(100) NOT NULL,
    date_given DATE,
    due_date DATE,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'overdue')),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sick_bay_visits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    visit_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    symptoms TEXT,
    diagnosis TEXT,
    treatment TEXT,
    medication_given TEXT,
    nurse_notes TEXT,
    parent_notified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 9. SCHOOL FEEDING PROGRAM
-- ============================================================================

CREATE TABLE IF NOT EXISTS meal_menu (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    meal_type VARCHAR(50) CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    menu_items TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(school_id, date, meal_type)
);

CREATE TABLE IF NOT EXISTS meal_attendance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    meal_type VARCHAR(50),
    attended BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, date, meal_type)
);

-- ============================================================================
-- 10. SIBLING DISCOUNTS (already in 010, adding payment plan details)
-- ============================================================================
-- Already covered in migration 010

-- ============================================================================
-- 11. LIBRARY MANAGEMENT
-- ============================================================================
-- Already covered in migration 010

-- ============================================================================
-- 12. CANTEEN/TUCK SHOP
-- ============================================================================

CREATE TABLE IF NOT EXISTS canteen_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    item_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(12, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student_canteen_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    balance DECIMAL(12, 2) DEFAULT 0,
    daily_limit DECIMAL(12, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id)
);

CREATE TABLE IF NOT EXISTS canteen_purchases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    item_id UUID REFERENCES canteen_items(id),
    item_name VARCHAR(100),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(12, 2),
    total_amount DECIMAL(12, 2),
    purchase_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 13. STAFF PAYROLL
-- ============================================================================

CREATE TABLE IF NOT EXISTS staff_salaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    staff_id UUID REFERENCES teachers(id), -- Can be teacher or other staff
    staff_name VARCHAR(255),
    position VARCHAR(100),
    basic_salary DECIMAL(12, 2) NOT NULL,
    allowances JSONB, -- {housing: 50000, transport: 20000}
    deductions JSONB, -- {nssf: 5000, paye: 15000}
    net_salary DECIMAL(12, 2),
    payment_frequency VARCHAR(50) DEFAULT 'monthly',
    bank_name VARCHAR(100),
    bank_account VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payroll_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    staff_id UUID,
    month INTEGER,
    year INTEGER,
    gross_salary DECIMAL(12, 2),
    total_deductions DECIMAL(12, 2),
    net_salary DECIMAL(12, 2),
    payment_date DATE,
    payment_method VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 14. ALUMNI TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS alumni (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    graduation_year INTEGER,
    current_occupation VARCHAR(255),
    employer VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    willing_to_donate BOOLEAN DEFAULT false,
    willing_to_mentor BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 15. PTA MANAGEMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS pta_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES parents(id),
    position VARCHAR(100), -- Chairman, Secretary, Treasurer, Member
    elected_date DATE,
    term_end_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pta_meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    meeting_date TIMESTAMP WITH TIME ZONE NOT NULL,
    agenda TEXT,
    minutes TEXT,
    attendees JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 16. SCHOOL EVENTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS school_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    event_name VARCHAR(255) NOT NULL,
    event_type VARCHAR(50), -- sports_day, graduation, parents_day, etc.
    event_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    location VARCHAR(255),
    description TEXT,
    requires_rsvp BOOLEAN DEFAULT false,
    max_attendees INTEGER,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS event_rsvp (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES school_events(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES parents(id),
    student_id UUID REFERENCES students(id),
    attending BOOLEAN DEFAULT true,
    number_of_guests INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 17. DISCIPLINARY RECORDS
-- ============================================================================

CREATE TABLE IF NOT EXISTS disciplinary_incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    incident_date DATE NOT NULL,
    incident_type VARCHAR(100), -- late, fighting, bullying, etc.
    description TEXT NOT NULL,
    severity VARCHAR(50) CHECK (severity IN ('minor', 'moderate', 'severe')),
    action_taken TEXT,
    parent_notified BOOLEAN DEFAULT false,
    follow_up_required BOOLEAN DEFAULT false,
    reported_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS suspensions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    incident_id UUID REFERENCES disciplinary_incidents(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT,
    approved_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 18. HOMEWORK TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS homework_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    teacher_id UUID REFERENCES teachers(id),
    class_name VARCHAR(50) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE NOT NULL,
    max_marks DECIMAL(5, 2),
    assigned_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS homework_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID NOT NULL REFERENCES homework_assignments(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    submission_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    marks_obtained DECIMAL(5, 2),
    feedback TEXT,
    status VARCHAR(50) DEFAULT 'submitted' CHECK (status IN ('submitted', 'graded', 'late', 'missing')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 19. CLUBS & SOCIETIES
-- ============================================================================

CREATE TABLE IF NOT EXISTS clubs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    club_name VARCHAR(100) NOT NULL,
    club_type VARCHAR(50), -- debate, drama, science, sports
    patron_teacher_id UUID REFERENCES teachers(id),
    meeting_schedule TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS club_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    club_id UUID NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    position VARCHAR(50), -- member, leader, secretary
    joined_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(club_id, student_id)
);

-- ============================================================================
-- 20. SPECIAL NEEDS STUDENTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS special_needs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    disability_type VARCHAR(100), -- visual, hearing, physical, learning
    severity VARCHAR(50) CHECK (severity IN ('mild', 'moderate', 'severe')),
    accommodations_needed TEXT,
    support_services TEXT,
    iep_document_url TEXT, -- Individual Education Plan
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 21. BODA-BODA COORDINATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS approved_bodaboda_riders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    rider_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    motorcycle_plate VARCHAR(50),
    photo_url TEXT,
    national_id VARCHAR(50),
    police_clearance BOOLEAN DEFAULT false,
    is_approved BOOLEAN DEFAULT false,
    rating DECIMAL(2, 1), -- Average rating out of 5
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bodaboda_rides (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    rider_id UUID NOT NULL REFERENCES approved_bodaboda_riders(id),
    ride_date DATE NOT NULL,
    ride_type VARCHAR(50) CHECK (ride_type IN ('to_school', 'from_school')),
    pickup_time TIME,
    drop_time TIME,
    parent_confirmed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 22. SACCO INTEGRATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS sacco_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    sacco_name VARCHAR(100) NOT NULL,
    leader_name VARCHAR(100),
    leader_phone VARCHAR(20),
    member_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sacco_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    sacco_id UUID NOT NULL REFERENCES sacco_groups(id),
    payment_date DATE NOT NULL,
    total_amount DECIMAL(12, 2),
    students_covered JSONB, -- [student_ids]
    reference_number VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 23. COMPOUND SECURITY
-- ============================================================================

CREATE TABLE IF NOT EXISTS visitor_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    visitor_name VARCHAR(100) NOT NULL,
    visitor_phone VARCHAR(20),
    purpose TEXT,
    person_to_see VARCHAR(100),
    entry_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    exit_time TIMESTAMP WITH TIME ZONE,
    badge_number VARCHAR(50),
    recorded_by UUID REFERENCES users(id)
);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX idx_transport_routes_school ON transport_routes(school_id);
CREATE INDEX idx_student_transport_student ON student_transport(student_id);
CREATE INDEX idx_dormitories_school ON dormitories(school_id);
CREATE INDEX idx_dormitory_beds_student ON dormitory_beds(student_id);
CREATE INDEX idx_health_records_student ON student_health_records(student_id);
CREATE INDEX idx_vaccinations_student ON vaccinations(student_id);
CREATE INDEX idx_sick_bay_student ON sick_bay_visits(student_id);
CREATE INDEX idx_meal_attendance_student ON meal_attendance(student_id);
CREATE INDEX idx_canteen_purchases_student ON canteen_purchases(student_id);
CREATE INDEX idx_alumni_school ON alumni(school_id);
CREATE INDEX idx_events_school ON school_events(school_id);
CREATE INDEX idx_disciplinary_student ON disciplinary_incidents(student_id);
CREATE INDEX idx_homework_class ON homework_assignments(class_name);
CREATE INDEX idx_clubs_school ON clubs(school_id);
CREATE INDEX idx_special_needs_student ON special_needs(student_id);
CREATE INDEX idx_bodaboda_rides_student ON bodaboda_rides(student_id);
CREATE INDEX idx_visitor_log_school ON visitor_log(school_id);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE transport_routes IS 'School bus routes and schedules (no GPS tracking)';
COMMENT ON TABLE dormitories IS 'Boarding school dormitories';
COMMENT ON TABLE student_health_records IS 'Student health records and emergency contacts';
COMMENT ON TABLE meal_menu IS 'School feeding program menu';
COMMENT ON TABLE canteen_items IS 'Canteen/tuck shop items';
COMMENT ON TABLE staff_salaries IS 'Staff payroll information';
COMMENT ON TABLE alumni IS 'Alumni database';
COMMENT ON TABLE school_events IS 'School events calendar';
COMMENT ON TABLE disciplinary_incidents IS 'Student disciplinary records';
COMMENT ON TABLE homework_assignments IS 'Homework tracking';
COMMENT ON TABLE clubs IS 'School clubs and societies';
COMMENT ON TABLE special_needs IS 'Special needs students support';
COMMENT ON TABLE approved_bodaboda_riders IS 'Approved motorcycle taxi riders';
COMMENT ON TABLE sacco_groups IS 'SACCO groups for collective fee payment';
COMMENT ON TABLE visitor_log IS 'School compound visitor tracking';
