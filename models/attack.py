from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Attack:
    """A single to-hit attack parsed from a monster's API actions.

    This represents the kind of action a creature rolls *to hit* with: it has
    an attack bonus (to-hit) and rolls damage dice. It deliberately does NOT
    represent:

      - grouping actions like "Multiattack" (no attack_bonus), or
      - save-based abilities like a dragon's "Fire Breath" (uses a saving
        throw / DC instead of an attack roll, so it has no attack_bonus).

    Build one with `Attack.from_actions(...)`, which filters the messy API
    `actions` list down to a real attack.
    """

    name: str
    to_hit: int                        # attack bonus, e.g. +17 -> 17
    damage_dice: str                   # dice expression, e.g. "1d6+2"
    damage_type: Optional[str] = None  # e.g. "Slashing" (display/sim convenience)

    @classmethod
    def from_action(cls, action: Dict[str, Any]) -> Optional["Attack"]:
        """Build an Attack from a single API action.

        Returns None when the action is not a usable to-hit attack — i.e. it
        has no `attack_bonus` (Multiattack, save-based abilities) or carries no
        rollable damage dice.
        """
        attack_bonus = action.get("attack_bonus")
        if attack_bonus is None:
            # Multiattack, Frightful Presence, Fire Breath, etc.
            return None

        # `damage` is a list; an attack can deal more than one damage type
        # (e.g. a dragon's Bite is piercing + fire). We take the first entry
        # that actually carries a dice expression as the attack's damage.
        damage_entries: List[Dict[str, Any]] = action.get("damage") or []
        primary = next((d for d in damage_entries if d.get("damage_dice")), None)
        if primary is None:
            # An attack roll with no rollable damage isn't usable for a fight.
            return None

        damage_type = (primary.get("damage_type") or {}).get("name")
        return cls(
            name=action.get("name", "Attack"),
            to_hit=attack_bonus,
            damage_dice=primary["damage_dice"],
            damage_type=damage_type,
        )

    @classmethod
    def from_actions(cls, actions: Optional[List[Dict[str, Any]]]) -> Optional["Attack"]:
        """Pick a monster's primary attack from its full `actions` list.

        Returns the first action that is a real to-hit attack, skipping
        non-attacks (Multiattack, save-based abilities). Returns None if the
        monster has no usable attack at all.
        """
        for action in actions or []:
            attack = cls.from_action(action)
            if attack is not None:
                return attack
        return None
