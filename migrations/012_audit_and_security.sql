-- ============================================================================
-- MIGRATION 012: Audit Logging and Security Enhancements
-- Production security and compliance features
-- ============================================================================

-- 1. Audit Logs Table (Immutable Audit Trail)
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    school_id UUID NOT NULL,
    action VARCHAR(100) NOT NULL,  -- view, create, update, delete, login, export, etc.
    resource_type VARCHAR(50) NOT NULL,  -- student, fee, grade, user, etc.
    resource_id VARCHAR(255) NOT NULL,
    changes JSONB,  -- Before/after values for updates
    ip_address INET,
    user_agent TEXT,
    metadata JSONB,  -- Additional context
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast audit trail queries
CREATE INDEX IF NOT EXISTS idx_audit_user_time ON audit_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_school_time ON audit_logs(school_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action, created_at DESC);

-- Prevent updates/deletes on audit logs (immutable)
CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'Audit logs are immutable. Operation % not allowed.', TG_OP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_logs_immutable
BEFORE UPDATE OR DELETE ON audit_logs
FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();


-- 2. Session Management (Track Active Sessions)
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    school_id UUID NOT NULL,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    refresh_token VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    device_type VARCHAR(50),  -- mobile, desktop, tablet
    is_active BOOLEAN DEFAULT true,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_sessions_expiry ON user_sessions(expires_at) WHERE is_active = true;


-- 3. Rate Limiting Table (API Abuse Prevention)
CREATE TABLE IF NOT EXISTS rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identifier VARCHAR(255) NOT NULL,  -- user_id or ip_address
    endpoint VARCHAR(255) NOT NULL,
    request_count INTEGER DEFAULT 1,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    window_end TIMESTAMP WITH TIME ZONE NOT NULL,
    is_blocked BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rate_limit_identifier ON rate_limits(identifier, endpoint, window_end);


-- 4. Security Events Table (Failed Logins, Suspicious Activity)
CREATE TABLE IF NOT EXISTS security_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,  -- failed_login, suspicious_access, brute_force
    user_id UUID,
    school_id UUID,
    ip_address INET,
    user_agent TEXT,
    severity VARCHAR(20) NOT NULL,  -- low, medium, high, critical
    description TEXT,
    metadata JSONB,
    resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_security_events_type ON security_events(event_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_security_events_unresolved ON security_events(resolved, severity) WHERE resolved = false;


-- 5. Data Access Log (Who Viewed What Student Data - GDPR)
CREATE TABLE IF NOT EXISTS data_access_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    school_id UUID NOT NULL,
    student_id UUID NOT NULL,
    access_type VARCHAR(50) NOT NULL,  -- view_profile, view_grades, view_health, etc.
    reason TEXT,  -- Why they accessed (for compliance)
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_data_access_student ON data_access_log(student_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_data_access_user ON data_access_log(user_id, created_at DESC);


-- 6. Function: Auto-cleanup old audit logs (retention policy)
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs()
RETURNS void AS $$
BEGIN
    -- Keep audit logs for 2 years (compliance requirement)
    DELETE FROM audit_logs 
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '2 years';
    
    -- Archive older logs if needed
    -- INSERT INTO audit_logs_archive SELECT * FROM audit_logs WHERE ...
END;
$$ LANGUAGE plpgsql;


-- 7. Function: Auto-cleanup expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    UPDATE user_sessions 
    SET is_active = false
    WHERE expires_at < CURRENT_TIMESTAMP 
    AND is_active = true;
    
    -- Delete very old sessions (> 90 days)
    DELETE FROM user_sessions
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;


-- 8. Views for Security Monitoring
CREATE OR REPLACE VIEW security_dashboard AS
SELECT 
    school_id,
    COUNT(DISTINCT user_id) as active_users_today,
    COUNT(*) FILTER (WHERE action = 'login_success') as successful_logins,
    COUNT(*) FILTER (WHERE action = 'login_failed') as failed_logins,
    COUNT(*) FILTER (WHERE action = 'export') as data_exports,
    COUNT(*) FILTER (WHERE action IN ('update', 'delete')) as modifications
FROM audit_logs
WHERE created_at >= CURRENT_DATE
GROUP BY school_id;


CREATE OR REPLACE VIEW suspicious_activity_summary AS
SELECT 
    user_id,
    school_id,
    COUNT(*) as failed_login_count,
    MAX(created_at) as last_attempt,
    ARRAY_AGG(DISTINCT ip_address::TEXT) as ip_addresses
FROM audit_logs
WHERE action = 'login_failed'
AND created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY user_id, school_id
HAVING COUNT(*) >= 5;


-- 9. Grants
GRANT SELECT ON audit_logs TO PUBLIC;  -- Read-only for all users
GRANT SELECT ON security_dashboard TO PUBLIC;
GRANT SELECT ON suspicious_activity_summary TO PUBLIC;

-- Comments
COMMENT ON TABLE audit_logs IS 'Immutable audit trail for all sensitive operations';
COMMENT ON TABLE user_sessions IS 'Active user sessions for session management';
COMMENT ON TABLE rate_limits IS 'Rate limiting data for API abuse prevention';
COMMENT ON TABLE security_events IS 'Security incidents and suspicious activity';
COMMENT ON TABLE data_access_log IS 'GDPR-compliant log of student data access';

-- Done!
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 012 complete: Audit logging and security enhancements';
END $$;
