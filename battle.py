"""
Single-battle simulator.

`simulate_battle(monster1, monster2, seed=None)` plays out one fight between two
monsters using their stats (HP, AC, and their parsed attack) and returns the
winning Monster.

Design of the fight:
  - The two monsters alternate attacks, monster1 first.
  - An attack rolls a d20 + the attacker's to-hit bonus against the defender's
    AC. A natural 20 always hits, a natural 1 always misses; otherwise it hits
    if the total meets or beats the AC.
  - A hit rolls the attack's damage dice (e.g. "1d6+2") and subtracts it from a
    LOCAL copy of the defender's HP. First to 0 HP loses.

Two guarantees the rest of the pipeline relies on:
  - Reproducible: all randomness comes from `random.Random(seed)`, so the same
    seed always replays the same fight.
  - Always terminates: rounds are capped (a monster with no usable attack deals
    no damage, which would otherwise loop forever). If the cap is reached, the
    winner is decided deterministically from the monsters' stats.

Stateless: it never mutates the Monster objects (HP is tracked in locals), so
the same monsters can be reused across thousands of fights.
"""

import random
import re
from dataclasses import dataclass
from typing import Optional

from models.monster import Monster

# Hard cap on rounds so a fight always ends, even when neither monster can deal
# damage. Generous enough that a normal fight is decided long before this.
MAX_ROUNDS = 1000

# Default number of fights to simulate when estimating win percentages. Large
# enough that the percentages are stable rather than noisy from a few rolls.
MONTE_CARLO_RUNS = 1000

# A matchup is "fun" only if BOTH monsters clear this win percentage — i.e. the
# underdog has at least a one-in-five shot (the line agreed with Haruki). Below
# it, the favourite wins more than four times out of five and the outcome isn't
# really in doubt, so the matchup is "boring".
FUN_WIN_THRESHOLD = 20.0

# Matches dice expressions like "2d6", "1d6+2", "3d8-1" (optional signed flat bonus).
_DICE_RE = re.compile(r"^\s*(\d+)\s*d\s*(\d+)\s*([+-]\s*\d+)?\s*$", re.IGNORECASE)


def _roll_damage(damage_dice: str, rng: random.Random) -> int:
    """Parse and roll a dice expression such as '2d6+3'.

    Returns the rolled total, never below 0. An unparseable or empty expression
    rolls 0 (treated as no damage rather than an error).
    """
    match = _DICE_RE.match(damage_dice or "")
    if not match:
        return 0

    num_dice = int(match.group(1))
    sides = int(match.group(2))
    modifier = int(match.group(3).replace(" ", "")) if match.group(3) else 0

    if num_dice <= 0 or sides <= 0:
        return 0

    total = sum(rng.randint(1, sides) for _ in range(num_dice)) + modifier
    return max(0, total)


def _resolve_attack(attacker: Monster, defender: Monster, defender_hp: int,
                    rng: random.Random) -> int:
    """Resolve one attack from `attacker` against `defender`.

    Returns the defender's HP after the attack. An attacker with no usable
    attack simply deals nothing.
    """
    attack = attacker.attack
    if attack is None:
        return defender_hp

    roll = rng.randint(1, 20)
    if roll == 1:
        return defender_hp  # natural 1 always misses
    if roll == 20 or roll + attack.to_hit >= defender.ac:
        return defender_hp - _roll_damage(attack.damage_dice, rng)
    return defender_hp  # miss


def _decide_by_stats(monster1: Monster, monster2: Monster,
                     hp1: int, hp2: int) -> Monster:
    """Break a stalemate (round cap reached) deterministically.

    Prefers more remaining HP, then higher AC, then higher Strength, and finally
    monster1, so a winner is always returned.
    """
    if hp1 != hp2:
        return monster1 if hp1 > hp2 else monster2
    if monster1.ac != monster2.ac:
        return monster1 if monster1.ac > monster2.ac else monster2
    if monster1.strength != monster2.strength:
        return monster1 if monster1.strength > monster2.strength else monster2
    return monster1


def simulate_battle(monster1: Monster, monster2: Monster,
                    seed: Optional[int] = None) -> Monster:
    """Play out a single fight and return the winning monster.

    Args:
        monster1: First combatant (attacks first).
        monster2: Second combatant.
        seed: Seeds the RNG; the same seed always replays the same fight. With
            seed=None the fight is random (non-reproducible).

    Returns:
        The Monster that won. If the round cap is reached without a knockout,
        the winner is decided from the monsters' stats (see _decide_by_stats).
    """
    rng = random.Random(seed)

    # Work on local HP copies — never mutate the Monster objects.
    hp1 = monster1.hp
    hp2 = monster2.hp

    for _ in range(MAX_ROUNDS):
        hp2 = _resolve_attack(monster1, monster2, hp2, rng)
        if hp2 <= 0:
            return monster1

        hp1 = _resolve_attack(monster2, monster1, hp1, rng)
        if hp1 <= 0:
            return monster2

    return _decide_by_stats(monster1, monster2, hp1, hp2)


@dataclass(frozen=True)
class BattleOdds:
    """The result of estimating a matchup's odds over many simulated fights.

    Carries everything the caller needs to display the odds without knowing how
    they were produced: each monster's win percentage and how many fights the
    estimate is based on.
    """

    percent1: float  # monster1's win percentage
    percent2: float  # monster2's win percentage
    runs: int        # number of fights the estimate is based on

    @property
    def is_fun(self) -> bool:
        """Whether this matchup is worth featuring (a real contest).

        Fun only if BOTH monsters clear FUN_WIN_THRESHOLD — equivalently, the
        underdog (the smaller win %) has at least a one-in-five shot. Below that
        it's a foregone conclusion ("boring").
        """
        return min(self.percent1, self.percent2) >= FUN_WIN_THRESHOLD


def battle_odds(monster1: Monster, monster2: Monster,
                runs: int = MONTE_CARLO_RUNS,
                seed: Optional[int] = None) -> BattleOdds:
    """Estimate each monster's chance of winning by simulating many fights.

    Plays `runs` independent battles, tallies the wins, and turns the tallies
    into percentages (a Monte Carlo estimate). The combat itself is NOT
    reimplemented here — every fight goes through simulate_battle.

    Args:
        monster1: First combatant.
        monster2: Second combatant.
        runs: How many fights to simulate. More runs -> more stable percentages.
        seed: Seeds the whole batch; the same seed reproduces the same
            percentages. With seed=None the batch is freshly random each time.

    Returns:
        A BattleOdds whose percent1/percent2 sum to 100.0 (both 0.0 when
        runs <= 0), and whose `runs` records how many fights were simulated.
    """
    if runs <= 0:
        return BattleOdds(percent1=0.0, percent2=0.0, runs=0)

    # Derive a distinct, deterministic seed per fight so the batch has variety
    # yet replays exactly when `seed` is given.
    seeder = random.Random(seed)
    wins1 = 0
    for _ in range(runs):
        fight_seed = seeder.randrange(2 ** 32)
        if simulate_battle(monster1, monster2, seed=fight_seed) is monster1:
            wins1 += 1

    percent1 = 100.0 * wins1 / runs
    return BattleOdds(percent1=percent1, percent2=100.0 - percent1, runs=runs)
