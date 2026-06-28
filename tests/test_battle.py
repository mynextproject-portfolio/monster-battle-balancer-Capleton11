"""
Tests for the single-battle simulator (battle.py).

These cover the contract the rest of the pipeline depends on:
  - a winner is always one of the two monsters,
  - the same seed reproduces the same outcome,
  - the fight actually uses HP / AC / attacks,
  - a fight always terminates (even with a monster that can't attack),
  - the Monster objects are never mutated.
"""

import battle
from battle import simulate_battle, battle_odds, BattleOdds
from models.monster import Monster


def make_monster(name, hp, ac, to_hit=None, damage_dice=None, strength=10):
    """Build a Monster with an optional single attack.

    Pass to_hit/damage_dice to give it an attack; omit them for a monster that
    can't attack (the Multiattack / no-attack case).
    """
    actions = []
    if to_hit is not None:
        actions.append({
            "name": "Attack",
            "attack_bonus": to_hit,
            "damage": [{"damage_type": {"name": "Slashing"}, "damage_dice": damage_dice}],
        })
    return Monster({
        "name": name,
        "hit_points": hp,
        "armor_class": [{"value": ac}],
        "strength": strength,
        "actions": actions,
    })


class TestWinner:
    """A valid winner is always returned."""

    def test_returns_one_of_the_two_monsters(self):
        m1 = make_monster("A", hp=30, ac=12, to_hit=5, damage_dice="1d8+3")
        m2 = make_monster("B", hp=30, ac=12, to_hit=5, damage_dice="1d8+3")

        winner = simulate_battle(m1, m2, seed=1)

        assert winner in (m1, m2)


class TestReproducibility:
    """Same seed -> same outcome."""

    def test_same_seed_same_winner(self):
        m1 = make_monster("A", hp=25, ac=13, to_hit=4, damage_dice="1d6+2")
        m2 = make_monster("B", hp=25, ac=13, to_hit=4, damage_dice="1d6+2")

        first = simulate_battle(m1, m2, seed=42)
        second = simulate_battle(m1, m2, seed=42)

        assert first is second

    def test_same_seed_replays_across_many_seeds(self):
        m1 = make_monster("A", hp=40, ac=15, to_hit=6, damage_dice="2d6+3")
        m2 = make_monster("B", hp=35, ac=14, to_hit=5, damage_dice="1d10+2")

        for seed in range(20):
            assert simulate_battle(m1, m2, seed=seed) is simulate_battle(m1, m2, seed=seed)


class TestUsesStats:
    """The outcome reflects the monsters' stats and attacks."""

    def test_attacker_beats_monster_that_cannot_attack(self):
        attacker = make_monster("Attacker", hp=30, ac=10, to_hit=8, damage_dice="2d8+4")
        helpless = make_monster("Helpless", hp=20, ac=10)  # no attack

        # The helpless monster can never deal damage, so the attacker always wins
        # regardless of seed.
        for seed in range(25):
            assert simulate_battle(attacker, helpless, seed=seed) is attacker

    def test_overwhelmingly_stronger_monster_wins(self):
        titan = make_monster("Titan", hp=500, ac=20, to_hit=15, damage_dice="6d10+10")
        weakling = make_monster("Weakling", hp=5, ac=8, to_hit=0, damage_dice="1d2")

        for seed in range(25):
            assert simulate_battle(titan, weakling, seed=seed) is titan


class TestTermination:
    """A fight always ends."""

    def test_two_monsters_that_cannot_attack_still_terminate(self):
        # Neither can deal damage; the fight must hit the round cap and resolve
        # by stats rather than loop forever. Higher AC wins the tiebreak.
        m1 = make_monster("Tougher", hp=20, ac=18)
        m2 = make_monster("Softer", hp=20, ac=12)

        winner = simulate_battle(m1, m2, seed=0)

        assert winner is m1

    def test_attacker_that_can_never_hit_still_terminates(self):
        # to_hit so low vs AC so high that only a natural 20 lands — the fight is
        # slow but bounded and still returns a winner.
        m1 = make_monster("PoorAim", hp=10, ac=30, to_hit=-5, damage_dice="1d4")
        m2 = make_monster("PoorAim2", hp=10, ac=30, to_hit=-5, damage_dice="1d4")

        winner = simulate_battle(m1, m2, seed=3)

        assert winner in (m1, m2)


class TestStateless:
    """The Monster objects are never mutated."""

    def test_does_not_mutate_monster_hp(self):
        m1 = make_monster("A", hp=30, ac=12, to_hit=5, damage_dice="1d8+3")
        m2 = make_monster("B", hp=30, ac=12, to_hit=5, damage_dice="1d8+3")

        simulate_battle(m1, m2, seed=7)

        assert m1.hp == 30
        assert m2.hp == 30

    def test_same_objects_reusable_across_fights(self):
        m1 = make_monster("A", hp=30, ac=12, to_hit=5, damage_dice="1d8+3")
        m2 = make_monster("B", hp=30, ac=12, to_hit=5, damage_dice="1d8+3")

        # Reusing the same objects across runs gives stable, repeatable results.
        results = [simulate_battle(m1, m2, seed=9) for _ in range(5)]
        assert all(r is results[0] for r in results)


