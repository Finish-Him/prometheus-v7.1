"""
Unit Tests — Hero Mapper
Tests for hero ID resolution, name normalization, and attribute mapping.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.hero_mapper import HERO_DATA as HERO_MAP


# ─── Hero Map Structure Tests ─────────────────────────────────────────────────

class TestHeroMap:
    """Tests for the HERO_MAP dictionary."""

    def test_hero_map_is_not_empty(self):
        assert len(HERO_MAP) > 0

    def test_hero_map_keys_are_integers(self):
        for key in HERO_MAP.keys():
            assert isinstance(key, int), f"Key {key} is not an integer"

    def test_hero_map_values_have_required_fields(self):
        required_fields = {"name", "primary_attr", "attack_type", "roles"}
        for hero_id, hero_data in HERO_MAP.items():
            for field in required_fields:
                assert field in hero_data, f"Hero {hero_id} missing field: {field}"

    def test_hero_primary_attr_is_valid(self):
        valid_attrs = {"str", "agi", "int", "all"}
        for hero_id, hero_data in HERO_MAP.items():
            assert hero_data["primary_attr"] in valid_attrs, (
                f"Hero {hero_id} has invalid primary_attr: {hero_data['primary_attr']}"
            )

    def test_hero_attack_type_is_valid(self):
        valid_types = {"Melee", "Ranged"}
        for hero_id, hero_data in HERO_MAP.items():
            assert hero_data["attack_type"] in valid_types, (
                f"Hero {hero_id} has invalid attack_type: {hero_data['attack_type']}"
            )

    def test_hero_roles_is_list(self):
        for hero_id, hero_data in HERO_MAP.items():
            assert isinstance(hero_data["roles"], list), (
                f"Hero {hero_id} roles should be a list"
            )

    def test_hero_roles_are_non_empty(self):
        for hero_id, hero_data in HERO_MAP.items():
            assert len(hero_data["roles"]) > 0, (
                f"Hero {hero_id} has empty roles list"
            )

    def test_hero_names_are_strings(self):
        for hero_id, hero_data in HERO_MAP.items():
            assert isinstance(hero_data["name"], str), (
                f"Hero {hero_id} name is not a string"
            )
            assert len(hero_data["name"]) > 0, (
                f"Hero {hero_id} has empty name"
            )

    def test_hero_ids_are_positive(self):
        for hero_id in HERO_MAP.keys():
            assert hero_id > 0, f"Hero ID {hero_id} should be positive"

    def test_no_duplicate_hero_names(self):
        names = [data["name"] for data in HERO_MAP.values()]
        assert len(names) == len(set(names)), "Duplicate hero names found in HERO_MAP"


# ─── Hero Lookup Tests ────────────────────────────────────────────────────────

class TestHeroLookup:
    """Tests for hero lookup by ID."""

    def test_lookup_known_hero_by_id(self):
        """Hero ID 1 should be Anti-Mage."""
        hero = HERO_MAP.get(1)
        assert hero is not None
        assert hero["name"] == "Anti-Mage"

    def test_lookup_axe_by_id(self):
        """Hero ID 2 should be Axe."""
        hero = HERO_MAP.get(2)
        assert hero is not None
        assert hero["name"] == "Axe"

    def test_lookup_nonexistent_hero_returns_none(self):
        hero = HERO_MAP.get(99999)
        assert hero is None

    def test_lookup_zero_id_returns_none(self):
        hero = HERO_MAP.get(0)
        assert hero is None


# ─── Attribute Distribution Tests ─────────────────────────────────────────────

class TestAttributeDistribution:
    """Tests for hero attribute distribution in the database."""

    def test_database_has_all_three_main_attributes(self):
        attrs = {data["primary_attr"] for data in HERO_MAP.values()}
        assert "str" in attrs, "No Strength heroes found"
        assert "agi" in attrs, "No Agility heroes found"
        assert "int" in attrs, "No Intelligence heroes found"

    def test_database_has_melee_and_ranged_heroes(self):
        attack_types = {data["attack_type"] for data in HERO_MAP.values()}
        assert "Melee" in attack_types
        assert "Ranged" in attack_types

    def test_carry_role_exists_in_database(self):
        carries = [d for d in HERO_MAP.values() if "Carry" in d["roles"]]
        assert len(carries) > 0, "No carries found in hero database"

    def test_support_role_exists_in_database(self):
        supports = [d for d in HERO_MAP.values() if "Support" in d["roles"]]
        assert len(supports) > 0, "No supports found in hero database"
