-- Academic Operations Module
-- Attendance, assessments, and academic performance tracking

-- Attendance records
CREATE TABLE IF NOT EXISTS attendance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    status VARCHAR(20) NOT NULL, -- present, absent, late, excused
    marked_by UUID REFERENCES teachers(id),
    notes TEXT,
    marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, date)
);

-- Assessments (exams, tests, quizzes)
CREATE TABLE IF NOT EXISTS assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- exam, test, quiz, assignment, project
    subject VARCHAR(100) NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    max_marks DECIMAL(10,2) NOT NULL,
    passing_marks DECIMAL(10,2),
    date DATE NOT NULL,
    created_by UUID REFERENCES teachers(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assessment results
CREATE TABLE IF NOT EXISTS assessment_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    marks_obtained DECIMAL(10,2) NOT NULL,
    grade VARCHAR(5),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(assessment_id, student_id)
);

-- Class timetable
CREATE TABLE IF NOT EXISTS timetable (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    class_name VARCHAR(50) NOT NULL,
    day_of_week INTEGER NOT NULL, -- 1=Monday, 7=Sunday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    subject VARCHAR(100) NOT NULL,
    teacher_id UUID REFERENCES teachers(id),
    room VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_attendance_student ON attendance(student_id, date);
CREATE INDEX idx_attendance_school_date ON attendance(school_id, date);
CREATE INDEX idx_assessments_school ON assessments(school_id, class_name);
CREATE INDEX idx_assessment_results_student ON assessment_results(student_id);
CREATE INDEX idx_timetable_class ON timetable(school_id, class_name, day_of_week);

-- Update triggers
CREATE TRIGGER update_assessments_updated_at BEFORE UPDATE ON assessments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_assessment_results_updated_at BEFORE UPDATE ON assessment_results FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_timetable_updated_at BEFORE UPDATE ON timetable FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
