"""
Prometheus V7.3 - Draft Composition Analyzer
Analyzes draft picks and predicts game dynamics.
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class Role(Enum):
    CARRY = "carry"
    MID = "mid"
    OFFLANE = "offlane"
    SOFT_SUPPORT = "soft_support"
    HARD_SUPPORT = "hard_support"


class Attribute(Enum):
    STRENGTH = "str"
    AGILITY = "agi"
    INTELLIGENCE = "int"
    UNIVERSAL = "all"


class Timing(Enum):
    EARLY = "early"      # 0-20 min
    MID = "mid"          # 20-35 min
    LATE = "late"        # 35+ min


@dataclass
class HeroProfile:
    """Hero draft profile for analysis."""
    name: str
    roles: List[Role]
    attribute: Attribute
    timing: Timing
    lane_presence: float  # 1-10
    teamfight: float      # 1-10
    push: float           # 1-10
    pickoff: float        # 1-10
    save: float           # 1-10
    control: float        # 1-10
    damage_type: str      # "physical", "magical", "mixed"
    mobility: float       # 1-10


# Hero database with profiles (top meta heroes)
HERO_PROFILES: Dict[str, HeroProfile] = {
    # Carries
    "Faceless Void": HeroProfile("Faceless Void", [Role.CARRY], Attribute.AGILITY, Timing.LATE, 6, 10, 4, 5, 2, 9, "physical", 8),
    "Phantom Assassin": HeroProfile("Phantom Assassin", [Role.CARRY], Attribute.AGILITY, Timing.MID, 7, 6, 5, 8, 1, 2, "physical", 7),
    "Morphling": HeroProfile("Morphling", [Role.CARRY], Attribute.AGILITY, Timing.LATE, 7, 5, 6, 8, 2, 3, "mixed", 9),
    "Terrorblade": HeroProfile("Terrorblade", [Role.CARRY], Attribute.AGILITY, Timing.LATE, 8, 5, 10, 3, 1, 2, "physical", 4),
    "Medusa": HeroProfile("Medusa", [Role.CARRY], Attribute.AGILITY, Timing.LATE, 9, 7, 6, 2, 1, 5, "physical", 3),
    "Luna": HeroProfile("Luna", [Role.CARRY], Attribute.AGILITY, Timing.MID, 7, 8, 9, 4, 1, 2, "physical", 5),
    "Juggernaut": HeroProfile("Juggernaut", [Role.CARRY], Attribute.AGILITY, Timing.MID, 7, 6, 7, 7, 3, 2, "physical", 5),
    "Lifestealer": HeroProfile("Lifestealer", [Role.CARRY], Attribute.STRENGTH, Timing.MID, 7, 5, 5, 6, 2, 1, "physical", 6),
    "Slark": HeroProfile("Slark", [Role.CARRY], Attribute.AGILITY, Timing.MID, 6, 4, 4, 9, 4, 3, "physical", 9),
    "Anti-Mage": HeroProfile("Anti-Mage", [Role.CARRY], Attribute.AGILITY, Timing.LATE, 8, 4, 8, 6, 1, 1, "physical", 10),
    "Naga Siren": HeroProfile("Naga Siren", [Role.CARRY], Attribute.AGILITY, Timing.LATE, 9, 6, 10, 4, 3, 5, "physical", 5),
    "Spectre": HeroProfile("Spectre", [Role.CARRY], Attribute.AGILITY, Timing.LATE, 5, 9, 3, 7, 1, 2, "physical", 10),
    "Drow Ranger": HeroProfile("Drow Ranger", [Role.CARRY], Attribute.AGILITY, Timing.MID, 8, 5, 8, 5, 1, 4, "physical", 3),
    
    # Mids
    "Invoker": HeroProfile("Invoker", [Role.MID], Attribute.UNIVERSAL, Timing.MID, 7, 9, 6, 7, 4, 8, "mixed", 6),
    "Storm Spirit": HeroProfile("Storm Spirit", [Role.MID], Attribute.INTELLIGENCE, Timing.MID, 6, 6, 4, 10, 2, 5, "magical", 10),
    "Queen of Pain": HeroProfile("Queen of Pain", [Role.MID], Attribute.INTELLIGENCE, Timing.MID, 7, 8, 5, 8, 1, 3, "magical", 9),
    "Ember Spirit": HeroProfile("Ember Spirit", [Role.MID], Attribute.AGILITY, Timing.MID, 6, 7, 4, 8, 3, 4, "mixed", 9),
    "Leshrac": HeroProfile("Leshrac", [Role.MID], Attribute.INTELLIGENCE, Timing.MID, 8, 8, 10, 4, 1, 5, "magical", 5),
    "Templar Assassin": HeroProfile("Templar Assassin", [Role.MID], Attribute.AGILITY, Timing.MID, 7, 5, 8, 7, 1, 2, "physical", 6),
    "Shadow Fiend": HeroProfile("Shadow Fiend", [Role.MID], Attribute.AGILITY, Timing.MID, 8, 7, 7, 5, 1, 3, "mixed", 4),
    "Puck": HeroProfile("Puck", [Role.MID, Role.OFFLANE], Attribute.INTELLIGENCE, Timing.MID, 6, 8, 4, 7, 3, 7, "magical", 9),
    "Void Spirit": HeroProfile("Void Spirit", [Role.MID], Attribute.UNIVERSAL, Timing.MID, 6, 7, 4, 9, 3, 5, "magical", 10),
    "Lina": HeroProfile("Lina", [Role.MID, Role.SOFT_SUPPORT], Attribute.INTELLIGENCE, Timing.MID, 7, 7, 6, 6, 1, 4, "magical", 4),
    "Kunkka": HeroProfile("Kunkka", [Role.MID, Role.OFFLANE], Attribute.STRENGTH, Timing.MID, 7, 9, 5, 6, 2, 7, "physical", 5),
    
    # Offlaners
    "Mars": HeroProfile("Mars", [Role.OFFLANE], Attribute.STRENGTH, Timing.MID, 8, 10, 5, 5, 3, 9, "physical", 6),
    "Axe": HeroProfile("Axe", [Role.OFFLANE], Attribute.STRENGTH, Timing.EARLY, 8, 8, 4, 6, 2, 7, "physical", 5),
    "Legion Commander": HeroProfile("Legion Commander", [Role.OFFLANE], Attribute.STRENGTH, Timing.MID, 7, 5, 5, 8, 3, 4, "physical", 6),
    "Tidehunter": HeroProfile("Tidehunter", [Role.OFFLANE], Attribute.STRENGTH, Timing.MID, 8, 10, 5, 3, 2, 9, "magical", 4),
    "Centaur Warrunner": HeroProfile("Centaur Warrunner", [Role.OFFLANE], Attribute.STRENGTH, Timing.MID, 8, 8, 5, 5, 4, 6, "mixed", 7),
    "Enigma": HeroProfile("Enigma", [Role.OFFLANE], Attribute.INTELLIGENCE, Timing.MID, 7, 10, 8, 4, 2, 9, "magical", 4),
    "Sand King": HeroProfile("Sand King", [Role.OFFLANE, Role.SOFT_SUPPORT], Attribute.STRENGTH, Timing.MID, 7, 9, 4, 4, 2, 8, "magical", 7),
    "Beastmaster": HeroProfile("Beastmaster", [Role.OFFLANE], Attribute.UNIVERSAL, Timing.EARLY, 8, 7, 9, 6, 2, 6, "mixed", 5),
    "Primal Beast": HeroProfile("Primal Beast", [Role.OFFLANE], Attribute.STRENGTH, Timing.MID, 8, 9, 4, 6, 2, 8, "physical", 6),
    "Doom": HeroProfile("Doom", [Role.OFFLANE], Attribute.STRENGTH, Timing.MID, 7, 6, 5, 7, 1, 8, "mixed", 5),
    "Pangolier": HeroProfile("Pangolier", [Role.OFFLANE, Role.MID], Attribute.UNIVERSAL, Timing.MID, 7, 8, 4, 7, 3, 7, "physical", 9),
    
    # Supports
    "Crystal Maiden": HeroProfile("Crystal Maiden", [Role.HARD_SUPPORT], Attribute.INTELLIGENCE, Timing.EARLY, 6, 8, 3, 3, 2, 7, "magical", 2),
    "Lion": HeroProfile("Lion", [Role.HARD_SUPPORT, Role.SOFT_SUPPORT], Attribute.INTELLIGENCE, Timing.MID, 6, 7, 3, 6, 1, 9, "magical", 3),
    "Shadow Shaman": HeroProfile("Shadow Shaman", [Role.HARD_SUPPORT, Role.SOFT_SUPPORT], Attribute.INTELLIGENCE, Timing.EARLY, 7, 6, 10, 5, 1, 9, "magical", 2),
    "Witch Doctor": HeroProfile("Witch Doctor", [Role.HARD_SUPPORT], Attribute.INTELLIGENCE, Timing.MID, 6, 8, 4, 4, 3, 5, "magical", 3),
    "Dazzle": HeroProfile("Dazzle", [Role.HARD_SUPPORT], Attribute.INTELLIGENCE, Timing.MID, 7, 6, 5, 3, 10, 4, "physical", 3),
    "Oracle": HeroProfile("Oracle", [Role.HARD_SUPPORT], Attribute.INTELLIGENCE, Timing.MID, 6, 5, 3, 4, 10, 6, "magical", 3),
    "Chen": HeroProfile("Chen", [Role.HARD_SUPPORT], Attribute.INTELLIGENCE, Timing.EARLY, 8, 6, 9, 3, 8, 6, "mixed", 4),
    "Io": HeroProfile("Io", [Role.HARD_SUPPORT], Attribute.STRENGTH, Timing.MID, 6, 7, 5, 3, 10, 2, "magical", 8),
    "Treant Protector": HeroProfile("Treant Protector", [Role.HARD_SUPPORT], Attribute.STRENGTH, Timing.MID, 7, 8, 6, 3, 9, 6, "physical", 3),
    "Undying": HeroProfile("Undying", [Role.HARD_SUPPORT, Role.OFFLANE], Attribute.STRENGTH, Timing.EARLY, 9, 8, 5, 3, 3, 5, "physical", 3),
    
    # Soft Supports
    "Earth Spirit": HeroProfile("Earth Spirit", [Role.SOFT_SUPPORT], Attribute.STRENGTH, Timing.EARLY, 7, 7, 3, 7, 4, 9, "magical", 9),
    "Tusk": HeroProfile("Tusk", [Role.SOFT_SUPPORT], Attribute.STRENGTH, Timing.EARLY, 7, 6, 3, 8, 5, 6, "physical", 7),
    "Rubick": HeroProfile("Rubick", [Role.SOFT_SUPPORT], Attribute.INTELLIGENCE, Timing.MID, 5, 8, 3, 5, 4, 7, "magical", 5),
    "Snapfire": HeroProfile("Snapfire", [Role.SOFT_SUPPORT], Attribute.STRENGTH, Timing.MID, 7, 8, 5, 5, 4, 6, "mixed", 5),
    "Hoodwink": HeroProfile("Hoodwink", [Role.SOFT_SUPPORT], Attribute.AGILITY, Timing.MID, 6, 6, 4, 6, 3, 6, "mixed", 7),
    "Marci": HeroProfile("Marci", [Role.SOFT_SUPPORT, Role.OFFLANE], Attribute.UNIVERSAL, Timing.MID, 7, 7, 4, 8, 4, 6, "physical", 8),
    "Dark Willow": HeroProfile("Dark Willow", [Role.SOFT_SUPPORT], Attribute.INTELLIGENCE, Timing.MID, 6, 8, 3, 6, 3, 8, "magical", 6),
    "Phoenix": HeroProfile("Phoenix", [Role.SOFT_SUPPORT, Role.OFFLANE], Attribute.STRENGTH, Timing.MID, 7, 9, 4, 4, 5, 5, "magical", 6),
    "Elder Titan": HeroProfile("Elder Titan", [Role.SOFT_SUPPORT, Role.OFFLANE], Attribute.STRENGTH, Timing.MID, 7, 9, 4, 4, 3, 8, "mixed", 4),
}


class DraftAnalyzer:
    """Analyze draft compositions and predict game dynamics."""
    
    def __init__(self):
        self.heroes = HERO_PROFILES
    
    def get_hero_profile(self, hero_name: str) -> Optional[HeroProfile]:
        """Get hero profile by name (flexible matching)."""
        hero_name = hero_name.lower().strip()
        for name, profile in self.heroes.items():
            if name.lower() == hero_name or hero_name in name.lower():
                return profile
        return None
    
    def analyze_composition(self, picks: List[str]) -> Dict:
        """Analyze a team's draft composition."""
        profiles = [self.get_hero_profile(h) for h in picks]
        valid_profiles = [p for p in profiles if p is not None]
        
        if not valid_profiles:
            return {"error": "No valid heroes found"}
        
        # Calculate averages
        avg_teamfight = sum(p.teamfight for p in valid_profiles) / len(valid_profiles)
        avg_push = sum(p.push for p in valid_profiles) / len(valid_profiles)
        avg_pickoff = sum(p.pickoff for p in valid_profiles) / len(valid_profiles)
        avg_save = sum(p.save for p in valid_profiles) / len(valid_profiles)
        avg_control = sum(p.control for p in valid_profiles) / len(valid_profiles)
        avg_mobility = sum(p.mobility for p in valid_profiles) / len(valid_profiles)
        
        # Determine timing
        timings = [p.timing for p in valid_profiles]
        timing_counts = {t: timings.count(t) for t in Timing}
        primary_timing = max(timing_counts, key=timing_counts.get)
        
        # Damage type analysis
        damage_types = [p.damage_type for p in valid_profiles]
        physical_count = damage_types.count("physical")
        magical_count = damage_types.count("magical")
        
        if physical_count >= 4:
            damage_profile = "Heavily Physical"
        elif magical_count >= 4:
            damage_profile = "Heavily Magical"
        elif physical_count >= 3:
            damage_profile = "Physical Focused"
        elif magical_count >= 3:
            damage_profile = "Magical Focused"
        else:
            damage_profile = "Mixed Damage"
        
        # Win conditions
        win_conditions = []
        if avg_teamfight >= 7:
            win_conditions.append("5v5 Teamfights")
        if avg_push >= 7:
            win_conditions.append("Push/Siege")
        if avg_pickoff >= 7:
            win_conditions.append("Pickoffs/Ganks")
        if avg_control >= 7:
            win_conditions.append("Lockdown/Control")
        if avg_mobility >= 7:
            win_conditions.append("Split Push/Map Control")
        
        if not win_conditions:
            if primary_timing == Timing.EARLY:
                win_conditions.append("Early Aggression")
            elif primary_timing == Timing.LATE:
                win_conditions.append("Scale to Late Game")
            else:
                win_conditions.append("Mid-Game Power Spike")
        
        # Composition archetype
        archetype = self._determine_archetype(
            avg_teamfight, avg_push, avg_pickoff, 
            avg_control, primary_timing
        )
        
        return {
            "heroes": picks,
            "valid_count": len(valid_profiles),
            "archetype": archetype,
            "timing": primary_timing.value,
            "damage_profile": damage_profile,
            "win_conditions": win_conditions,
            "scores": {
                "teamfight": round(avg_teamfight, 1),
                "push": round(avg_push, 1),
                "pickoff": round(avg_pickoff, 1),
                "save": round(avg_save, 1),
                "control": round(avg_control, 1),
                "mobility": round(avg_mobility, 1)
            }
        }
    
    def _determine_archetype(
        self, 
        teamfight: float, 
        push: float, 
        pickoff: float,
        control: float,
        timing: Timing
    ) -> str:
        """Determine draft archetype."""
        
        if teamfight >= 8 and control >= 7:
            return "Wombo Combo"
        elif push >= 8:
            return "Deathball/Push"
        elif pickoff >= 8 and control >= 6:
            return "Gank/Pickoff"
        elif timing == Timing.LATE and teamfight >= 6:
            return "4 Protect 1"
        elif timing == Timing.EARLY and pickoff >= 6:
            return "Early Aggression"
        elif teamfight >= 7:
            return "Teamfight"
        else:
            return "Balanced/Flexible"
    
    def compare_drafts(
        self, 
        radiant_picks: List[str], 
        dire_picks: List[str]
    ) -> Dict:
        """Compare two draft compositions."""
        
        radiant = self.analyze_composition(radiant_picks)
        dire = self.analyze_composition(dire_picks)
        
        if "error" in radiant or "error" in dire:
            return {"error": "Could not analyze one or both drafts"}
        
        # Compare scores
        score_comparison = {}
        for metric in ["teamfight", "push", "pickoff", "save", "control", "mobility"]:
            r_score = radiant["scores"][metric]
            d_score = dire["scores"][metric]
            diff = r_score - d_score
            
            if diff > 1.5:
                advantage = "Radiant"
            elif diff < -1.5:
                advantage = "Dire"
            else:
                advantage = "Even"
            
            score_comparison[metric] = {
                "radiant": r_score,
                "dire": d_score,
                "advantage": advantage
            }
        
        # Overall advantage
        radiant_advantages = sum(1 for m in score_comparison.values() if m["advantage"] == "Radiant")
        dire_advantages = sum(1 for m in score_comparison.values() if m["advantage"] == "Dire")
        
        if radiant_advantages > dire_advantages + 1:
            draft_winner = "Radiant"
            draft_advantage = radiant_advantages - dire_advantages
        elif dire_advantages > radiant_advantages + 1:
            draft_winner = "Dire"
            draft_advantage = dire_advantages - radiant_advantages
        else:
            draft_winner = "Even"
            draft_advantage = 0
        
        # Timing analysis
        timing_advantage = self._compare_timing(radiant["timing"], dire["timing"])
        
        # Win probability estimation
        base_prob = 50
        prob_adjustment = draft_advantage * 3  # Each advantage = ~3%
        
        if draft_winner == "Radiant":
            radiant_prob = min(70, base_prob + prob_adjustment)
        elif draft_winner == "Dire":
            radiant_prob = max(30, base_prob - prob_adjustment)
        else:
            radiant_prob = 50
        
        return {
            "radiant": radiant,
            "dire": dire,
            "comparison": score_comparison,
            "draft_winner": draft_winner,
            "draft_advantage": draft_advantage,
            "timing_analysis": timing_advantage,
            "predicted_winner": draft_winner if draft_winner != "Even" else "Toss-up",
            "win_probability": {
                "radiant": radiant_prob,
                "dire": 100 - radiant_prob
            },
            "game_prediction": self._predict_game_dynamics(radiant, dire)
        }
    
    def _compare_timing(self, radiant_timing: str, dire_timing: str) -> Dict:
        """Compare timing advantages."""
        timing_order = {"early": 0, "mid": 1, "late": 2}
        
        r_order = timing_order.get(radiant_timing, 1)
        d_order = timing_order.get(dire_timing, 1)
        
        if r_order < d_order:
            return {
                "analysis": "Radiant wants early game, Dire wants late",
                "key_timing": f"15-25 min critical for Radiant",
                "advantage_early": "Radiant",
                "advantage_late": "Dire"
            }
        elif r_order > d_order:
            return {
                "analysis": "Dire wants early game, Radiant wants late",
                "key_timing": f"15-25 min critical for Dire",
                "advantage_early": "Dire",
                "advantage_late": "Radiant"
            }
        else:
            return {
                "analysis": f"Both teams peak at {radiant_timing} game",
                "key_timing": "Execution will determine outcome",
                "advantage_early": "Even",
                "advantage_late": "Even"
            }
    
    def _predict_game_dynamics(self, radiant: Dict, dire: Dict) -> Dict:
        """Predict how the game will play out."""
        
        # Duration prediction
        r_timing = radiant["timing"]
        d_timing = dire["timing"]
        
        if r_timing == "early" and d_timing == "early":
            duration = "Short (20-30 min)"
        elif r_timing == "late" and d_timing == "late":
            duration = "Long (40+ min)"
        elif radiant["scores"]["push"] >= 7 or dire["scores"]["push"] >= 7:
            duration = "Medium (30-40 min)"
        else:
            duration = "Variable (25-40 min)"
        
        # Kill prediction
        total_pickoff = radiant["scores"]["pickoff"] + dire["scores"]["pickoff"]
        total_control = radiant["scores"]["control"] + dire["scores"]["control"]
        
        if total_pickoff >= 14 and total_control >= 12:
            kill_prediction = "High kills (50+)"
        elif total_pickoff >= 12:
            kill_prediction = "Medium-High kills (40-50)"
        else:
            kill_prediction = "Standard kills (30-40)"
        
        # Objective control
        push_diff = radiant["scores"]["push"] - dire["scores"]["push"]
        if push_diff > 2:
            objective_control = "Radiant likely takes more objectives"
        elif push_diff < -2:
            objective_control = "Dire likely takes more objectives"
        else:
            objective_control = "Even objective trading expected"
        
        return {
            "predicted_duration": duration,
            "kill_prediction": kill_prediction,
            "objective_control": objective_control,
            "key_heroes_radiant": [radiant["heroes"][0]] if radiant["heroes"] else [],
            "key_heroes_dire": [dire["heroes"][0]] if dire["heroes"] else [],
            "watch_for": self._get_key_moments(radiant, dire)
        }
    
    def _get_key_moments(self, radiant: Dict, dire: Dict) -> List[str]:
        """Get key moments to watch for."""
        moments = []
        
        if radiant["archetype"] == "Wombo Combo" or dire["archetype"] == "Wombo Combo":
            moments.append("Big teamfight ultimates combo")
        
        if "Push/Siege" in radiant["win_conditions"] or "Push/Siege" in dire["win_conditions"]:
            moments.append("Early tower takes and HG sieges")
        
        if radiant["scores"]["pickoff"] >= 7 or dire["scores"]["pickoff"] >= 7:
            moments.append("Smoke ganks and pickoffs")
        
        if radiant["timing"] != dire["timing"]:
            moments.append("Critical timing window battles")
        
        if not moments:
            moments.append("Standard Dota 2 gameplay")
        
        return moments


# Convenience function
def analyze_draft(
    radiant_picks: List[str], 
    dire_picks: List[str]
) -> Dict:
    """Quick draft analysis."""
    analyzer = DraftAnalyzer()
    return analyzer.compare_drafts(radiant_picks, dire_picks)


def analyze_single_draft(picks: List[str]) -> Dict:
    """Analyze a single team's draft."""
    analyzer = DraftAnalyzer()
    return analyzer.analyze_composition(picks)
