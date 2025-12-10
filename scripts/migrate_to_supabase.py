"""
Prometheus V7 - Migration Script: JSON to Supabase PostgreSQL
Migrates existing JSON data to Supabase database.

Usage:
    python scripts/migrate_to_supabase.py

Requirements:
    pip install supabase python-dotenv
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ supabase-py not installed. Run: pip install supabase")
    exit(1)

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / "Database" / "Json"

# Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # anon or service_role key

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_json(filepath: Path) -> dict:
    """Load JSON file safely."""
    try:
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
    return {}


def get_supabase_client() -> Optional[Client]:
    """Create Supabase client."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env file")
        print("   Create a .env file with:")
        print("   SUPABASE_URL=https://your-project.supabase.co")
        print("   SUPABASE_KEY=your-anon-or-service-role-key")
        return None
    
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"✅ Connected to Supabase: {SUPABASE_URL[:50]}...")
        return client
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return None


# =============================================================================
# MIGRATION FUNCTIONS
# =============================================================================

def migrate_tournaments(client: Client) -> int:
    """Migrate tournament data from dreamleague_s27.json."""
    print("\n📦 Migrating tournaments...")
    
    data = load_json(DATABASE_PATH / "leagues" / "dreamleague_s27.json")
    if not data:
        print("   ⚠️ No tournament data found")
        return 0
    
    tournament = data.get("tournament", {})
    if not tournament:
        return 0
    
    record = {
        "id": tournament.get("id", "dreamleague_s27"),
        "name": tournament.get("name", "DreamLeague Season 27"),
        "tier": tournament.get("tier", 1),
        "prize_pool": tournament.get("prize_pool", 1000000),
        "start_date": tournament.get("start_date"),
        "end_date": tournament.get("end_date"),
        "location": tournament.get("location", "Stockholm"),
        "format": tournament.get("format", {}),
        "status": "ongoing"
    }
    
    try:
        result = client.table("tournaments").upsert(record).execute()
        print(f"   ✅ Tournament: {record['name']}")
        return 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 0


def migrate_teams(client: Client) -> int:
    """Migrate teams from pro_teams.json and dreamleague_s27.json."""
    print("\n📦 Migrating teams...")
    
    # Load pro teams (with OpenDota data)
    pro_teams = load_json(DATABASE_PATH / "teams" / "pro_teams.json")
    teams_list = pro_teams.get("teams", [])
    
    # Load DreamLeague teams for additional data
    dl_data = load_json(DATABASE_PATH / "leagues" / "dreamleague_s27.json")
    dl_teams = {t.get("name"): t for t in dl_data.get("teams", [])}
    
    count = 0
    for team in teams_list:
        team_name = team.get("name", "")
        dl_team = dl_teams.get(team_name, {})
        recent_stats = team.get("recent_stats", {})
        
        record = {
            "team_id": team.get("team_id"),
            "name": team_name,
            "tag": team.get("tag"),
            "region": dl_team.get("region", "Unknown"),
            "tier": dl_team.get("tier", "B"),
            "logo_url": team.get("logo_url"),
            "rating": team.get("rating", 0),
            "all_time_wins": team.get("all_time_wins", 0),
            "all_time_losses": team.get("all_time_losses", 0),
            "last_match_time": team.get("last_match_time"),
            "opendota_synced": True
        }
        
        try:
            client.table("teams").upsert(record).execute()
            count += 1
            print(f"   ✅ Team: {team_name} (ID: {record['team_id']})")
        except Exception as e:
            print(f"   ❌ Team {team_name}: {e}")
    
    print(f"   📊 Total teams migrated: {count}")
    return count


def migrate_players(client: Client) -> int:
    """Migrate players from pro_players.json."""
    print("\n📦 Migrating players...")
    
    data = load_json(DATABASE_PATH / "players" / "pro_players.json")
    players_list = data.get("players", [])
    
    count = 0
    for player in players_list:
        record = {
            "account_id": player.get("account_id"),
            "name": player.get("name"),
            "team_id": player.get("team_id"),
            "games_played": player.get("games_played", 0),
            "wins": player.get("wins", 0),
            "losses": player.get("games_played", 0) - player.get("wins", 0),
            "winrate": player.get("winrate", 0),
            "is_current_team_member": player.get("is_current_team_member", True)
        }
        
        try:
            client.table("players").upsert(record).execute()
            count += 1
        except Exception as e:
            print(f"   ❌ Player {player.get('name')}: {e}")
    
    print(f"   ✅ Migrated {count} players")
    return count


