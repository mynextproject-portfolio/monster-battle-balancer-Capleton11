"""
Tests for the Monster model class.

These tests cover:
- Fail-fast validation (required fields)
- Raw attribute access (hp, ac, strength, name, image_url)
- String representations
"""

import pytest
from models.monster import Monster


class TestMonsterInitialization:
    """Test Monster initialization and validation."""

    def test_successful_initialization_with_valid_data(self):
        """Test that a Monster can be created with all required fields."""
        data = {
            "index": "goblin",
            "name": "Goblin",
            "hit_points": 7,
            "armor_class": [{"value": 15}],
            "strength": 8,
            "full_image_url": "https://example.com/goblin.png"
        }

        monster = Monster(data)

        assert monster.index == "goblin"
        assert monster.name == "Goblin"
        assert monster.hp == 7
        assert monster.ac == 15
        assert monster.strength == 8
        assert monster.image_url == "https://example.com/goblin.png"

    def test_initialization_with_defaults(self):
        """Test that optional fields use sensible defaults."""
        data = {
            "name": "Test Monster",
            "hit_points": 50,
            "armor_class": [{"value": 12}],
            "strength": 10,
            # No index or image_url
        }

        monster = Monster(data)

        assert monster.index == ""
        assert monster.image_url is None


class TestMonsterValidation:
    """Test fail-fast validation for required fields."""

    def test_missing_hit_points_raises_error(self):
        """Test that missing hit_points raises ValueError immediately."""
        data = {
            "name": "Invalid Monster",
            # Missing hit_points
            "armor_class": [{"value": 12}],
            "strength": 10,
        }

        with pytest.raises(ValueError, match="missing required 'hit_points'"):
            Monster(data)

    def test_missing_armor_class_raises_error(self):
        """Test that missing armor_class raises ValueError immediately."""
        data = {
            "name": "Invalid Monster",
            "hit_points": 50,
            # Missing armor_class
            "strength": 10,
        }

        with pytest.raises(ValueError, match="missing required 'armor_class'"):
            Monster(data)

    def test_missing_strength_raises_error(self):
        """Test that missing strength raises ValueError immediately."""
        data = {
            "name": "Invalid Monster",
            "hit_points": 50,
            "armor_class": [{"value": 12}],
            # Missing strength
        }

        with pytest.raises(ValueError, match="missing required 'strength'"):
            Monster(data)


class TestStringRepresentations:
    """Test __str__ and __repr__ methods."""

    def test_str_returns_name(self):
        """Test that str(monster) returns the monster name."""
        data = {
            "name": "Ancient Dragon",
            "hit_points": 500,
            "armor_class": [{"value": 22}],
            "strength": 27,
        }

        monster = Monster(data)

        assert str(monster) == "Ancient Dragon"

    def test_repr_shows_key_attributes(self):
        """Test that repr(monster) shows name, hp, and ac."""
        data = {
            "name": "Goblin",
            "hit_points": 7,
            "armor_class": [{"value": 15}],
            "strength": 8,
        }

        monster = Monster(data)

        assert repr(monster) == "Monster(name='Goblin', hp=7, ac=15)"
