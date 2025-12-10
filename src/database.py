"""
Prometheus V7 - Supabase Database Client
Handles all database operations with Supabase PostgreSQL.
"""

import os
import json
import streamlit as st
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# Try to import supabase, fallback to JSON if not available
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

# =============================================================================
# CONFIGURATION
# =============================================================================

DATABASE_PATH = Path(__file__).parent.parent / "Database" / "Json"


def _load_json(filepath: Path) -> dict:
    """Load JSON file safely (fallback when Supabase unavailable)."""
    try:
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


# =============================================================================
# SUPABASE CLIENT
# =============================================================================

@st.cache_resource
def get_supabase_client() -> Optional[Client]:
    """
    Get Supabase client (cached for performance).
    Uses st.secrets for Streamlit Cloud or environment variables locally.
    """
    if not SUPABASE_AVAILABLE:
        return None
    
    # Try Streamlit secrets first (for Streamlit Cloud)
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    
    # Try environment variables (for local development)
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    
    return None


def is_supabase_connected() -> bool:
    """Check if Supabase is available and connected."""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        # Simple query to test connection
        client.table("tournaments").select("id").limit(1).execute()
        return True
    except Exception:
        return False


# =============================================================================
# DATA LOADING FUNCTIONS (Hybrid: Supabase + JSON fallback)
# =============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_tournaments() -> List[Dict[str, Any]]:
    """Load tournaments from Supabase or JSON fallback."""
    client = get_supabase_client()
    
    if client:
        try:
            result = client.table("tournaments").select("*").execute()
            if result.data:
                return result.data
        except Exception:
            pass
    
    # Fallback to JSON
    data = _load_json(DATABASE_PATH / "leagues" / "dreamleague_s27.json")
    if data.get("tournament"):
        return [data["tournament"]]
    return []


@st.cache_data(ttl=300)
def load_dreamleague() -> Dict[str, Any]:
    """Load DreamLeague S27 data."""
    client = get_supabase_client()
    
    if client:
        try:
            # Get tournament
            tournament = client.table("tournaments")\
                .select("*")\
                .eq("id", "dreamleague_s27")\
                .single()\
                .execute()
            
            # Get teams
            teams = client.table("tournament_teams")\
                .select("*, teams(*)")\
                .eq("tournament_id", "dreamleague_s27")\
                .execute()
            
            # Get schedule
            schedule = client.table("schedule")\
                .select("*")\
                .eq("tournament_id", "dreamleague_s27")\
                .order("match_date")\
                .order("time_brt")\
                .execute()
            
            if tournament.data:
                return {
                    "tournament": tournament.data,
                    "teams": [t.get("teams") for t in teams.data] if teams.data else [],
                    "schedule": {"round_1": {"matches": schedule.data}} if schedule.data else {}
                }
        except Exception:
            pass
    
    # Fallback to JSON
    data = _load_json(DATABASE_PATH / "leagues" / "dreamleague_s27.json")
    if not data:
        data = _load_json(DATABASE_PATH / "leagues" / "dreamleague_s26.json")
    return data


@st.cache_data(ttl=300)
def load_pro_teams() -> Dict[str, Any]:
    """Load pro teams from Supabase or JSON fallback."""
    client = get_supabase_client()
    
    if client:
        try:
            result = client.table("teams")\
                .select("*, team_stats(*)")\
                .order("rating", desc=True)\
                .execute()
            
            if result.data:
                teams = []
                for team in result.data:
                    stats = team.pop("team_stats", [])
                    recent = next((s for s in stats if s.get("period") == "last_100"), {})
                    team["recent_stats"] = {
                        "matches": recent.get("matches_played", 0),
                        "wins": recent.get("wins", 0),
                        "losses": recent.get("losses", 0),
                        "winrate": float(recent.get("winrate", 0)),
                        "avg_duration_min": float(recent.get("avg_duration_min", 0))
                    }
                    teams.append(team)
                
                return {"teams": teams, "last_updated": datetime.now().isoformat()}
        except Exception:
            pass
    
    # Fallback to JSON
    return _load_json(DATABASE_PATH / "teams" / "pro_teams.json")


@st.cache_data(ttl=300)
def load_pro_players() -> Dict[str, Any]:
    """Load pro players from Supabase or JSON fallback."""
    client = get_supabase_client()
    
    if client:
        try:
            result = client.table("players")\
                .select("*, teams(name, tag)")\
                .order("winrate", desc=True)\
                .execute()
            
            if result.data:
                players = []
                for player in result.data:
                    team_info = player.pop("teams", {}) or {}
                    player["team_name"] = team_info.get("name", "Unknown")
                    players.append(player)
                
                return {"players": players, "last_updated": datetime.now().isoformat()}
        except Exception:
            pass
    
    # Fallback to JSON
    return _load_json(DATABASE_PATH / "players" / "pro_players.json")


