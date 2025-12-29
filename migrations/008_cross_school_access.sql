-- Migration 008: Cross-School Access for Parents and Multi-Role Users
-- Enables users to access multiple schools with one account

-- User school access table (links users to multiple schools)
CREATE TABLE IF NOT EXISTS user_school_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('parent', 'teacher', 'admin', 'staff', 'student')),
    is_active BOOLEAN DEFAULT true,
    access_granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    access_granted_by UUID REFERENCES users(id),
    last_accessed TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, school_id, role)
);

-- Parent-child relationships across schools (global view)
CREATE TABLE IF NOT EXISTS parent_children_global (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    child_student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    relationship VARCHAR(50) NOT NULL, -- father, mother, guardian, sponsor
    is_primary BOOLEAN DEFAULT false,
    can_pickup BOOLEAN DEFAULT true,
    can_view_grades BOOLEAN DEFAULT true,
    can_pay_fees BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(parent_user_id, child_student_id)
);

-- User preferences (school selection, default school, etc.)
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    default_school_id UUID REFERENCES schools(id),
    preferred_language VARCHAR(10) DEFAULT 'en',
    notification_preferences JSONB DEFAULT '{
        "email": true,
        "sms": true,
        "push": true,
        "attendance": true,
        "grades": true,
        "fees": true,
        "announcements": true
    }'::jsonb,
    ui_preferences JSONB DEFAULT '{
        "theme": "light",
        "compact_view": false,
        "show_all_schools": false
    }'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Cross-school notifications aggregation view
CREATE OR REPLACE VIEW user_schools_summary AS
SELECT 
    u.id as user_id,
    u.email,
    u.first_name,
    u.last_name,
    COUNT(DISTINCT usa.school_id) as total_schools,
    json_agg(DISTINCT jsonb_build_object(
        'school_id', s.id,
        'school_name', s.name,
        'role', usa.role,
        'is_active', usa.is_active,
        'last_accessed', usa.last_accessed
    )) as schools
FROM users u
LEFT JOIN user_school_access usa ON usa.user_id = u.id
LEFT JOIN schools s ON s.id = usa.school_id
WHERE usa.is_active = true
GROUP BY u.id, u.email, u.first_name, u.last_name;

-- Indexes for performance
CREATE INDEX idx_user_school_access_user ON user_school_access(user_id);
CREATE INDEX idx_user_school_access_school ON user_school_access(school_id);
CREATE INDEX idx_user_school_access_active ON user_school_access(user_id, is_active);
CREATE INDEX idx_parent_children_global_parent ON parent_children_global(parent_user_id);
CREATE INDEX idx_parent_children_global_child ON parent_children_global(child_student_id);
CREATE INDEX idx_parent_children_global_school ON parent_children_global(school_id);
CREATE INDEX idx_user_preferences_user ON user_preferences(user_id);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_school_access_updated_at
    BEFORE UPDATE ON user_school_access
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_parent_children_global_updated_at
    BEFORE UPDATE ON parent_children_global
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE user_school_access IS 'Enables users to access multiple schools with one account';
COMMENT ON TABLE parent_children_global IS 'Links parents to children across different schools';
COMMENT ON TABLE user_preferences IS 'User preferences including default school selection';
COMMENT ON VIEW user_schools_summary IS 'Summary view of all schools a user has access to';

-- Migration to link existing parents to user_school_access
-- This ensures backward compatibility with existing data
DO $$
DECLARE
    parent_record RECORD;
    user_record RECORD;
BEGIN
    -- For each existing parent, create user_school_access if they have a user account
    FOR parent_record IN 
        SELECT DISTINCT p.id as parent_id, p.school_id, u.id as user_id
        FROM parents p
        JOIN users u ON u.email = p.email
    LOOP
        -- Insert into user_school_access if not exists
        INSERT INTO user_school_access (user_id, school_id, role, is_active)
        VALUES (parent_record.user_id, parent_record.school_id, 'parent', true)
        ON CONFLICT (user_id, school_id, role) DO NOTHING;
        
        -- Migrate existing student-parent relationships to global table
        INSERT INTO parent_children_global (
            parent_user_id, child_student_id, school_id, 
            relationship, is_primary, can_pickup
        )
        SELECT 
            parent_record.user_id,
            sp.student_id,
            parent_record.school_id,
            COALESCE(sp.relationship, 'parent'),
            sp.is_primary,
            sp.can_pickup
        FROM student_parents sp
        WHERE sp.parent_id = parent_record.parent_id
        ON CONFLICT (parent_user_id, child_student_id) DO NOTHING;
    END LOOP;
END $$;

-- Create default preferences for existing users
INSERT INTO user_preferences (user_id, default_school_id)
SELECT 
    u.id,
    (SELECT school_id FROM user_school_access WHERE user_id = u.id LIMIT 1)
FROM users u
WHERE NOT EXISTS (SELECT 1 FROM user_preferences WHERE user_id = u.id)
ON CONFLICT (user_id) DO NOTHING;
