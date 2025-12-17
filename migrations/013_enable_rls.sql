-- ============================================================================
-- 13. ENABLE ROW LEVEL SECURITY (RLS) - "The Vault"
-- ============================================================================

-- Function to get current user's school_id
CREATE OR REPLACE FUNCTION get_user_school_id()
RETURNS UUID AS $$
BEGIN
  RETURN (
    SELECT school_id 
    FROM user_session_access -- Assuming this view or table holds the active session context
    WHERE user_id = auth.uid() 
    LIMIT 1
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 1. Enable RLS on Tables
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE teachers ENABLE ROW LEVEL SECURITY;
ALTER TABLE parents ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance ENABLE ROW LEVEL SECURITY;
ALTER TABLE grades ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 2. Create Isolation Policies
-- "Users can only see students in their own school"

CREATE POLICY "Isolate Students" ON students
    USING (school_id IN (
        SELECT school_id FROM user_schools WHERE user_id = auth.uid()
    ));

CREATE POLICY "Isolate Teachers" ON teachers
    USING (school_id IN (
        SELECT school_id FROM user_schools WHERE user_id = auth.uid()
    ));

CREATE POLICY "Isolate Parents" ON parents
    USING (school_id IN (
        SELECT school_id FROM user_schools WHERE user_id = auth.uid()
    ));

CREATE POLICY "Isolate Attendance" ON attendance
    USING (school_id IN (
        SELECT school_id FROM user_schools WHERE user_id = auth.uid()
    ));

CREATE POLICY "Isolate Grades" ON grades
    USING (school_id IN (
        SELECT school_id FROM user_schools WHERE user_id = auth.uid()
    ));

CREATE POLICY "Isolate Payments" ON payments
    USING (school_id IN (
        SELECT school_id FROM user_schools WHERE user_id = auth.uid()
    ));

CREATE POLICY "Isolate Messages" ON messages
    USING (school_id IN (
        SELECT school_id FROM user_schools WHERE user_id = auth.uid()
    ));

-- 3. Universal "Root" Access for Super Admins (Optional but smart)
-- (Omitted for strict security unless explicitly requested)

DO $$
BEGIN
    RAISE NOTICE '✅ RLS Enabled. School isolation active.';
END $$;
