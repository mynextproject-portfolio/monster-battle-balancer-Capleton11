"""
Integration tests for API → Monster pipeline.

These tests make real API calls to verify that:
1. We can fetch monster data from the D&D 5e API
2. The Monster class correctly parses and validates API responses
3. All computed properties work with real data

Note: These tests require internet connection and are slower than unit tests.
Run with: pytest tests/test_integration_api.py -v
Skip with: pytest -m "not integration"
"""

import pytest
from dnd_api import get_monster_details


@pytest.mark.integration
class TestMonsterCreationFromAPI:
    """Test creating Monster objects from real API data."""
    
    def test_create_goblin_from_api(self):
        """Test fetching and creating a Goblin from the API."""
        # Fetch real Goblin data from D&D API
        goblin = get_monster_details('goblin')
        
        # Verify basic attributes
        assert goblin is not None
        assert goblin.name == "Goblin"
        assert goblin.index == "goblin"
        
        # Verify required fields were parsed
        assert goblin.hp == 7
        assert goblin.ac == 15
        assert goblin.strength == 8
    
    def test_create_ancient_dragon_from_api(self):
        """Test fetching a powerful creature with large stats."""
        # Ancient Red Dragon has very high stats
        dragon = get_monster_details('ancient-red-dragon')
        
        assert dragon is not None
        assert dragon.name == "Ancient Red Dragon"
        
        # Ancient dragons have massive HP
        assert dragon.hp > 400
        
        # Very high armor class
        assert dragon.ac >= 20
        
        # Legendary strength
        assert dragon.strength >= 20
    
    def test_create_commoner_from_api(self):
        """Test fetching a weak creature (Commoner has minimal stats)."""
        commoner = get_monster_details('commoner')
        
        assert commoner is not None
        assert commoner.name == "Commoner"
        
        # Commoners are weak
        assert commoner.hp <= 10
        assert commoner.ac <= 12
        
        # Average strength (around 10)
        assert 8 <= commoner.strength <= 12
    
    def test_monster_image_url_available(self):
        """Test that monster images are available from API."""
        # Not all monsters have images, but some do
        goblin = get_monster_details('goblin')
        
        # Image URL might be None or a valid URL
        # Just verify the attribute exists and doesn't crash
        image_url = goblin.image_url
        assert image_url is None or isinstance(image_url, str)
    
    def test_multiple_monsters_can_be_created(self):
        """Test creating multiple different monsters from API."""
        # Create several different monsters
        monsters = [
            get_monster_details('goblin'),
            get_monster_details('kobold'),
            get_monster_details('orc'),
        ]
        
        # All should be created successfully
        assert all(m is not None for m in monsters)
        
        # Each should have different stats
        names = [m.name for m in monsters]
        assert len(set(names)) == 3  # All unique names
        
        # Each should have valid stats
        for monster in monsters:
            assert monster.hp > 0
            assert monster.ac > 0
            assert isinstance(monster.strength, int)


@pytest.mark.integration
class TestAPIErrorHandling:
    """Test how the system handles API errors."""
    
    def test_invalid_monster_index_returns_none(self):
        """Test that invalid monster index returns None gracefully."""
        # Try to fetch a monster that doesn't exist
        invalid_monster = get_monster_details('definitely-not-a-real-monster-12345')
        
        # Should return None, not crash
        assert invalid_monster is None
    
    def test_empty_string_returns_none(self):
        """Test that empty string returns None gracefully."""
        invalid_monster = get_monster_details('')
        assert invalid_monster is None

