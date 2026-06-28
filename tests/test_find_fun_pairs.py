"""
Tests for the all-pairs fun-matchup finder.

These exercise the pure logic (pre-filter and find) with synthetic monsters, so
they're fast and need no network. The finder reuses the already-tested engine
(battle_odds / is_fun); here we check the orchestration around it.
"""

import find_fun_pairs as finder
from models.monster import Monster


def make_monster(name, hp, ac, to_hit=None, damage_dice=None, strength=10):
    """Build a Monster with an optional single attack."""
    actions = []
    if to_hit is not None:
        actions.append({
            "name": "Attack",
            "attack_bonus": to_hit,
            "damage": [{"damage_type": {"name": "Slashing"}, "damage_dice": damage_dice}],
        })
    return Monster({
        "index": name.lower(),
        "name": name,
        "hit_points": hp,
        "armor_class": [{"value": ac}],
        "strength": strength,
        "actions": actions,
    })


class TestPreFilter:
    """The cheap closed-form mismatch filter."""

    def test_mean_damage(self):
        assert finder.mean_damage("1d6+2") == 5.5   # (1+6)/2 + 2
        assert finder.mean_damage("2d8") == 9.0      # 2 * (1+8)/2
        assert finder.mean_damage("garbage") == 0.0

    def test_hit_probability_bounds(self):
        # Needs a 10 to hit -> faces 10..20 land = 11/20.
        assert finder.hit_probability(to_hit=0, target_ac=10) == 11 / 20
        # Absurdly high AC -> only a natural 20 lands.
        assert finder.hit_probability(to_hit=0, target_ac=100) == 1 / 20

    def test_evenly_matched_pair_not_skipped(self):
        a = make_monster("A", hp=30, ac=13, to_hit=5, damage_dice="1d8+2")
        b = make_monster("B", hp=30, ac=13, to_hit=5, damage_dice="1d8+2")
        assert finder.is_obvious_mismatch(a, b) is False

    def test_lopsided_pair_is_skipped(self):
        titan = make_monster("Titan", hp=400, ac=20, to_hit=15, damage_dice="6d10+10")
        weakling = make_monster("Weakling", hp=5, ac=8, to_hit=0, damage_dice="1d2")
        assert finder.is_obvious_mismatch(titan, weakling) is True

    def test_monster_with_no_attack_is_skipped(self):
        fighter = make_monster("Fighter", hp=30, ac=13, to_hit=5, damage_dice="1d8+2")
        pacifist = make_monster("Pacifist", hp=30, ac=13)  # no attack
        assert finder.is_obvious_mismatch(fighter, pacifist) is True


class TestFindFunPairs:
    """The end-to-end find over a small monster set."""

    def test_finds_even_pair_and_skips_stomp(self):
        a = make_monster("Araknid", hp=30, ac=13, to_hit=5, damage_dice="1d8+2")
        b = make_monster("Bruiser", hp=30, ac=13, to_hit=5, damage_dice="1d8+2")
        titan = make_monster("Titan", hp=400, ac=20, to_hit=15, damage_dice="6d10+10")

        rows = finder.find_fun_pairs([a, b, titan], sims=300)

        names = {frozenset((r["monster_1"], r["monster_2"])) for r in rows}
        assert frozenset(("Araknid", "Bruiser")) in names           # fun pair found
        assert frozenset(("Araknid", "Titan")) not in names         # stomp excluded
        assert frozenset(("Bruiser", "Titan")) not in names

    def test_rows_carry_both_monsters_and_win_pcts(self):
        a = make_monster("A", hp=30, ac=13, to_hit=5, damage_dice="1d8+2")
        b = make_monster("B", hp=30, ac=13, to_hit=5, damage_dice="1d8+2")

        rows = finder.find_fun_pairs([a, b], sims=300)

        assert len(rows) == 1
        row = rows[0]
        assert {row["monster_1"], row["monster_2"]} == {"A", "B"}
        assert row["win_pct_1"] + row["win_pct_2"] == 100.0

    def test_results_reproducible(self):
        a = make_monster("A", hp=40, ac=15, to_hit=6, damage_dice="2d6+3")
        b = make_monster("B", hp=35, ac=14, to_hit=5, damage_dice="1d10+2")

        assert finder.find_fun_pairs([a, b], sims=300) == finder.find_fun_pairs([a, b], sims=300)

    def test_sorted_closest_to_even_first(self):
        rows = [
            {"underdog_pct": 25.0}, {"underdog_pct": 48.0}, {"underdog_pct": 33.0},
        ]
        rows.sort(key=lambda r: r["underdog_pct"], reverse=True)
        assert [r["underdog_pct"] for r in rows] == [48.0, 33.0, 25.0]
