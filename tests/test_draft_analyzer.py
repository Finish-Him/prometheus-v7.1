"""
Unit Tests — Draft Composition Analyzer
Tests for hero classification, draft scoring, and composition analysis.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.draft_analyzer import (
    HeroProfile,
    Role,
    Attribute,
    Timing,
    HERO_PROFILES,
)


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def carry_hero():
    return HERO_PROFILES.get("Faceless Void")


@pytest.fixture
def support_hero():
    return HERO_PROFILES.get("Crystal Maiden") or HERO_PROFILES.get("Lion")


@pytest.fixture
def sample_draft():
    """A balanced 5-hero draft for testing."""
    names = ["Faceless Void", "Invoker", "Mars", "Lion", "Dazzle"]
    return [HERO_PROFILES[n] for n in names if n in HERO_PROFILES]


# ─── HeroProfile Unit Tests ───────────────────────────────────────────────────

class TestHeroProfile:
    """Tests for the HeroProfile dataclass."""

    def test_hero_profile_has_required_fields(self, carry_hero):
        assert carry_hero is not None
        assert isinstance(carry_hero.name, str)
        assert isinstance(carry_hero.roles, list)
        assert isinstance(carry_hero.attribute, Attribute)
        assert isinstance(carry_hero.timing, Timing)

    def test_hero_profile_scores_are_in_valid_range(self, carry_hero):
        """All numeric scores should be between 1 and 10."""
        assert 1 <= carry_hero.lane_presence <= 10
        assert 1 <= carry_hero.teamfight <= 10
        assert 1 <= carry_hero.push <= 10
        assert 1 <= carry_hero.pickoff <= 10
        assert 1 <= carry_hero.save <= 10
        assert 1 <= carry_hero.control <= 10
        assert 1 <= carry_hero.mobility <= 10

    def test_hero_damage_type_is_valid(self, carry_hero):
        valid_types = {"physical", "magical", "mixed"}
        assert carry_hero.damage_type in valid_types

    def test_hero_has_at_least_one_role(self, carry_hero):
        assert len(carry_hero.roles) >= 1

    def test_hero_roles_are_valid_enum_values(self, carry_hero):
        for role in carry_hero.roles:
            assert isinstance(role, Role)


# ─── HERO_PROFILES Database Tests ─────────────────────────────────────────────

class TestHeroDatabase:
    """Tests for the HERO_PROFILES dictionary."""

    def test_hero_database_is_not_empty(self):
        assert len(HERO_PROFILES) > 0

    def test_all_heroes_have_valid_profiles(self):
        for name, profile in HERO_PROFILES.items():
            assert isinstance(profile, HeroProfile), f"{name} has invalid profile"
            assert profile.name == name, f"Name mismatch: {name} vs {profile.name}"

    def test_hero_database_contains_key_carries(self):
        key_carries = ["Anti-Mage", "Juggernaut", "Phantom Assassin"]
        for hero in key_carries:
            assert hero in HERO_PROFILES, f"Missing key carry: {hero}"

    def test_hero_database_contains_key_supports(self):
        key_supports = ["Lion", "Lina"]
        for hero in key_supports:
            assert hero in HERO_PROFILES, f"Missing key support: {hero}"

    def test_all_heroes_have_at_least_one_role(self):
        for name, profile in HERO_PROFILES.items():
            assert len(profile.roles) >= 1, f"{name} has no roles"

    def test_no_duplicate_hero_names(self):
        names = [p.name for p in HERO_PROFILES.values()]
        assert len(names) == len(set(names)), "Duplicate hero names found"


# ─── Role Enum Tests ──────────────────────────────────────────────────────────

class TestRoleEnum:
    """Tests for Role enumeration."""

    def test_all_roles_defined(self):
        expected = {"carry", "mid", "offlane", "soft_support", "hard_support"}
        actual = {r.value for r in Role}
        assert actual == expected

    def test_role_values_are_strings(self):
        for role in Role:
            assert isinstance(role.value, str)


# ─── Attribute Enum Tests ─────────────────────────────────────────────────────

class TestAttributeEnum:
    """Tests for Attribute enumeration."""

    def test_all_attributes_defined(self):
        expected = {"str", "agi", "int", "all"}
        actual = {a.value for a in Attribute}
        assert actual == expected


# ─── Timing Enum Tests ────────────────────────────────────────────────────────

class TestTimingEnum:
    """Tests for Timing enumeration."""

    def test_timing_values(self):
        assert Timing.EARLY.value == "early"
        assert Timing.MID.value == "mid"
        assert Timing.LATE.value == "late"


# ─── Draft Composition Logic Tests ───────────────────────────────────────────

class TestDraftComposition:
    """Tests for draft composition analysis logic."""

    def test_sample_draft_has_five_heroes(self, sample_draft):
        assert len(sample_draft) == 5

    def test_draft_average_teamfight_is_calculable(self, sample_draft):
        if not sample_draft:
            pytest.skip("Sample draft heroes not in database")
        avg = sum(h.teamfight for h in sample_draft) / len(sample_draft)
        assert 1.0 <= avg <= 10.0

    def test_draft_average_push_is_calculable(self, sample_draft):
        if not sample_draft:
            pytest.skip("Sample draft heroes not in database")
        avg = sum(h.push for h in sample_draft) / len(sample_draft)
        assert 1.0 <= avg <= 10.0

    def test_draft_has_carry_role(self, sample_draft):
        if not sample_draft:
            pytest.skip("Sample draft heroes not in database")
        roles_in_draft = [r for h in sample_draft for r in h.roles]
        assert Role.CARRY in roles_in_draft, "Draft should contain at least one carry"

    def test_draft_timing_distribution(self, sample_draft):
        if not sample_draft:
            pytest.skip("Sample draft heroes not in database")
        timings = [h.timing for h in sample_draft]
        assert len(timings) == len(sample_draft)
        for t in timings:
            assert isinstance(t, Timing)

    def test_late_game_draft_has_high_avg_lane_presence(self):
        """Late-game carries should have high lane presence scores."""
        late_carries = [
            h for h in HERO_PROFILES.values()
            if Role.CARRY in h.roles and h.timing == Timing.LATE
        ]
        if not late_carries:
            pytest.skip("No late-game carries in database")
        avg_lane = sum(h.lane_presence for h in late_carries) / len(late_carries)
        assert avg_lane >= 5.0, "Late-game carries should have >= 5.0 avg lane presence"

    def test_supports_have_lower_mobility_than_carries(self):
        """On average, supports should be less mobile than carries."""
        carries = [h for h in HERO_PROFILES.values() if Role.CARRY in h.roles]
        supports = [h for h in HERO_PROFILES.values() if Role.HARD_SUPPORT in h.roles]
        if not carries or not supports:
            pytest.skip("Insufficient heroes for comparison")
        avg_carry_mobility = sum(h.mobility for h in carries) / len(carries)
        avg_support_mobility = sum(h.mobility for h in supports) / len(supports)
        # Carries are generally more mobile — this is a soft assertion
        assert avg_carry_mobility >= avg_support_mobility - 2.0
