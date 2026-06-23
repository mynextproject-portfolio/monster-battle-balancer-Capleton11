from typing import Dict, Any


class Monster:
    """Represents a D&D monster with its raw display attributes.

    This class validates required fields during initialization so that
    invalid API data fails fast with a clear error message.
    """

    def __init__(self, data: Dict[str, Any]):
        """Initialize a Monster from API response data.

        Validates required fields immediately (fail-fast error handling).

        Args:
            data: Dictionary containing monster data from the API

        Raises:
            ValueError: If required fields are missing or invalid
        """
        self._data = data

        # Basic attributes (with defaults)
        self.index = data.get("index", "")
        self.name = data.get("name", "Unknown")
        self.image_url = data.get("full_image_url")

        # Validate and extract required fields (fail fast)
        self._validate_and_extract_required_fields()

    def _validate_and_extract_required_fields(self) -> None:
        """Validate and extract required fields from API data.

        Raises:
            ValueError: If any required field is missing or invalid
        """
        # Hit points (required)
        if "hit_points" not in self._data:
            raise ValueError(f"Monster '{self.name}' missing required 'hit_points' data")
        self._hp = self._data["hit_points"]

        # Armor class (required)
        armor_class = self._data.get("armor_class", [])
        if not armor_class or len(armor_class) == 0:
            raise ValueError(f"Monster '{self.name}' missing required 'armor_class' data")
        ac_value = armor_class[0].get("value")
        if ac_value is None:
            raise ValueError(f"Monster '{self.name}' has invalid 'armor_class' structure")
        self._ac = ac_value

        # Strength (required)
        if "strength" not in self._data:
            raise ValueError(f"Monster '{self.name}' missing required 'strength' data")
        self._strength = self._data["strength"]

    # Properties - lightweight accessors returning the validated values

    @property
    def hp(self) -> int:
        """Return the monster's hit points."""
        return self._hp

    @property
    def ac(self) -> int:
        """Return the monster's armor class (Defense)."""
        return self._ac

    @property
    def strength(self) -> int:
        """Return the monster's Strength score."""
        return self._strength

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"Monster(name='{self.name}', hp={self.hp}, ac={self.ac})"
