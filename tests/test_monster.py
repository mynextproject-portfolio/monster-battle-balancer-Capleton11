"""
Tests for the Monster model class.

These tests cover:
- Fail-fast validation (required fields)
- Raw attribute access (hp, ac, strength, name, image_url)
- String representations
"""

import pytest
from models.monster import Monster
from models.attack import Attack


def _monster_data(actions, **overrides):
    """Build valid base monster data with the given actions list.

    Keeps the required hp/ac/strength fields satisfied so tests can focus on
    attack parsing.
    """
    data = {
        "name": "Test Monster",
        "hit_points": 10,
        "armor_class": [{"value": 12}],
        "strength": 10,
        "actions": actions,
    }
    data.update(overrides)
    return data


# Realistic API-shaped actions for reuse in tests
SCIMITAR = {
    "name": "Scimitar",
    "attack_bonus": 4,
    "damage": [
        {"damage_type": {"name": "Slashing"}, "damage_dice": "1d6+2"},
    ],
}
MULTIATTACK = {
    "name": "Multiattack",
    "desc": "The monster makes two attacks.",
    "damage": [],  # present but empty, and crucially no attack_bonus
}
FIRE_BREATH = {  # save-based ability: has damage + dc but no attack_bonus
    "name": "Fire Breath",
    "dc": {"dc_value": 21},
    "damage": [{"damage_type": {"name": "Fire"}, "damage_dice": "26d6"}],
}


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


class TestMonsterAttack:
    """Test parsing a monster's attack (to-hit + damage) from API actions."""

    def test_simple_attack_is_parsed(self):
        """A straightforward attack exposes its to-hit and damage."""
        monster = Monster(_monster_data([SCIMITAR]))

        assert monster.attack is not None
        assert monster.attack.name == "Scimitar"
        assert monster.attack.to_hit == 4
        assert monster.attack.damage_dice == "1d6+2"
        assert monster.attack.damage_type == "Slashing"

    def test_multiattack_is_skipped(self):
        """Multiattack (no attack_bonus) is not treated as an attack."""
        monster = Monster(_monster_data([MULTIATTACK, SCIMITAR]))

        # The real attack after Multiattack is selected, not Multiattack.
        assert monster.attack is not None
        assert monster.attack.name == "Scimitar"

    def test_save_based_ability_is_skipped(self):
        """A save-based ability (DC, no attack_bonus) is not an attack."""
        monster = Monster(_monster_data([MULTIATTACK, FIRE_BREATH]))

        # Neither Multiattack nor Fire Breath is a to-hit attack.
        assert monster.attack is None

    def test_monster_with_no_actions_has_no_attack(self):
        """A monster with no actions exposes attack == None, not an error."""
        data = _monster_data([])
        del data["actions"]  # actions key entirely absent

        monster = Monster(data)

        assert monster.attack is None

    def test_first_real_attack_is_chosen(self):
        """When several attacks exist, the first real attack wins."""
        bite = {
            "name": "Bite",
            "attack_bonus": 17,
            "damage": [
                {"damage_type": {"name": "Piercing"}, "damage_dice": "2d10+10"},
                {"damage_type": {"name": "Fire"}, "damage_dice": "4d6"},
            ],
        }
        monster = Monster(_monster_data([MULTIATTACK, bite, SCIMITAR]))

        assert monster.attack.name == "Bite"
        # Multi-type attack: the primary (first) damage entry is used.
        assert monster.attack.damage_dice == "2d10+10"
        assert monster.attack.damage_type == "Piercing"

    def test_attack_with_no_damage_dice_is_skipped(self):
        """An attack_bonus action with no rollable damage isn't usable."""
        no_damage = {"name": "Grapple", "attack_bonus": 5, "damage": []}
        monster = Monster(_monster_data([no_damage, SCIMITAR]))

        assert monster.attack.name == "Scimitar"

    def test_attack_does_not_affect_required_fields(self):
        """Parsing attacks leaves hp/ac/strength behaviour unchanged."""
        monster = Monster(_monster_data([SCIMITAR]))

        assert monster.hp == 10
        assert monster.ac == 12
        assert monster.strength == 10


class TestAttackFromActions:
    """Test the Attack.from_actions selection logic directly."""

    def test_returns_none_for_empty_or_missing(self):
        assert Attack.from_actions([]) is None
        assert Attack.from_actions(None) is None

    def test_picks_first_real_attack(self):
        attack = Attack.from_actions([MULTIATTACK, SCIMITAR])
        assert isinstance(attack, Attack)
        assert attack.name == "Scimitar"
