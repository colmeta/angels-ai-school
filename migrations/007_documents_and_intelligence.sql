-- Migration 007: Document Intelligence & Professional Analysis Support
-- Enables universal document processing and McKinsey-level business intelligence

-- Documents table: Store all uploaded documents with AI-extracted data
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    document_type VARCHAR(100),
    extracted_data JSONB,
    raw_text TEXT,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    uploaded_by UUID REFERENCES users(id),
    confidence_score DECIMAL(3, 2),  -- AI confidence (0.00-1.00)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Intelligence reports table: Store professional analysis reports
CREATE TABLE IF NOT EXISTS intelligence_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    report_type VARCHAR(100) NOT NULL,  -- legal, financial, security, etc.
    domain VARCHAR(50) NOT NULL,  -- Clarity domain used
    analysis JSONB NOT NULL,
    generated_by UUID REFERENCES users(id),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,  -- For time-sensitive reports
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Data migration logs: Track all data imports
CREATE TABLE IF NOT EXISTS migration_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    source_filename VARCHAR(255),
    data_type VARCHAR(100),  -- students, payments, grades, etc.
    records_imported INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    mapping_used JSONB,
    errors JSONB,
    imported_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_documents_school ON documents(school_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_date ON documents(processed_at);
CREATE INDEX idx_documents_uploaded_by ON documents(uploaded_by);

CREATE INDEX idx_intelligence_school ON intelligence_reports(school_id);
CREATE INDEX idx_intelligence_type ON intelligence_reports(report_type);
CREATE INDEX idx_intelligence_domain ON intelligence_reports(domain);
CREATE INDEX idx_intelligence_date ON intelligence_reports(generated_at);

CREATE INDEX idx_migration_school ON migration_logs(school_id);
CREATE INDEX idx_migration_type ON migration_logs(data_type);
CREATE INDEX idx_migration_date ON migration_logs(created_at);

-- Updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add AI analysis fields to existing tables for enhanced insights
ALTER TABLE students ADD COLUMN IF NOT EXISTS ai_risk_score DECIMAL(3, 2);  -- Dropout risk
ALTER TABLE students ADD COLUMN IF NOT EXISTS ai_performance_trend VARCHAR(50);  -- improving/stable/declining

ALTER TABLE expenses ADD COLUMN IF NOT EXISTS ai_category_confidence DECIMAL(3, 2);
ALTER TABLE expenses ADD COLUMN IF NOT EXISTS ai_anomaly_flag BOOLEAN DEFAULT FALSE;

-- Comments
COMMENT ON TABLE documents IS 'Universal document storage with AI-extracted data';
COMMENT ON TABLE intelligence_reports IS 'Professional analysis reports across all domains';
COMMENT ON TABLE migration_logs IS 'Audit trail for all data imports';

COMMENT ON COLUMN documents.confidence_score IS 'AI confidence in data extraction (0.00-1.00)';
COMMENT ON COLUMN intelligence_reports.domain IS 'Clarity domain: legal, financial, security, healthcare, data-science, education, proposals, ngo, expenses';
COMMENT ON COLUMN migration_logs.mapping_used IS 'Field mapping used for import';
