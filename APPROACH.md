# Approach: Finding Every Fun Matchup Across the Full Monster Set

**Status:** Plan for review (no code yet). Alex reviews before we build.

## Goal

Right now we classify one matchup at a time on the battle screen. Haruki wants
the whole picture: scan the entire monster set, find **every fun matchup** (both
sides clear the 20% win-chance bar we agreed on), and surface them ranked, with
the foregone conclusions demoted rather than hidden.

This document is about the hard part — doing that at scale without it taking
forever — and what the run produces.

## The scale (measured, not guessed)

Numbers below are measured on the current machine against the live D&D API and
our existing engine:

| Quantity | Value |
|---|---|
| Monsters in the set (`N`) | **334** |
| Unordered pairs (`N·(N-1)/2`) | **55,611** |
| Simulated battles at 1,000 sims/pair | **~55.6 million** |
| Time for one matchup (1,000 sims) | **~26 ms** |
| Time to fetch one monster's details (network) | **~0.9 s** |

### Why the naive version is too slow

A naive "loop over every pair, fetch both monsters, run 1,000 sims" has **two**
cost centers, and one of them is catastrophic:

1. **Network (the real killer).** Fetching each monster's details inside the
   pair loop means `55,611 pairs × 2 fetches × 0.9 s ≈ 100,000 s ≈ 28 hours` —
   almost all of it re-downloading the same 334 monsters tens of thousands of
   times.
2. **Compute.** Even if every fetch were free, `55.6M` simulated battles is
   `~24 minutes` single-threaded. Feasible, but not something you want to re-run
   casually, and it grows quadratically if the set grows.

So the naive run is dominated by redundant network I/O, with a compute floor of
~24 min underneath it. Both need to come down.

## How we make it feasible

The levers below stack. Roughly in order of impact:

### 1. Cache the monster data (kills the 28-hour problem)
There are only **334** distinct monsters, not 111,222. Fetch each one's details
**once** (~5 minutes total), store them on disk (a single JSON file), and load
from that cache for every pair. Network cost goes from ~28 hours to a one-time
~5 minutes — and zero on subsequent runs. This alone moves us from "impossible"
to "compute-bound."

### 2. Scope the set (shrinks N, and pairs shrink quadratically)
- **Drop monsters that can't fight.** Any monster whose `attack` is `None`
  (Multiattack-only / save-only creatures) can never deal damage and is never
  part of a fun matchup. Removing them trims `N` and, because pairs grow with
  `N²`, the savings are amplified.
- **Optional committee scoping.** If Haruki only cares about a curated band
  (e.g. a Challenge-Rating range, or a hand-picked roster), restricting `N`
  is the cheapest possible win. Worth confirming the intended set with him.

### 3. Pre-filter obvious mismatches before simulating (skip the stomps cheaply)
Most of the 55,611 pairs are blowouts we can reject **without** simulating, using
the stats we already parse (HP, AC, and the attack's to-hit + damage). A cheap
closed-form estimate — expected damage per round vs. HP, i.e. how many rounds
each side needs to kill the other — predicts lopsidedness in microseconds. If
that estimate says one side is wildly faster, the pair is boring; skip it. We
only spend simulations on pairs the heuristic flags as **plausibly competitive**.
The heuristic must be conservative (only skip clear mismatches) so we never
discard a genuinely fun fight; borderline pairs always fall through to real sims.

### 4. Adaptive simulation counts (don't spend 1,000 sims on a 95/5)
The fun/boring call is a single threshold at **20%**. How many sims a pair needs
depends only on how close it is to that line:
- Run a **small first batch** (e.g. 100–200 sims).
- If the result is comfortably far from 20% (deep stomp or clearly even), we're
  already confident — **stop early**.
- Only pairs whose estimate lands **near 20%** escalate to the full 1,000+ sims
  (or more) to classify them confidently.

Since most surviving pairs are not near the boundary, average sims/pair drops far
below 1,000.

### 5. Parallelize (pairs are embarrassingly parallel)
Each pair is independent, so fan the work out across CPU cores with
multiprocessing. On a typical machine this cuts wall-clock by roughly the core
count (e.g. ~8×). Combined with the filtering above, the realistic target is a
few minutes for a full run.

### 6. Reuse the engine as-is
This is an **orchestration layer on top of** `battle_odds` / `simulate_battle` —
no changes to the combat rules. The new module loads the cache, filters, runs
adaptive parallel sims, classifies with the existing `is_fun` logic, ranks, and
writes the output.

## Correctness notes (matters more at scale)

- **First-mover bias.** `simulate_battle` lets monster1 attack first, a real
  edge. One bad classification is invisible on one screen but systematic across
  55k pairs. Mitigation: simulate each pair in **both orderings** (swap who goes
  first) and combine, or alternate initiative inside the sim.
- **Noise at the boundary.** Simulated percentages wobble ±1–2% near 20%. The
  adaptive escalation (lever 4) directly addresses this — pairs on the bubble get
  more sims until the estimate is confidently on one side of the line. We can
  also record an explicit "on the bubble" band (e.g. 18–22%) for review.
- **Reproducibility.** Seed each pair deterministically (e.g. from the two
  monster indices) so a full run is repeatable and re-runs of a single pair match
  the batch — same guarantee we already rely on in `battle_odds`.

## What the run produces

A **persisted, ranked results file** (e.g. `featured_matchups.json`) so the
expensive batch runs offline and the UI just reads it (instant load):

- One entry per evaluated pair: the two monsters, each side's win %, the
  fun/boring verdict, and a **competitiveness score** (closeness to 50/50, e.g.
  the underdog's win chance).
- **Sorted** with the closest-to-even fights first — the fun ones lead.
- Boring pairs are kept in the file but flagged and sorted to the bottom
  (demoted, not deleted — per Haruki's "don't hide them").
- Metadata: monster-set size, sims budget, threshold used, timestamp — so a
  result is self-describing and we know what produced it.

This file becomes the data source for a future "featured matchups" view.

## Rough budget after optimization

| Stage | Naive | After plan |
|---|---|---|
| Network | ~28 h (refetch per pair) | ~5 min once, cached thereafter |
| Simulation | ~24 min (all pairs × 1,000) | a few minutes (filtered + adaptive + parallel) |
| Re-run cost | full every time | instant (read cached JSON) |

## Open questions for Alex / Haruki

1. **Scope of the set** — full 334, attack-capable only, or a curated/CR-bounded
   roster for the committee?
2. **Both-orderings** — accept the cost of simulating each pair twice to remove
   first-mover bias, or alternate initiative inside a single run?
3. **Output home** — is a cached JSON file the right contract for the UI, and
   where should it live / how often is it regenerated?
4. **Pre-filter aggressiveness** — how conservative should the skip heuristic be?
   (Trade-off: more skipping = faster, but risk of missing a borderline-fun pair.)
