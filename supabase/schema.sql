-- ============================================================
-- WHATSAPP AI RECEPTIONIST - Schema SQL per Supabase
-- ============================================================
-- Esegui questo script nel SQL Editor di Supabase.
-- Crea tutte le tabelle, indici, funzioni e trigger necessari.
-- ============================================================

-- 1. TABELLA TENANTS
CREATE TABLE tenants (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('restaurant', 'medical', 'barber', 'beauty', 'generic')),
    whatsapp_phone_number_id TEXT NOT NULL UNIQUE,
    welcome_message TEXT,
    capacity INTEGER NOT NULL DEFAULT 20,
    min_advance_hours INTEGER NOT NULL DEFAULT 2,
    max_advance_days INTEGER NOT NULL DEFAULT 30,
    slot_interval_minutes INTEGER NOT NULL DEFAULT 30,
    max_party_size INTEGER NOT NULL DEFAULT 20,
    min_party_size INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tenants_whatsapp ON tenants(whatsapp_phone_number_id);

-- 2. TABELLA TIME_PREFERENCES (fasce orarie)
CREATE TABLE time_preferences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    pref_key TEXT NOT NULL,
    label TEXT NOT NULL,
    from_time TIME NOT NULL,
    to_time TIME NOT NULL,
    UNIQUE(tenant_id, pref_key)
);

CREATE INDEX idx_time_prefs_tenant ON time_preferences(tenant_id);

-- 3. TABELLA SERVICES
CREATE TABLE services (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    service_key TEXT NOT NULL,
    name TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    description TEXT,
    UNIQUE(tenant_id, service_key)
);

CREATE INDEX idx_services_tenant ON services(tenant_id);

-- 4. TABELLA OPENING_HOURS
CREATE TABLE opening_hours (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    open_time TIME NOT NULL,
    close_time TIME NOT NULL,
    UNIQUE(tenant_id, day_of_week)
);

CREATE INDEX idx_opening_hours_tenant ON opening_hours(tenant_id);

-- 5. TABELLA EXCEPTIONS (chiusure, festività)
CREATE TABLE exceptions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    exception_date DATE NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('closed', 'special_hours')),
    open_time TIME,
    close_time TIME,
    reason TEXT,
    UNIQUE(tenant_id, exception_date)
);

CREATE INDEX idx_exceptions_tenant_date ON exceptions(tenant_id, exception_date);

-- 6. TABELLA BOOKINGS (prenotazioni)
CREATE TABLE bookings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    phone_number TEXT NOT NULL,
    customer_name TEXT,
    intent TEXT NOT NULL CHECK (intent IN ('create', 'move', 'cancel')),
    party_size INTEGER NOT NULL CHECK (party_size > 0),
    booking_date DATE NOT NULL,
    booking_time TIME NOT NULL,
    time_preference TEXT,
    service_id UUID REFERENCES services(id),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed')),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    confirmed_at TIMESTAMPTZ
);

CREATE INDEX idx_bookings_tenant ON bookings(tenant_id);
CREATE INDEX idx_bookings_phone ON bookings(phone_number);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_date_time ON bookings(tenant_id, booking_date, booking_time);

-- 7. TABELLA SESSIONS (sostituisce Redis)
CREATE TABLE sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    phone_number TEXT NOT NULL,
    conversation_id TEXT NOT NULL UNIQUE,
    intent TEXT,
    party_size INTEGER,
    time_preference TEXT,
    booking_date TEXT,
    booking_time TEXT,
    service_id TEXT,
    customer_name TEXT,
    existing_booking_id UUID,
    status TEXT NOT NULL DEFAULT 'collecting' CHECK (status IN ('collecting', 'confirming', 'completed', 'cancelled')),
    last_question TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '24 hours'),
    UNIQUE(tenant_id, phone_number)
);

CREATE INDEX idx_sessions_phone ON sessions(tenant_id, phone_number);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);

-- 8. FUNZIONE: Cleanup sessioni scadute
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sessions WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 9. FUNZIONE: Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bookings_updated_at BEFORE UPDATE ON bookings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 10. FUNZIONE: Trova slot disponibili per un giorno
CREATE OR REPLACE FUNCTION get_available_slots(
    p_tenant_id UUID,
    p_date DATE,
    p_time_preference TEXT DEFAULT NULL,
    p_party_size INTEGER DEFAULT NULL
)
RETURNS TABLE (slot_time TIME, is_available BOOLEAN) AS $$
DECLARE
    v_open_time TIME;
    v_close_time TIME;
    v_interval INTEGER;
    v_duration INTEGER;
    v_current_time TIME;
    v_is_closed BOOLEAN;
