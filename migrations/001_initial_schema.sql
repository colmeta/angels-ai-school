-- Angels AI School Platform - Initial Database Schema
-- This creates all core tables for the complete educational revolution platform

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Schools table (multi-tenant support)
CREATE TABLE IF NOT EXISTS schools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    country VARCHAR(100) DEFAULT 'Uganda',
    region VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- School branding (white-label support)
CREATE TABLE IF NOT EXISTS school_branding (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    brand_name VARCHAR(255) NOT NULL,
    primary_color VARCHAR(7) DEFAULT '#0B69FF',
    accent_color VARCHAR(7) DEFAULT '#FFB400',
    logo_url TEXT,
    favicon_url TEXT,
    custom_css TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(school_id)
);

-- School feature flags (enable/disable features per school)
CREATE TABLE IF NOT EXISTS school_feature_flags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    enable_background_sync BOOLEAN DEFAULT true,
    enable_parent_chatbot BOOLEAN DEFAULT true,
    enable_mobile_money BOOLEAN DEFAULT true,
    enable_offline_mode BOOLEAN DEFAULT true,
    enable_ai_agents BOOLEAN DEFAULT true,
    enable_clarity_engine BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(school_id)
);

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    admission_number VARCHAR(50) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(20),
    class_name VARCHAR(50),
    section VARCHAR(50),
    roll_number VARCHAR(50),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    emergency_contact VARCHAR(255),
    medical_conditions TEXT,
    allergies TEXT,
    photo_url TEXT,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'active', -- active, suspended, graduated, transferred
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(school_id, admission_number)
);

-- Parents/Guardians table
CREATE TABLE IF NOT EXISTS parents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50) NOT NULL,
    alternate_phone VARCHAR(50),
    relationship VARCHAR(50), -- father, mother, guardian, sponsor
    occupation VARCHAR(100),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Student-Parent relationships (many-to-many)
CREATE TABLE IF NOT EXISTS student_parents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    parent_id UUID NOT NULL REFERENCES parents(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT false,
    can_pickup BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, parent_id)
);

-- Teachers table
CREATE TABLE IF NOT EXISTS teachers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    employee_id VARCHAR(50) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50) NOT NULL,
    subject_specialization TEXT[],
    qualification VARCHAR(255),
    hire_date DATE,
    status VARCHAR(20) DEFAULT 'active', -- active, on_leave, resigned, terminated
    photo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(school_id, employee_id)
);

-- Create indexes for better performance
CREATE INDEX idx_students_school ON students(school_id);
CREATE INDEX idx_students_admission ON students(school_id, admission_number);
CREATE INDEX idx_students_class ON students(school_id, class_name);
CREATE INDEX idx_parents_school ON parents(school_id);
CREATE INDEX idx_parents_phone ON parents(phone);
CREATE INDEX idx_teachers_school ON teachers(school_id);
CREATE INDEX idx_teachers_employee ON teachers(school_id, employee_id);

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers to all tables
CREATE TRIGGER update_schools_updated_at BEFORE UPDATE ON schools FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_school_branding_updated_at BEFORE UPDATE ON school_branding FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_school_feature_flags_updated_at BEFORE UPDATE ON school_feature_flags FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_students_updated_at BEFORE UPDATE ON students FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_parents_updated_at BEFORE UPDATE ON parents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_teachers_updated_at BEFORE UPDATE ON teachers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
