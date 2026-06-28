import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
from models.monster import Monster

# Load environment variables from .env file
if not load_dotenv():
    raise RuntimeError("Failed to load .env file. Please ensure .env file exists with DND_API_BASE_URL and DND_API_IMAGE_BASE_URL")

BASE_URL = os.getenv("DND_API_BASE_URL")
IMAGE_BASE_URL = os.getenv("DND_API_IMAGE_BASE_URL")

if not BASE_URL or not IMAGE_BASE_URL:
    raise RuntimeError("Missing required environment variables: DND_API_BASE_URL and/or DND_API_IMAGE_BASE_URL. Check your .env file.")

def get_monsters() -> List[Dict]:
    """Fetch list of all monsters from D&D API.
    Returns list of dicts with 'index' and 'name' for dropdown selection.
    """
    try:
        response = requests.get(f"{BASE_URL}/monsters")
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except Exception as e:
        print(f"Error fetching monsters: {e}")
        return []

def get_monster_data(monster_index: str) -> Optional[Dict]:
    """Fetch a specific monster's raw data dict from the D&D API.

    Returns the API response (with a computed 'full_image_url') or None on error.
    Separated from get_monster_details so callers that want to cache or persist
    the raw data (e.g. the all-pairs finder) can do so without building a Monster.
    """
    try:
        response = requests.get(f"{BASE_URL}/monsters/{monster_index}")
        response.raise_for_status()
        monster_data = response.json()

        # Add full image URL if image exists
        if "image" in monster_data and monster_data["image"]:
            monster_data["full_image_url"] = f"{IMAGE_BASE_URL}{monster_data['image']}"
        else:
            monster_data["full_image_url"] = None

        return monster_data
    except Exception as e:
        print(f"Error fetching monster details for {monster_index}: {e}")
        return None


def get_monster_details(monster_index: str) -> Optional[Monster]:
    """Fetch detailed information about a specific monster.
    Returns a Monster object or None if error.
    """
    monster_data = get_monster_data(monster_index)
    if not monster_data:
        return None
    try:
        return Monster(monster_data)
    except ValueError as e:
        print(f"Error parsing monster details for {monster_index}: {e}")
        return None