BEGIN
    -- Verifica eccezioni
    SELECT type = 'closed' INTO v_is_closed
    FROM exceptions WHERE tenant_id = p_tenant_id AND exception_date = p_date LIMIT 1;
    
    IF v_is_closed THEN RETURN; END IF;
    
    -- Recupera orari apertura
    SELECT oh.open_time, oh.close_time INTO v_open_time, v_close_time
    FROM opening_hours oh
    WHERE oh.tenant_id = p_tenant_id AND oh.day_of_week = EXTRACT(DOW FROM p_date)::INTEGER;
    
    IF v_open_time IS NULL THEN RETURN; END IF;
    
    -- Config
    SELECT t.slot_interval_minutes, COALESCE(s.duration_minutes, 60)
    INTO v_interval, v_duration
    FROM tenants t LEFT JOIN services s ON s.tenant_id = t.id
    WHERE t.id = p_tenant_id LIMIT 1;
    
    -- Genera slot
    v_current_time := v_open_time;
    WHILE v_current_time + (v_duration || ' minutes')::INTERVAL <= v_close_time LOOP
        -- Filtra per fascia
        IF p_time_preference IS NOT NULL THEN
            IF NOT EXISTS (
                SELECT 1 FROM time_preferences tp
                WHERE tp.tenant_id = p_tenant_id AND tp.pref_key = p_time_preference
                AND v_current_time >= tp.from_time AND v_current_time < tp.to_time
            ) THEN
                v_current_time := v_current_time + (v_interval || ' minutes')::INTERVAL;
                CONTINUE;
            END IF;
        END IF;
        
        slot_time := v_current_time;
        is_available := NOT EXISTS (
            SELECT 1 FROM bookings b
            WHERE b.tenant_id = p_tenant_id AND b.booking_date = p_date
            AND b.status IN ('pending', 'confirmed')
            AND b.booking_time < (v_current_time + (v_duration || ' minutes')::INTERVAL)
            AND (b.booking_time + (v_duration || ' minutes')::INTERVAL) > v_current_time
        );
        
        IF is_available THEN RETURN NEXT; END IF;
        v_current_time := v_current_time + (v_interval || ' minutes')::INTERVAL;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 11. ROW LEVEL SECURITY
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE time_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE services ENABLE ROW LEVEL SECURITY;
ALTER TABLE opening_hours ENABLE ROW LEVEL SECURITY;
ALTER TABLE exceptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all" ON tenants FOR ALL USING (true);
CREATE POLICY "Allow all" ON time_preferences FOR ALL USING (true);
CREATE POLICY "Allow all" ON services FOR ALL USING (true);
CREATE POLICY "Allow all" ON opening_hours FOR ALL USING (true);
CREATE POLICY "Allow all" ON exceptions FOR ALL USING (true);
CREATE POLICY "Allow all" ON bookings FOR ALL USING (true);
CREATE POLICY "Allow all" ON sessions FOR ALL USING (true);

-- 12. DATI DI ESEMPIO
INSERT INTO tenants (id, name, type, whatsapp_phone_number_id, capacity)
VALUES ('00000000-0000-0000-0000-000000000001', 'Ristorante Bella Vista', 'restaurant', 'test_phone_id', 60);

INSERT INTO time_preferences (tenant_id, pref_key, label, from_time, to_time) VALUES
    ('00000000-0000-0000-0000-000000000001', 'lunch', 'Pranzo', '12:00', '14:30'),
    ('00000000-0000-0000-0000-000000000001', 'dinner', 'Cena', '19:00', '23:00');

INSERT INTO services (tenant_id, service_key, name, duration_minutes) VALUES
    ('00000000-0000-0000-0000-000000000001', 'table', 'Tavolo', 90);

INSERT INTO opening_hours (tenant_id, day_of_week, open_time, close_time) VALUES
    ('00000000-0000-0000-0000-000000000001', 0, '12:00', '23:00'),
    ('00000000-0000-0000-0000-000000000001', 1, '12:00', '14:30'),
    ('00000000-0000-0000-0000-000000000001', 2, '12:00', '14:30'),
    ('00000000-0000-0000-0000-000000000001', 3, '12:00', '14:30'),
    ('00000000-0000-0000-0000-000000000001', 4, '12:00', '14:30'),
    ('00000000-0000-0000-0000-000000000001', 5, '12:00', '14:30'),
    ('00000000-0000-0000-0000-000000000001', 6, '12:00', '23:00');