-- ============================================================================
-- DATABASE BACKUP SETUP FOR PRODUCTION
-- Run this on your Render PostgreSQL database
-- ============================================================================

-- 1. Enable Point-in-Time Recovery (PITR)
-- This is handled by Render PostgreSQL automatically on paid plans
-- Free tier: Manual backups only

-- 2. Create backup user with read-only access
CREATE USER backup_user WITH PASSWORD 'CHANGE_THIS_BACKUP_PASSWORD';
GRANT CONNECT ON DATABASE angels_ai_school TO backup_user;
GRANT USAGE ON SCHEMA public TO backup_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO backup_user;

-- 3. Create backup log table
CREATE TABLE IF NOT EXISTS backup_logs (
    id SERIAL PRIMARY KEY,
    backup_type VARCHAR(50) NOT NULL,  -- manual, automated, pitr
    backup_size_mb DECIMAL(10, 2),
    backup_duration_seconds INTEGER,
    backup_status VARCHAR(20) NOT NULL,  -- success, failed, in_progress
    backup_location TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_by VARCHAR(100) DEFAULT 'system'
);

-- 4. Create function to log backups
CREATE OR REPLACE FUNCTION log_backup(
    p_backup_type VARCHAR,
    p_backup_status VARCHAR,
    p_backup_size_mb DECIMAL DEFAULT NULL,
    p_backup_duration INTEGER DEFAULT NULL,
    p_backup_location TEXT DEFAULT NULL,
    p_error_message TEXT DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    backup_id INTEGER;
BEGIN
    INSERT INTO backup_logs (
        backup_type, backup_status, backup_size_mb,
        backup_duration_seconds, backup_location, error_message,
        completed_at
    ) VALUES (
        p_backup_type, p_backup_status, p_backup_size_mb,
        p_backup_duration, p_backup_location, p_error_message,
        CASE WHEN p_backup_status != 'in_progress' THEN CURRENT_TIMESTAMP END
    ) RETURNING id INTO backup_id;
    
    RETURN backup_id;
END;
$$ LANGUAGE plpgsql;

-- 5. Create view for backup monitoring
CREATE OR REPLACE VIEW backup_status AS
SELECT 
    backup_type,
    COUNT(*) as total_backups,
    SUM(CASE WHEN backup_status = 'success' THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN backup_status = 'failed' THEN 1 ELSE 0 END) as failed,
    MAX(completed_at) as last_backup,
    AVG(backup_size_mb) as avg_size_mb,
    AVG(backup_duration_seconds) as avg_duration_seconds
FROM backup_logs
WHERE completed_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY backup_type;

-- 6. Grant permissions
GRANT SELECT ON backup_logs TO backup_user;
GRANT SELECT ON backup_status TO backup_user;

COMMENT ON TABLE backup_logs IS 'Tracks all database backup operations';
COMMENT ON VIEW backup_status IS 'Summary of backup health and status';