class TestDamageRoll:
    """The dice parser/roller behaves and stays in range."""

    def test_roll_in_expected_range(self):
        import random
        rng = random.Random(123)
        for _ in range(200):
            value = battle._roll_damage("2d6+3", rng)
            assert 5 <= value <= 15  # 2..12 from dice, +3

    def test_flat_and_no_modifier(self):
        import random
        rng = random.Random(1)
        assert battle._roll_damage("1d1", rng) == 1          # 1 side die -> always 1
        assert battle._roll_damage("3d1-1", rng) == 2        # 3*1 - 1

    def test_unparseable_rolls_zero(self):
        import random
        rng = random.Random(1)
        assert battle._roll_damage("", rng) == 0
        assert battle._roll_damage("not dice", rng) == 0


class TestBattleOdds:
    """Test the Monte Carlo win-percentage estimate (battle_odds)."""

    def test_percentages_sum_to_100(self):
        m1 = make_monster("A", hp=30, ac=13, to_hit=5, damage_dice="1d8+2")
        m2 = make_monster("B", hp=30, ac=13, to_hit=5, damage_dice="1d8+2")

        odds = battle_odds(m1, m2, runs=500, seed=1)

        assert isinstance(odds, BattleOdds)
        assert odds.percent1 + odds.percent2 == 100.0
        assert 0.0 <= odds.percent1 <= 100.0 and 0.0 <= odds.percent2 <= 100.0

    def test_records_number_of_runs(self):
        m1 = make_monster("A", hp=30, ac=13, to_hit=5, damage_dice="1d8+2")
        m2 = make_monster("B", hp=30, ac=13, to_hit=5, damage_dice="1d8+2")

        assert battle_odds(m1, m2, runs=500, seed=1).runs == 500

    def test_same_seed_same_odds(self):
        m1 = make_monster("A", hp=40, ac=15, to_hit=6, damage_dice="2d6+3")
        m2 = make_monster("B", hp=35, ac=14, to_hit=5, damage_dice="1d10+2")

        first = battle_odds(m1, m2, runs=300, seed=42)
        second = battle_odds(m1, m2, runs=300, seed=42)

        assert first == second

    def test_dominant_monster_wins_almost_always(self):
        titan = make_monster("Titan", hp=500, ac=20, to_hit=15, damage_dice="6d10+10")
        weakling = make_monster("Weakling", hp=5, ac=8, to_hit=0, damage_dice="1d2")

        odds = battle_odds(titan, weakling, runs=500, seed=7)

        assert odds.percent1 == 100.0
        assert odds.percent2 == 0.0

    def test_runs_many_battles_not_one(self):
        # An evenly matched pair should land somewhere in between, which only
        # happens if many distinct fights are actually run.
        m1 = make_monster("A", hp=30, ac=13, to_hit=5, damage_dice="1d8+2")
        m2 = make_monster("B", hp=30, ac=13, to_hit=5, damage_dice="1d8+2")

        odds = battle_odds(m1, m2, runs=1000, seed=3)

        assert 0.0 < odds.percent1 < 100.0

    def test_zero_runs_returns_zeros(self):
        m1 = make_monster("A", hp=30, ac=13, to_hit=5, damage_dice="1d8+2")
        m2 = make_monster("B", hp=30, ac=13, to_hit=5, damage_dice="1d8+2")

        odds = battle_odds(m1, m2, runs=0)

        assert (odds.percent1, odds.percent2, odds.runs) == (0.0, 0.0, 0)

    def test_does_not_mutate_monsters(self):
        m1 = make_monster("A", hp=30, ac=13, to_hit=5, damage_dice="1d8+2")
        m2 = make_monster("B", hp=30, ac=13, to_hit=5, damage_dice="1d8+2")

        battle_odds(m1, m2, runs=200, seed=1)

        assert m1.hp == 30 and m2.hp == 30


class TestFunVerdict:
    """Test the fun/boring classification (both sides must clear 20%)."""

    def test_even_matchup_is_fun(self):
        assert BattleOdds(percent1=60.0, percent2=40.0, runs=100).is_fun is True

    def test_lopsided_matchup_is_boring(self):
        assert BattleOdds(percent1=95.0, percent2=5.0, runs=100).is_fun is False

    def test_threshold_is_inclusive_at_20(self):
        # Underdog with exactly a one-in-five shot still counts as fun.
        assert BattleOdds(percent1=80.0, percent2=20.0, runs=100).is_fun is True

    def test_just_below_threshold_is_boring(self):
        # 81/19 — the underdog falls just short of one-in-five.
        assert BattleOdds(percent1=81.0, percent2=19.0, runs=100).is_fun is False

    def test_verdict_independent_of_side_order(self):
        # The favourite being monster1 or monster2 must not change the verdict.
        assert BattleOdds(percent1=5.0, percent2=95.0, runs=100).is_fun is False
        assert BattleOdds(percent1=45.0, percent2=55.0, runs=100).is_fun is True

    def test_dominant_matchup_from_simulation_is_boring(self):
        titan = make_monster("Titan", hp=500, ac=20, to_hit=15, damage_dice="6d10+10")
        weakling = make_monster("Weakling", hp=5, ac=8, to_hit=0, damage_dice="1d2")

        assert battle_odds(titan, weakling, runs=300, seed=7).is_fun is False
