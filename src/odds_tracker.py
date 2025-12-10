"""
Prometheus V7.3 - Odds Tracker
Register and track betting odds from various bookmakers.
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import pytz

SP_TZ = pytz.timezone('America/Sao_Paulo')

# Odds storage file
ODDS_FILE = Path(__file__).parent.parent / "Database" / "Json" / "odds" / "dreamleague_odds.json"


class OddsTracker:
    """Track and analyze betting odds for DreamLeague matches."""
    
    # Common bookmakers
    BOOKMAKERS = [
        "bet365",
        "Betano",
        "Betfair",
        "Pinnacle",
        "1xBet",
        "Rivalry",
        "Thunderpick",
        "GG.bet",
        "Stake"
    ]
    
    def __init__(self):
        self.odds_file = ODDS_FILE
        self.odds_file.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load_odds()
    
    def _load_odds(self) -> Dict:
        """Load odds from file."""
        if self.odds_file.exists():
            with open(self.odds_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"matches": {}, "history": []}
    
    def _save_odds(self):
        """Save odds to file."""
        with open(self.odds_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def register_odds(
        self,
        match_id: str,
        team_a: str,
        team_b: str,
        bookmaker: str,
        odds_a: float,
        odds_b: float,
        match_date: str = None
    ) -> Dict:
        """Register odds for a match."""
        
        timestamp = datetime.now(SP_TZ).isoformat()
        
        # Create or update match entry
        if match_id not in self.data["matches"]:
            self.data["matches"][match_id] = {
                "team_a": team_a,
                "team_b": team_b,
                "match_date": match_date,
                "created": timestamp,
                "odds": {}
            }
        
        match = self.data["matches"][match_id]
        
        # Calculate implied probability
        implied_a = 1 / odds_a * 100 if odds_a > 0 else 0
        implied_b = 1 / odds_b * 100 if odds_b > 0 else 0
        overround = implied_a + implied_b - 100
        
        # Store odds for bookmaker
        if bookmaker not in match["odds"]:
            match["odds"][bookmaker] = []
        
        odds_entry = {
            "timestamp": timestamp,
            "odds_a": odds_a,
            "odds_b": odds_b,
            "implied_a": round(implied_a, 2),
            "implied_b": round(implied_b, 2),
            "overround": round(overround, 2)
        }
        
        match["odds"][bookmaker].append(odds_entry)
        
        # Add to history
        self.data["history"].append({
            "match_id": match_id,
            "bookmaker": bookmaker,
            **odds_entry
        })
        
        self._save_odds()
        
        return {
            "success": True,
            "match_id": match_id,
            "bookmaker": bookmaker,
            "odds": odds_entry
        }
    
    def get_match_odds(self, match_id: str) -> Optional[Dict]:
        """Get all odds for a match."""
        return self.data["matches"].get(match_id)
    
    def get_best_odds(self, match_id: str) -> Dict:
        """Get best available odds across all bookmakers."""
        match = self.data["matches"].get(match_id)
        if not match:
            return {"error": "Match not found"}
        
        best_a = {"odds": 0, "bookmaker": None}
        best_b = {"odds": 0, "bookmaker": None}
        
        for bookmaker, entries in match["odds"].items():
            if entries:
                latest = entries[-1]  # Most recent
                if latest["odds_a"] > best_a["odds"]:
                    best_a = {"odds": latest["odds_a"], "bookmaker": bookmaker}
                if latest["odds_b"] > best_b["odds"]:
                    best_b = {"odds": latest["odds_b"], "bookmaker": bookmaker}
        
        return {
            "team_a": match["team_a"],
            "team_b": match["team_b"],
            "best_odds_a": best_a,
            "best_odds_b": best_b
        }
    
    def get_odds_movement(self, match_id: str, bookmaker: str = None) -> List[Dict]:
        """Get odds movement history for a match."""
        match = self.data["matches"].get(match_id)
        if not match:
            return []
        
        if bookmaker:
            return match["odds"].get(bookmaker, [])
        
        # Combine all bookmakers
        all_movements = []
        for bm, entries in match["odds"].items():
            for entry in entries:
                all_movements.append({"bookmaker": bm, **entry})
        
        return sorted(all_movements, key=lambda x: x["timestamp"])
    
    def calculate_value(
        self,
        match_id: str,
        predicted_prob_a: float,
        predicted_prob_b: float = None
    ) -> Dict:
        """Calculate value bets based on predicted probabilities."""
        
        if predicted_prob_b is None:
            predicted_prob_b = 100 - predicted_prob_a
        
        best = self.get_best_odds(match_id)
        if "error" in best:
            return best
        
        # Calculate expected value
        best_odds_a = best["best_odds_a"]["odds"]
        best_odds_b = best["best_odds_b"]["odds"]
        
        ev_a = (predicted_prob_a / 100) * (best_odds_a - 1) - (1 - predicted_prob_a / 100)
        ev_b = (predicted_prob_b / 100) * (best_odds_b - 1) - (1 - predicted_prob_b / 100)
        
        value_a = predicted_prob_a - (100 / best_odds_a) if best_odds_a > 0 else 0
        value_b = predicted_prob_b - (100 / best_odds_b) if best_odds_b > 0 else 0
        
        return {
            "team_a": {
                "name": best["team_a"],
                "best_odds": best_odds_a,
                "bookmaker": best["best_odds_a"]["bookmaker"],
                "predicted_prob": predicted_prob_a,
                "implied_prob": round(100 / best_odds_a, 2) if best_odds_a > 0 else 0,
                "value": round(value_a, 2),
                "ev": round(ev_a, 4),
                "is_value": value_a > 0
            },
            "team_b": {
                "name": best["team_b"],
                "best_odds": best_odds_b,
                "bookmaker": best["best_odds_b"]["bookmaker"],
                "predicted_prob": predicted_prob_b,
                "implied_prob": round(100 / best_odds_b, 2) if best_odds_b > 0 else 0,
                "value": round(value_b, 2),
                "ev": round(ev_b, 4),
                "is_value": value_b > 0
            }
        }
    
    def get_all_matches(self) -> List[Dict]:
        """Get all matches with odds summary."""
        matches = []
        for match_id, match in self.data["matches"].items():
            # Get latest odds from each bookmaker
            latest_odds = {}
            for bm, entries in match["odds"].items():
                if entries:
                    latest_odds[bm] = entries[-1]
            
            matches.append({
                "match_id": match_id,
                "team_a": match["team_a"],
                "team_b": match["team_b"],
                "match_date": match.get("match_date"),
                "bookmakers_count": len(match["odds"]),
                "latest_odds": latest_odds
            })
        
        return matches
    
    def clear_old_odds(self, days: int = 7):
        """Remove odds older than N days."""
        from datetime import timedelta
        cutoff = datetime.now(SP_TZ) - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        removed = 0
        for match_id, match in list(self.data["matches"].items()):
            if match.get("match_date") and match["match_date"] < cutoff_str[:10]:
                del self.data["matches"][match_id]
                removed += 1
        
        self._save_odds()
        return removed


def decimal_to_american(decimal_odds: float) -> int:
    """Convert decimal odds to American format."""
    if decimal_odds >= 2.0:
        return int((decimal_odds - 1) * 100)
    else:
        return int(-100 / (decimal_odds - 1))


def american_to_decimal(american_odds: int) -> float:
    """Convert American odds to decimal format."""
    if american_odds > 0:
        return (american_odds / 100) + 1
    else:
        return (100 / abs(american_odds)) + 1


def implied_probability(decimal_odds: float) -> float:
    """Calculate implied probability from decimal odds."""
    return (1 / decimal_odds) * 100 if decimal_odds > 0 else 0


def calculate_kelly(prob: float, odds: float) -> float:
    """Calculate Kelly Criterion stake percentage."""
    # Kelly = (bp - q) / b
    # b = decimal odds - 1
    # p = probability of winning
    # q = probability of losing (1 - p)
    b = odds - 1
    p = prob / 100
    q = 1 - p
    
    kelly = (b * p - q) / b if b > 0 else 0
    return max(0, kelly) * 100  # Return as percentage


# Singleton instance
_tracker = None

def get_tracker() -> OddsTracker:
    """Get or create OddsTracker singleton."""
    global _tracker
    if _tracker is None:
        _tracker = OddsTracker()
    return _tracker