@st.cache_data(ttl=300)
def load_schedule(tournament_id: str = "dreamleague_s27") -> List[Dict[str, Any]]:
    """Load match schedule from Supabase."""
    client = get_supabase_client()
    
    if client:
        try:
            result = client.table("schedule")\
                .select("*")\
                .eq("tournament_id", tournament_id)\
                .order("match_date")\
                .order("time_brt")\
                .execute()
            
            if result.data:
                return result.data
        except Exception:
            pass
    
    # Fallback to JSON
    data = _load_json(DATABASE_PATH / "leagues" / f"{tournament_id}.json")
    return data.get("schedule", {}).get("round_1", {}).get("matches", [])


@st.cache_data(ttl=60)  # Cache for 1 minute (bets change frequently)
def load_bets(user_id: str = "default_user") -> Dict[str, Any]:
    """Load user bets from Supabase."""
    client = get_supabase_client()
    
    if client:
        try:
            # Get bankroll
            bankroll_result = client.table("bankroll")\
                .select("*")\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            # Get bets
            bets_result = client.table("bets")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .execute()
            
            bankroll = bankroll_result.data.get("balance", 1000) if bankroll_result.data else 1000
            bets = bets_result.data if bets_result.data else []
            
            return {"bankroll": bankroll, "bets": bets}
        except Exception:
            pass
    
    # Fallback to JSON
    data = _load_json(DATABASE_PATH / "bets" / "user_bets.json")
    return data if data else {"bankroll": 1000, "bets": []}


# =============================================================================
# DATA WRITING FUNCTIONS
# =============================================================================

def save_bet(bet_data: Dict[str, Any], user_id: str = "default_user") -> bool:
    """Save a new bet to Supabase."""
    client = get_supabase_client()
    
    if not client:
        st.warning("⚠️ Database not connected. Bet not saved.")
        return False
    
    try:
        bet_data["user_id"] = user_id
        bet_data["created_at"] = datetime.now().isoformat()
        
        client.table("bets").insert(bet_data).execute()
        
        # Clear bets cache
        load_bets.clear()
        
        return True
    except Exception as e:
        st.error(f"❌ Error saving bet: {e}")
        return False


def update_bankroll(user_id: str, amount: float, operation: str = "set") -> bool:
    """Update user bankroll."""
    client = get_supabase_client()
    
    if not client:
        return False
    
    try:
        if operation == "set":
            client.table("bankroll")\
                .update({"balance": amount, "updated_at": datetime.now().isoformat()})\
                .eq("user_id", user_id)\
                .execute()
        elif operation == "add":
            result = client.table("bankroll")\
                .select("balance")\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            current = result.data.get("balance", 0) if result.data else 0
            new_balance = current + amount
            
            client.table("bankroll")\
                .update({"balance": new_balance, "updated_at": datetime.now().isoformat()})\
                .eq("user_id", user_id)\
                .execute()
        
        # Clear cache
        load_bets.clear()
        
        return True
    except Exception as e:
        st.error(f"❌ Error updating bankroll: {e}")
        return False


def settle_bet(bet_id: str, result: str, profit: float) -> bool:
    """Settle a bet (won/lost/void)."""
    client = get_supabase_client()
    
    if not client:
        return False
    
    try:
        client.table("bets")\
            .update({
                "status": result,
                "result": result,
                "profit": profit,
                "settled_at": datetime.now().isoformat()
            })\
            .eq("id", bet_id)\
            .execute()
        
        # Clear cache
        load_bets.clear()
        
        return True
    except Exception:
        return False


# =============================================================================
# STATISTICS FUNCTIONS
# =============================================================================

@st.cache_data(ttl=300)
def get_team_head_to_head(team_a_id: int, team_b_id: int) -> Dict[str, Any]:
    """Get head-to-head statistics between two teams."""
    client = get_supabase_client()
    
    if not client:
        return {"error": "Database not connected"}
    
    try:
        # Get matches where team_a played against team_b
        result = client.table("matches")\
            .select("*")\
            .eq("team_id", team_a_id)\
            .eq("opponent_team_id", team_b_id)\
            .execute()
        
        matches = result.data if result.data else []
        
        team_a_wins = sum(1 for m in matches if m.get("won"))
        team_b_wins = len(matches) - team_a_wins
        
        return {
            "total_matches": len(matches),
            "team_a_wins": team_a_wins,
            "team_b_wins": team_b_wins,
            "matches": matches[:10]  # Last 10 matches
        }
    except Exception:
        return {"error": "Failed to fetch H2H data"}


@st.cache_data(ttl=300)
def get_team_recent_form(team_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Get team's recent match results."""
    client = get_supabase_client()
    
    if not client:
        return []
    
    try:
        result = client.table("matches")\
            .select("*")\
            .eq("team_id", team_id)\
            .order("start_time", desc=True)\
            .limit(limit)\
            .execute()
        
        return result.data if result.data else []
    except Exception:
        return []


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_data_source() -> str:
    """Return current data source indicator."""
    if is_supabase_connected():
        return "🟢 Supabase"
    else:
        return "🟡 JSON (Offline)"


def clear_all_caches():
    """Clear all cached data."""
    load_tournaments.clear()
    load_dreamleague.clear()
    load_pro_teams.clear()
    load_pro_players.clear()
    load_schedule.clear()
    load_bets.clear()
    get_team_head_to_head.clear()
    get_team_recent_form.clear()
