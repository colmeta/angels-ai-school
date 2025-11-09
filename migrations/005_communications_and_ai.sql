-- Communications and AI Agent Module
-- Messages, notifications, chatbot conversations, and AI agent tasks

-- Messages (parent-teacher communication)
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL, -- teacher, parent, admin, system
    sender_id UUID,
    recipient_type VARCHAR(20) NOT NULL,
    recipient_id UUID,
    student_id UUID REFERENCES students(id),
    subject VARCHAR(500),
    message_body TEXT NOT NULL,
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMP,
    parent_thread_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    recipient_type VARCHAR(20) NOT NULL, -- parent, teacher, admin, all_parents, all_teachers
    recipient_id UUID,
    notification_type VARCHAR(50) NOT NULL, -- attendance, fee, incident, health, transport, general
    title VARCHAR(500) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal', -- low, normal, high, urgent
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMP,
    related_entity_type VARCHAR(50),
    related_entity_id UUID,
    sent_via VARCHAR(50)[], -- app, sms, email
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chatbot conversations
CREATE TABLE IF NOT EXISTS chatbot_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    user_type VARCHAR(20) NOT NULL, -- parent, teacher, student
    user_id UUID,
    session_id UUID DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Chatbot messages
CREATE TABLE IF NOT EXISTS chatbot_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES chatbot_conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- user, assistant, system
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Agent tasks (for tracking agent work)
CREATE TABLE IF NOT EXISTS ai_agent_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL, -- ceo, command_intelligence, financial_ops, etc.
    task_type VARCHAR(100) NOT NULL,
    directive TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    input_data JSONB,
    output_data JSONB,
    clarity_task_id VARCHAR(255), -- Reference to Clarity API task
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Offline sync queue (for PWA offline operations)
CREATE TABLE IF NOT EXISTS offline_sync_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    user_id UUID,
    operation_type VARCHAR(50) NOT NULL, -- create, update, delete
    entity_type VARCHAR(50) NOT NULL, -- attendance, payment, incident, etc.
    payload JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, synced, failed
    retry_count INTEGER DEFAULT 0,
    last_retry_at TIMESTAMP,
    synced_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_messages_school ON messages(school_id, created_at);
CREATE INDEX idx_messages_recipient ON messages(recipient_type, recipient_id);
CREATE INDEX idx_messages_student ON messages(student_id);
CREATE INDEX idx_notifications_school ON notifications(school_id, created_at);
CREATE INDEX idx_notifications_recipient ON notifications(recipient_type, recipient_id);
CREATE INDEX idx_notifications_type ON notifications(notification_type);
CREATE INDEX idx_chatbot_conversations_school ON chatbot_conversations(school_id);
CREATE INDEX idx_chatbot_conversations_user ON chatbot_conversations(user_type, user_id);
CREATE INDEX idx_chatbot_messages_conversation ON chatbot_messages(conversation_id, created_at);
CREATE INDEX idx_ai_agent_tasks_school ON ai_agent_tasks(school_id, status);
CREATE INDEX idx_ai_agent_tasks_agent ON ai_agent_tasks(agent_name, created_at);
CREATE INDEX idx_offline_sync_queue_school ON offline_sync_queue(school_id, status);
CREATE INDEX idx_offline_sync_queue_user ON offline_sync_queue(user_id, created_at);

-- Update triggers
CREATE TRIGGER update_ai_agent_tasks_updated_at BEFORE UPDATE ON ai_agent_tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_offline_sync_queue_updated_at BEFORE UPDATE ON offline_sync_queue FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