def migrate_team_stats(client: Client) -> int:
    """Migrate team statistics from pro_teams.json."""
    print("\n📦 Migrating team stats...")
    
    data = load_json(DATABASE_PATH / "teams" / "pro_teams.json")
    teams_list = data.get("teams", [])
    
    count = 0
    for team in teams_list:
        recent = team.get("recent_stats", {})
        
        record = {
            "team_id": team.get("team_id"),
            "period": "last_100",
            "matches_played": recent.get("matches", 0),
            "wins": recent.get("wins", 0),
            "losses": recent.get("losses", 0),
            "winrate": recent.get("winrate", 0),
            "avg_duration_min": recent.get("avg_duration_min", 0)
        }
        
        try:
            client.table("team_stats").upsert(
                record,
                on_conflict="team_id,period"
            ).execute()
            count += 1
        except Exception as e:
            print(f"   ❌ Stats for team {team.get('team_id')}: {e}")
    
    print(f"   ✅ Migrated stats for {count} teams")
    return count


def migrate_team_heroes(client: Client) -> int:
    """Migrate team hero preferences from pro_teams.json."""
    print("\n📦 Migrating team heroes...")
    
    data = load_json(DATABASE_PATH / "teams" / "pro_teams.json")
    teams_list = data.get("teams", [])
    
    count = 0
    for team in teams_list:
        team_id = team.get("team_id")
        heroes = team.get("top_heroes", [])
        
        for hero in heroes[:10]:  # Top 10 heroes per team
            record = {
                "team_id": team_id,
                "hero_id": hero.get("hero_id"),
                "games": hero.get("games", 0),
                "wins": hero.get("wins", 0),
                "winrate": hero.get("winrate", 0)
            }
            
            try:
                client.table("team_heroes").upsert(
                    record,
                    on_conflict="team_id,hero_id"
                ).execute()
                count += 1
            except Exception as e:
                pass  # Skip errors for hero data
    
    print(f"   ✅ Migrated {count} team-hero records")
    return count


def migrate_tournament_teams(client: Client) -> int:
    """Migrate tournament team registrations."""
    print("\n📦 Migrating tournament teams...")
    
    data = load_json(DATABASE_PATH / "leagues" / "dreamleague_s27.json")
    teams = data.get("teams", [])
    
    count = 0
    for team in teams:
        team_id = team.get("team_id")
        if not team_id:
            continue
        
        record = {
            "tournament_id": "dreamleague_s27",
            "team_id": team_id,
            "seed": team.get("tier", "C"),
            "ranking": team.get("ranking")
        }
        
        try:
            client.table("tournament_teams").upsert(record).execute()
            count += 1
        except Exception as e:
            print(f"   ❌ Tournament team {team.get('name')}: {e}")
    
    print(f"   ✅ Migrated {count} tournament team registrations")
    return count


def migrate_schedule(client: Client) -> int:
    """Migrate match schedule from dreamleague_s27.json."""
    print("\n📦 Migrating schedule...")
    
    data = load_json(DATABASE_PATH / "leagues" / "dreamleague_s27.json")
    schedule = data.get("schedule", {})
    
    # Create a team name -> team_id mapping
    teams = {t.get("name"): t.get("team_id") for t in data.get("teams", [])}
    
    count = 0
    for round_name, round_data in schedule.items():
        matches = round_data.get("matches", [])
        
        for i, match in enumerate(matches):
            team_a = match.get("team_a", "")
            team_b = match.get("team_b", "")
            
            # Parse time (format: "HH:MM")
            time_cet = match.get("time_cet", "")
            time_brt = match.get("time_brt", "")
            
            record = {
                "tournament_id": "dreamleague_s27",
                "round": round_name.replace("_", " ").title(),
                "match_number": i + 1,
                "match_date": "2025-12-10",  # From schedule
                "time_cet": time_cet if time_cet else None,
                "time_brt": time_brt if time_brt else None,
                "team_a_id": teams.get(team_a),
                "team_b_id": teams.get(team_b),
                "team_a_name": team_a,
                "team_b_name": team_b,
                "format": match.get("format", "Bo3"),
                "status": "scheduled"
            }
            
            try:
                client.table("schedule").insert(record).execute()
                count += 1
            except Exception as e:
                print(f"   ❌ Schedule match {team_a} vs {team_b}: {e}")
    
    print(f"   ✅ Migrated {count} scheduled matches")
    return count


