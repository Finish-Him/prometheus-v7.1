-- =============================================================================
-- PROMETHEUS V7 - SUPABASE POSTGRESQL SCHEMA
-- DreamLeague Season 27 Edition
-- Created: 2025-12-10
-- =============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- 1. TOURNAMENTS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS tournaments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    tier INTEGER DEFAULT 1,
    prize_pool INTEGER DEFAULT 0,
    start_date DATE,
    end_date DATE,
    location TEXT,
    format JSONB DEFAULT '{}',
    status TEXT DEFAULT 'upcoming' CHECK (status IN ('upcoming', 'ongoing', 'completed')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for tournament queries
CREATE INDEX idx_tournaments_status ON tournaments(status);
CREATE INDEX idx_tournaments_dates ON tournaments(start_date, end_date);

COMMENT ON TABLE tournaments IS 'Dota 2 tournaments and leagues';

-- =============================================================================
-- 2. TEAMS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS teams (
    team_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    tag TEXT,
    region TEXT,
    tier TEXT DEFAULT 'C' CHECK (tier IN ('S', 'A', 'B', 'C')),
    logo_url TEXT,
    rating NUMERIC(10, 2) DEFAULT 0,
    all_time_wins INTEGER DEFAULT 0,
    all_time_losses INTEGER DEFAULT 0,
    last_match_time BIGINT,
    opendota_synced BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for team queries
CREATE INDEX idx_teams_name ON teams(name);
CREATE INDEX idx_teams_region ON teams(region);
CREATE INDEX idx_teams_rating ON teams(rating DESC);
CREATE INDEX idx_teams_tier ON teams(tier);

COMMENT ON TABLE teams IS 'Professional Dota 2 teams with OpenDota data';

-- =============================================================================
-- 3. PLAYERS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS players (
    account_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    team_id BIGINT REFERENCES teams(team_id) ON DELETE SET NULL,
    role TEXT,
    position INTEGER CHECK (position BETWEEN 1 AND 5),
    games_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    winrate NUMERIC(5, 2) DEFAULT 0,
    is_current_team_member BOOLEAN DEFAULT TRUE,
    country_code TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for player queries
CREATE INDEX idx_players_team ON players(team_id);
CREATE INDEX idx_players_name ON players(name);
CREATE INDEX idx_players_winrate ON players(winrate DESC);

COMMENT ON TABLE players IS 'Professional Dota 2 players';

-- =============================================================================
-- 4. MATCHES TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS matches (
    match_id BIGINT PRIMARY KEY,
    team_id BIGINT REFERENCES teams(team_id) ON DELETE CASCADE,
    opponent_team_id BIGINT REFERENCES teams(team_id) ON DELETE SET NULL,
    opponent_name TEXT,
    radiant BOOLEAN,
    radiant_win BOOLEAN,
    won BOOLEAN,
    duration INTEGER,
    duration_min NUMERIC(5, 1),
    start_time BIGINT,
    match_date DATE,
    league_id BIGINT,
    league_name TEXT,
    game_mode INTEGER,
    cluster INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for match queries
CREATE INDEX idx_matches_team ON matches(team_id);
CREATE INDEX idx_matches_opponent ON matches(opponent_team_id);
CREATE INDEX idx_matches_date ON matches(match_date DESC);
CREATE INDEX idx_matches_start_time ON matches(start_time DESC);
CREATE INDEX idx_matches_league ON matches(league_id);

COMMENT ON TABLE matches IS 'Historical match data from OpenDota';

-- =============================================================================
-- 5. TOURNAMENT_TEAMS (Junction Table)
-- =============================================================================
CREATE TABLE IF NOT EXISTS tournament_teams (
    tournament_id TEXT REFERENCES tournaments(id) ON DELETE CASCADE,
    team_id BIGINT REFERENCES teams(team_id) ON DELETE CASCADE,
    seed TEXT,
    ranking INTEGER,
    group_name TEXT,
    PRIMARY KEY (tournament_id, team_id)
);

CREATE INDEX idx_tournament_teams_tournament ON tournament_teams(tournament_id);
CREATE INDEX idx_tournament_teams_team ON tournament_teams(team_id);

COMMENT ON TABLE tournament_teams IS 'Teams participating in tournaments';

-- =============================================================================
-- 6. SCHEDULE TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS schedule (
    id SERIAL PRIMARY KEY,
    tournament_id TEXT REFERENCES tournaments(id) ON DELETE CASCADE,
    round TEXT NOT NULL,
    match_number INTEGER,
    match_date DATE,
    time_cet TIME,
    time_brt TIME,
    team_a_id BIGINT REFERENCES teams(team_id) ON DELETE SET NULL,
    team_b_id BIGINT REFERENCES teams(team_id) ON DELETE SET NULL,
    team_a_name TEXT,
    team_b_name TEXT,
    format TEXT DEFAULT 'Bo3',
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'live', 'completed', 'postponed')),
    result JSONB DEFAULT '{}',
    stream_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_schedule_tournament ON schedule(tournament_id);
CREATE INDEX idx_schedule_date ON schedule(match_date);
CREATE INDEX idx_schedule_status ON schedule(status);

COMMENT ON TABLE schedule IS 'Tournament match schedule';

-- =============================================================================
-- 7. BETS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS bets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT DEFAULT 'default_user',
    schedule_id INTEGER REFERENCES schedule(id) ON DELETE SET NULL,
    match_id BIGINT,
    tournament_id TEXT REFERENCES tournaments(id) ON DELETE SET NULL,
    team_a TEXT,
    team_b TEXT,
    selection TEXT NOT NULL,
    market TEXT DEFAULT 'match_winner',
    odds NUMERIC(5, 2) NOT NULL CHECK (odds >= 1.01),
    stake NUMERIC(10, 2) NOT NULL CHECK (stake > 0),
    potential_return NUMERIC(10, 2),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'won', 'lost', 'void', 'cashout')),
    result TEXT,
    profit NUMERIC(10, 2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    settled_at TIMESTAMPTZ
);

CREATE INDEX idx_bets_user ON bets(user_id);
CREATE INDEX idx_bets_status ON bets(status);
CREATE INDEX idx_bets_created ON bets(created_at DESC);
CREATE INDEX idx_bets_tournament ON bets(tournament_id);

COMMENT ON TABLE bets IS 'User betting records';

-- =============================================================================
-- 8. TEAM_STATS TABLE (Aggregated Statistics)
-- =============================================================================
CREATE TABLE IF NOT EXISTS team_stats (
    id SERIAL PRIMARY KEY,
    team_id BIGINT REFERENCES teams(team_id) ON DELETE CASCADE,
    period TEXT DEFAULT 'all_time',
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    winrate NUMERIC(5, 2) DEFAULT 0,
    avg_duration_min NUMERIC(5, 1) DEFAULT 0,
    radiant_winrate NUMERIC(5, 2) DEFAULT 0,
    dire_winrate NUMERIC(5, 2) DEFAULT 0,
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(team_id, period)
);

CREATE INDEX idx_team_stats_team ON team_stats(team_id);

COMMENT ON TABLE team_stats IS 'Pre-calculated team statistics';

-- =============================================================================
-- 9. HEROES TABLE (Reference)
-- =============================================================================
CREATE TABLE IF NOT EXISTS heroes (
    hero_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    localized_name TEXT,
    primary_attr TEXT,
    attack_type TEXT,
    roles TEXT[],
    img_url TEXT
);

COMMENT ON TABLE heroes IS 'Dota 2 hero reference data';

-- =============================================================================
-- 10. TEAM_HEROES TABLE (Team hero preferences)
-- =============================================================================
CREATE TABLE IF NOT EXISTS team_heroes (
    id SERIAL PRIMARY KEY,
    team_id BIGINT REFERENCES teams(team_id) ON DELETE CASCADE,
    hero_id INTEGER REFERENCES heroes(hero_id) ON DELETE CASCADE,
    games INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    winrate NUMERIC(5, 2) DEFAULT 0,
    UNIQUE(team_id, hero_id)
);

CREATE INDEX idx_team_heroes_team ON team_heroes(team_id);
CREATE INDEX idx_team_heroes_hero ON team_heroes(hero_id);

COMMENT ON TABLE team_heroes IS 'Team hero pick statistics';

-- =============================================================================
-- 11. BANKROLL TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS bankroll (
    id SERIAL PRIMARY KEY,
    user_id TEXT DEFAULT 'default_user' UNIQUE,
    balance NUMERIC(12, 2) DEFAULT 1000.00,
    initial_balance NUMERIC(12, 2) DEFAULT 1000.00,
    total_deposited NUMERIC(12, 2) DEFAULT 0,
    total_withdrawn NUMERIC(12, 2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE bankroll IS 'User bankroll management';

-- =============================================================================
-- 12. AUDIT_LOG TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    record_id TEXT,
    old_data JSONB,
    new_data JSONB,
    user_id TEXT DEFAULT 'system',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_log_table ON audit_log(table_name);
CREATE INDEX idx_audit_log_created ON audit_log(created_at DESC);

COMMENT ON TABLE audit_log IS 'Data change audit trail';

-- =============================================================================
-- FUNCTIONS & TRIGGERS
-- =============================================================================

-- Function to update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update_at trigger to relevant tables
CREATE TRIGGER update_tournaments_updated_at
    BEFORE UPDATE ON tournaments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teams_updated_at
    BEFORE UPDATE ON teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_players_updated_at
    BEFORE UPDATE ON players
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_schedule_updated_at
    BEFORE UPDATE ON schedule
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bankroll_updated_at
    BEFORE UPDATE ON bankroll
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate potential return on bet insert
CREATE OR REPLACE FUNCTION calculate_bet_return()
RETURNS TRIGGER AS $$
BEGIN
    NEW.potential_return = NEW.stake * NEW.odds;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calculate_bet_return_trigger
    BEFORE INSERT OR UPDATE ON bets
    FOR EACH ROW EXECUTE FUNCTION calculate_bet_return();

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

-- Enable RLS on sensitive tables
ALTER TABLE bets ENABLE ROW LEVEL SECURITY;
ALTER TABLE bankroll ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own bets (for future auth)
CREATE POLICY "Users can view own bets" ON bets
    FOR SELECT USING (user_id = current_setting('app.user_id', true) OR current_setting('app.user_id', true) IS NULL);

CREATE POLICY "Users can insert own bets" ON bets
    FOR INSERT WITH CHECK (user_id = current_setting('app.user_id', true) OR current_setting('app.user_id', true) IS NULL);

CREATE POLICY "Users can update own bets" ON bets
    FOR UPDATE USING (user_id = current_setting('app.user_id', true) OR current_setting('app.user_id', true) IS NULL);

-- Policy: Users can only see their own bankroll
CREATE POLICY "Users can view own bankroll" ON bankroll
    FOR SELECT USING (user_id = current_setting('app.user_id', true) OR current_setting('app.user_id', true) IS NULL);

CREATE POLICY "Users can update own bankroll" ON bankroll
    FOR UPDATE USING (user_id = current_setting('app.user_id', true) OR current_setting('app.user_id', true) IS NULL);

-- =============================================================================
-- VIEWS
-- =============================================================================

-- View: Team standings with recent performance
CREATE OR REPLACE VIEW v_team_standings AS
SELECT 
    t.team_id,
    t.name,
    t.tag,
    t.region,
    t.tier,
    t.rating,
    ts.matches_played,
    ts.wins,
    ts.losses,
    ts.winrate,
    ts.avg_duration_min
FROM teams t
LEFT JOIN team_stats ts ON t.team_id = ts.team_id AND ts.period = 'last_100'
ORDER BY t.rating DESC;

-- View: Upcoming matches
CREATE OR REPLACE VIEW v_upcoming_matches AS
SELECT 
    s.id,
    s.tournament_id,
    tr.name as tournament_name,
    s.round,
    s.match_date,
    s.time_brt,
    s.team_a_name,
    s.team_b_name,
    s.format,
    s.status,
    ta.rating as team_a_rating,
    tb.rating as team_b_rating
FROM schedule s
JOIN tournaments tr ON s.tournament_id = tr.id
LEFT JOIN teams ta ON s.team_a_id = ta.team_id
LEFT JOIN teams tb ON s.team_b_id = tb.team_id
WHERE s.status IN ('scheduled', 'live')
ORDER BY s.match_date, s.time_brt;

-- View: Bet history with P&L
CREATE OR REPLACE VIEW v_bet_history AS
SELECT 
    b.id,
    b.created_at,
    b.tournament_id,
    b.team_a || ' vs ' || b.team_b as match,
    b.selection,
    b.odds,
    b.stake,
    b.potential_return,
    b.status,
    b.profit,
    SUM(b.profit) OVER (ORDER BY b.created_at) as running_total
FROM bets b
ORDER BY b.created_at DESC;

-- =============================================================================
-- INITIAL DATA
-- =============================================================================

-- Insert default user bankroll
INSERT INTO bankroll (user_id, balance, initial_balance)
VALUES ('default_user', 1000.00, 1000.00)
ON CONFLICT (user_id) DO NOTHING;

-- =============================================================================
-- GRANT PERMISSIONS (for Supabase anon/authenticated roles)
-- =============================================================================

-- Public read access to most tables
GRANT SELECT ON tournaments, teams, players, matches, tournament_teams, schedule, heroes, team_heroes, team_stats TO anon;
GRANT SELECT ON v_team_standings, v_upcoming_matches TO anon;

-- Authenticated users can manage bets and bankroll
GRANT ALL ON bets, bankroll TO authenticated;
GRANT SELECT ON v_bet_history TO authenticated;
GRANT USAGE ON SEQUENCE bets_id_seq TO authenticated;

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================
