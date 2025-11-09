-- Support Operations Module
-- Incidents, inventory, health, library, and transport management

-- Incidents (behavior, safety, discipline)
CREATE TABLE IF NOT EXISTS incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id),
    incident_type VARCHAR(100) NOT NULL, -- behavior, safety, medical, bullying, accident
    severity VARCHAR(20) NOT NULL, -- low, medium, high, critical
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255),
    incident_date TIMESTAMP NOT NULL,
    reported_by VARCHAR(255) NOT NULL,
    witnesses TEXT,
    action_taken TEXT,
    parent_notified BOOLEAN DEFAULT false,
    parent_notified_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'open', -- open, investigating, resolved, closed
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory items
CREATE TABLE IF NOT EXISTS inventory_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL, -- furniture, equipment, supplies, books, electronics
    sku VARCHAR(100),
    description TEXT,
    unit_price DECIMAL(15,2),
    quantity_on_hand INTEGER DEFAULT 0,
    minimum_quantity INTEGER DEFAULT 0,
    location VARCHAR(255),
    condition VARCHAR(50) DEFAULT 'good', -- good, fair, poor, damaged
    purchase_date DATE,
    warranty_expiry DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory transactions
CREATE TABLE IF NOT EXISTS inventory_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inventory_item_id UUID NOT NULL REFERENCES inventory_items(id) ON DELETE CASCADE,
    transaction_type VARCHAR(50) NOT NULL, -- purchase, issue, return, damage, disposal
    quantity INTEGER NOT NULL,
    previous_quantity INTEGER NOT NULL,
    new_quantity INTEGER NOT NULL,
    issued_to VARCHAR(255),
    department VARCHAR(100),
    notes TEXT,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recorded_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Health visits (sickbay records)
CREATE TABLE IF NOT EXISTS health_visits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    symptoms TEXT NOT NULL,
    temperature DECIMAL(4,1),
    blood_pressure VARCHAR(20),
    diagnosis TEXT,
    treatment TEXT,
    medication_given TEXT,
    parent_notified BOOLEAN DEFAULT false,
    parent_notified_at TIMESTAMP,
    sent_home BOOLEAN DEFAULT false,
    follow_up_required BOOLEAN DEFAULT false,
    follow_up_notes TEXT,
    attended_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Library books
CREATE TABLE IF NOT EXISTS library_books (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    author VARCHAR(255),
    isbn VARCHAR(50),
    category VARCHAR(100),
    publisher VARCHAR(255),
    publication_year INTEGER,
    total_copies INTEGER DEFAULT 1,
    available_copies INTEGER DEFAULT 1,
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Library transactions
CREATE TABLE IF NOT EXISTS library_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    book_id UUID NOT NULL REFERENCES library_books(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id),
    teacher_id UUID REFERENCES teachers(id),
    transaction_type VARCHAR(20) NOT NULL, -- borrow, return
    borrow_date DATE DEFAULT CURRENT_DATE,
    due_date DATE,
    return_date DATE,
    fine_amount DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active', -- active, returned, overdue
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transport routes
CREATE TABLE IF NOT EXISTS transport_routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    route_name VARCHAR(255) NOT NULL,
    vehicle_number VARCHAR(50),
    driver_name VARCHAR(255),
    driver_phone VARCHAR(50),
    capacity INTEGER,
    stops TEXT[], -- Array of stop locations
    pickup_time TIME,
    dropoff_time TIME,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transport logs
CREATE TABLE IF NOT EXISTS transport_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    route_id UUID NOT NULL REFERENCES transport_routes(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id),
    log_date DATE DEFAULT CURRENT_DATE,
    log_type VARCHAR(20) NOT NULL, -- pickup, dropoff, absence
    stop_location VARCHAR(255),
    actual_time TIME,
    parent_notified BOOLEAN DEFAULT false,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_incidents_school ON incidents(school_id, incident_date);
CREATE INDEX idx_incidents_student ON incidents(student_id);
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_inventory_items_school ON inventory_items(school_id, category);
CREATE INDEX idx_inventory_transactions_item ON inventory_transactions(inventory_item_id);
CREATE INDEX idx_health_visits_school ON health_visits(school_id, visit_date);
CREATE INDEX idx_health_visits_student ON health_visits(student_id);
CREATE INDEX idx_library_books_school ON library_books(school_id);
CREATE INDEX idx_library_transactions_book ON library_transactions(book_id);
CREATE INDEX idx_library_transactions_student ON library_transactions(student_id);
CREATE INDEX idx_library_transactions_status ON library_transactions(status);
CREATE INDEX idx_transport_routes_school ON transport_routes(school_id);
CREATE INDEX idx_transport_logs_route ON transport_logs(route_id, log_date);

-- Update triggers
CREATE TRIGGER update_incidents_updated_at BEFORE UPDATE ON incidents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_inventory_items_updated_at BEFORE UPDATE ON inventory_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_health_visits_updated_at BEFORE UPDATE ON health_visits FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_library_books_updated_at BEFORE UPDATE ON library_books FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_library_transactions_updated_at BEFORE UPDATE ON library_transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transport_routes_updated_at BEFORE UPDATE ON transport_routes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
