"""
All-pairs "fun matchup" finder.

Scans every pair of monsters, classifies each with the fun/boring rule, and
writes the fun matchups to fun_pairs.csv. See APPROACH.md for the reasoning.

It reuses the existing engine end to end — simulate_battle (via battle_odds) for
the fights, and BattleOdds.is_fun for the verdict. The only new logic here is the
orchestration that makes a full run feasible:

  1. Cache monster data on disk so the API is hit ~N times, not ~N^2.
  2. Scope to monsters that can actually attack.
  3. Pre-filter obvious mismatches with a cheap closed-form estimate, so we only
     simulate plausibly-competitive pairs.

Run it:  python find_fun_pairs.py
"""

import csv
import hashlib
import itertools
import json
import math
import os
from typing import List, Optional

from battle import battle_odds, parse_damage_dice, MONTE_CARLO_RUNS
from dnd_api import get_monsters, get_monster_data
from models.monster import Monster

CACHE_PATH = "monster_cache.json"      # raw API data, so re-runs need no network
OUTPUT_PATH = "fun_pairs.csv"
SIMS_PER_PAIR = MONTE_CARLO_RUNS       # reuse the engine's default batch size

# Pre-filter: skip a pair only if one side is predicted to kill the other this
# many times faster. Deliberately generous so genuinely close fights always make
# it through to a real simulation (we'd rather waste sims than miss a fun pair).
MAX_KILL_SPEED_RATIO = 2.5


# --- Cheap closed-form pre-filter -------------------------------------------

def mean_damage(damage_dice: str) -> float:
    """Average value of a dice expression like '2d6+3' (0 if unparseable)."""
    parsed = parse_damage_dice(damage_dice)
    if parsed is None:
        return 0.0
    num_dice, sides, modifier = parsed
    return num_dice * (sides + 1) / 2 + modifier


def hit_probability(to_hit: int, target_ac: int) -> float:
    """Chance a d20 + to_hit lands vs target_ac (nat 20 hits, nat 1 misses)."""
    needed = target_ac - to_hit
    winning_faces = sum(
        1 for face in range(2, 21) if face == 20 or face >= needed
    )
    return winning_faces / 20


def rounds_to_defeat(attacker: Monster, defender: Monster) -> float:
    """Rough number of rounds for attacker to drop defender (inf if it can't)."""
    attack = attacker.attack
    if attack is None:
        return math.inf
    damage_per_round = hit_probability(attack.to_hit, defender.ac) * mean_damage(attack.damage_dice)
    if damage_per_round <= 0:
        return math.inf
    return defender.hp / damage_per_round


def is_obvious_mismatch(m1: Monster, m2: Monster,
                        max_ratio: float = MAX_KILL_SPEED_RATIO) -> bool:
    """True if the pair is clearly lopsided enough to skip without simulating."""
    r1 = rounds_to_defeat(m1, m2)  # how fast m1 finishes m2
    r2 = rounds_to_defeat(m2, m1)  # how fast m2 finishes m1

    # If either side can't deal damage at all, it's never a contest.
    if math.isinf(r1) or math.isinf(r2):
        return True

    faster, slower = sorted((r1, r2))
    return (slower / faster) > max_ratio


# --- The finder --------------------------------------------------------------

def _pair_seed(m1: Monster, m2: Monster) -> int:
    """A stable, reproducible seed for a pair (independent of run order)."""
    key = "|".join(sorted((m1.index, m2.index)))
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2 ** 32)


def find_fun_pairs(monsters: List[Monster], sims: int = SIMS_PER_PAIR) -> List[dict]:
    """Return the fun matchups among all pairs of `monsters`.

    Reuses battle_odds (the simulator) and BattleOdds.is_fun (the classifier).
    Each result row carries both monsters and each side's win percentage.
    """
    fun_rows = []
    for m1, m2 in itertools.combinations(monsters, 2):
        if is_obvious_mismatch(m1, m2):
            continue

        odds = battle_odds(m1, m2, runs=sims, seed=_pair_seed(m1, m2))
        if not odds.is_fun:
            continue

        fun_rows.append({
            "monster_1": m1.name,
            "monster_2": m2.name,
            "win_pct_1": round(odds.percent1, 1),
            "win_pct_2": round(odds.percent2, 1),
            "underdog_pct": round(min(odds.percent1, odds.percent2), 1),
        })

    # Closest-to-even first — the most fun matchups lead.
    fun_rows.sort(key=lambda r: r["underdog_pct"], reverse=True)
    return fun_rows


# --- Data loading (cached) ---------------------------------------------------

def load_monsters(limit: Optional[int] = None,
                  cache_path: str = CACHE_PATH) -> List[Monster]:
    """Load attack-capable monsters, using an on-disk cache of raw API data.

    The cache means the API is hit once per monster (the first run only); every
    later run is instant and offline.
    """
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            raw_by_index = json.load(f)
    else:
        raw_by_index = {}
        listing = get_monsters()
        print(f"Fetching {len(listing)} monsters from the API (one-time)...")
        for entry in listing:
            data = get_monster_data(entry["index"])
            if data:
                raw_by_index[entry["index"]] = data
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(raw_by_index, f)
        print(f"Cached {len(raw_by_index)} monsters to {cache_path}")

    monsters = []
    for data in raw_by_index.values():
        try:
            monster = Monster(data)
        except ValueError:
            continue  # skip monsters with incomplete stats
        if monster.attack is not None:  # scope: must be able to fight
            monsters.append(monster)

    if limit is not None:
        monsters = monsters[:limit]
    return monsters


def write_csv(rows: List[dict], path: str = OUTPUT_PATH) -> None:
    """Write the fun matchups to a CSV at `path`."""
    fieldnames = ["monster_1", "monster_2", "win_pct_1", "win_pct_2", "underdog_pct"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    monsters = load_monsters()
    total_pairs = len(monsters) * (len(monsters) - 1) // 2
    print(f"{len(monsters)} attack-capable monsters -> {total_pairs} pairs to scan")

    fun_rows = find_fun_pairs(monsters)
    write_csv(fun_rows)
    print(f"Found {len(fun_rows)} fun matchups -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