def migrate_matches(client: Client) -> int:
    """Migrate historical matches from match JSON files."""
    print("\n📦 Migrating historical matches...")
    
    matches_dir = DATABASE_PATH / "matches" / "dreamleague_s27"
    if not matches_dir.exists():
        print(f"   ⚠️ Matches directory not found: {matches_dir}")
        return 0
    
    count = 0
    total_files = 0
    
    for match_file in matches_dir.glob("*.json"):
        total_files += 1
        data = load_json(match_file)
        
        team_id = data.get("team_id")
        matches = data.get("matches", [])
        
        for match in matches[:50]:  # Limit to 50 per team for initial migration
            record = {
                "match_id": match.get("match_id"),
                "team_id": team_id,
                "opponent_team_id": match.get("opposing_team_id"),
                "opponent_name": match.get("opposing_team_name"),
                "radiant": match.get("radiant"),
                "radiant_win": match.get("radiant_win"),
                "won": match.get("radiant") == match.get("radiant_win"),
                "duration": match.get("duration"),
                "duration_min": round(match.get("duration", 0) / 60, 1),
                "start_time": match.get("start_time"),
                "league_id": match.get("leagueid")
            }
            
            try:
                client.table("matches").upsert(record).execute()
                count += 1
            except Exception as e:
                pass  # Skip duplicates
        
        print(f"   📁 Processed: {match_file.name}")
    
    print(f"   ✅ Migrated {count} matches from {total_files} files")
    return count


def initialize_bankroll(client: Client) -> bool:
    """Initialize default user bankroll."""
    print("\n📦 Initializing bankroll...")
    
    record = {
        "user_id": "default_user",
        "balance": 1000.00,
        "initial_balance": 1000.00
    }
    
    try:
        client.table("bankroll").upsert(record).execute()
        print("   ✅ Bankroll initialized: R$ 1,000.00")
        return True
    except Exception as e:
        print(f"   ❌ Bankroll error: {e}")
        return False


# =============================================================================
# VERIFICATION FUNCTIONS
# =============================================================================

def verify_migration(client: Client):
    """Verify migration by counting records in each table."""
    print("\n" + "=" * 60)
    print("📊 MIGRATION VERIFICATION")
    print("=" * 60)
    
    tables = [
        "tournaments",
        "teams", 
        "players",
        "matches",
        "tournament_teams",
        "schedule",
        "team_stats",
        "team_heroes",
        "bankroll"
    ]
    
    for table in tables:
        try:
            result = client.table(table).select("*", count="exact").execute()
            count = len(result.data) if result.data else 0
            print(f"   {table}: {count} records")
        except Exception as e:
            print(f"   {table}: ❌ Error - {e}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main migration function."""
    print("=" * 60)
    print("🔥 PROMETHEUS V7 - SUPABASE MIGRATION")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Database path: {DATABASE_PATH}")
    
    # Connect to Supabase
    client = get_supabase_client()
    if not client:
        return
    
    # Run migrations in order (respecting foreign keys)
    totals = {}
    
    # 1. Tournaments first (no dependencies)
    totals["tournaments"] = migrate_tournaments(client)
    
    # 2. Teams (no dependencies)
    totals["teams"] = migrate_teams(client)
    
    # 3. Players (depends on teams)
    totals["players"] = migrate_players(client)
    
    # 4. Tournament teams (depends on tournaments, teams)
    totals["tournament_teams"] = migrate_tournament_teams(client)
    
    # 5. Schedule (depends on tournaments, teams)
    totals["schedule"] = migrate_schedule(client)
    
    # 6. Team stats (depends on teams)
    totals["team_stats"] = migrate_team_stats(client)
    
    # 7. Team heroes (depends on teams)
    totals["team_heroes"] = migrate_team_heroes(client)
    
    # 8. Matches (depends on teams)
    totals["matches"] = migrate_matches(client)
    
    # 9. Initialize bankroll
    initialize_bankroll(client)
    
    # Verify migration
    verify_migration(client)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ MIGRATION COMPLETE")
    print("=" * 60)
    total_records = sum(totals.values())
    print(f"📊 Total records migrated: {total_records}")
    
    for table, count in totals.items():
        print(f"   • {table}: {count}")


if __name__ == "__main__":
    main()
