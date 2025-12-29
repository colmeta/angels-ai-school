-- Angels AI School - Dynamic Attendance Schema
-- Adds support for Subject-wise and Exam attendance with multimodal input tracking

-- Subject Attendance Table
CREATE TABLE IF NOT EXISTS subject_attendance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    subject VARCHAR(100) NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    teacher_id UUID REFERENCES teachers(id),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    start_time TIME DEFAULT CURRENT_TIME,
    status VARCHAR(20) NOT NULL, -- present, absent, late, excused, sickbay
    mode VARCHAR(20) NOT NULL, -- photo, text, voice, manual
    topic_covered TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(school_id, student_id, subject, date, start_time)
);

-- Exam Attendance Table
CREATE TABLE IF NOT EXISTS exam_attendance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    exam_name VARCHAR(100) NOT NULL, -- e.g. "Mid-Term 1 2024"
    subject VARCHAR(100) NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    supervisor_id UUID REFERENCES teachers(id),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) NOT NULL, -- sat_exam, absent, sickbay, expelled_from_exam
    mode VARCHAR(20) NOT NULL, -- photo, manual
    seat_number VARCHAR(20),
    booklet_number VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(school_id, student_id, exam_name, subject)
);

-- Indexes for performance
CREATE INDEX idx_subject_attendance_lookup ON subject_attendance(school_id, class_name, subject, date);
CREATE INDEX idx_subject_attendance_student ON subject_attendance(student_id);
CREATE INDEX idx_exam_attendance_lookup ON exam_attendance(school_id, exam_name, subject);
CREATE INDEX idx_exam_attendance_student ON exam_attendance(student_id);

-- Add update triggers
CREATE TRIGGER update_subject_attendance_updated_at BEFORE UPDATE ON subject_attendance FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_exam_attendance_updated_at BEFORE UPDATE ON exam_attendance FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
