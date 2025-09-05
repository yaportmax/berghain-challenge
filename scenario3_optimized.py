#!/usr/bin/env python3
"""Run scenario 3 with a strategy tuned to minimise rejections.

The default `bouncer.py` implementation uses a generic heuristic for
scenarios 1 and 3.  This script focuses solely on scenario 3 and applies
custom logic that aggressively fills required attribute quotas while
keeping the number of rejected entrants as low as possible.  Game creation
is rate‑limited, so the script stores the ID of a newly created game and
reuses it on subsequent runs.  Once a game is started the `decide-and-next`
endpoint may be called freely until the scenario completes.
"""

from typing import Dict
import argparse
import random
from pathlib import Path

from bouncer import BerghainBouncer


GAME_ID_FILE = Path("scenario3_game_id.txt")


class Scenario3Bouncer(BerghainBouncer):
    """Specialised bouncer with acceptance rules for scenario 3.

    Supports multiple strategies to experiment with different trade-offs
    between filling quotas early and keeping rejections low.  The class can
    also run an offline Monte-Carlo simulation so optimisation can continue
    without repeatedly calling the remote API.
    """

    needed = {
        "underground_veteran": 500,
        "international": 650,
        "fashion_forward": 550,
        "queer_friendly": 250,
        "vinyl_collector": 200,
        "german_speaker": 800,
    }
    capacity = 1000

    # Approximate attribute frequencies used for simulation mode
    attribute_freq = {
        "underground_veteran": 0.501,
        "international": 0.651,
        "fashion_forward": 0.551,
        "queer_friendly": 0.251,
        "vinyl_collector": 0.201,
        "german_speaker": 0.4565,
    }

    def __init__(self, strategy: str = "balanced") -> None:
        super().__init__()
        self.strategy = strategy

    def _calc_deficits(self, counts: Dict[str, int]) -> Dict[str, int]:
        return {
            attr: max(0, self.needed[attr] - counts.get(attr, 0)) for attr in self.needed
        }

    def _should_accept(
        self, attrs: Dict[str, bool], current: Dict[str, int], admitted: int
    ) -> bool:
        """Return ``True`` if admitting this person keeps all constraints feasible."""

        remaining = self.capacity - admitted
        if remaining <= 0:
            return False

        deficits = self._calc_deficits(current)
        total_deficit = sum(deficits.values())
        helpful_attrs = [a for a, d in deficits.items() if d > 0 and attrs.get(a)]

        # If any attribute would become impossible to satisfy after rejection,
        # force acceptance when the person has that critical attribute.
        for attr, deficit in deficits.items():
            if deficit > remaining - 1 and attrs.get(attr):
                return True
            if deficit > remaining - 1 and not attrs.get(attr):
                return False

        if total_deficit == 0:
            return True

        slack = remaining - total_deficit
        if self.strategy == "deficit_first" and total_deficit >= remaining:
            return bool(helpful_attrs)

        if self.strategy == "quota_first" and helpful_attrs:
            # Prioritise the attribute with the largest remaining deficit
            priority_attr = max(deficits, key=lambda a: deficits[a])
            if deficits[priority_attr] > 0:
                if attrs.get(priority_attr):
                    return True
                return slack > 0 and len(helpful_attrs) == 0

        if helpful_attrs:
            return True

        return slack > 0

    def run(
        self,
        existing_game_id: str | None = None,
        limit: int | None = None,
    ) -> Dict:
        """Play through scenario 3 and return final statistics.

        If ``existing_game_id`` is provided, a new game is not created and the
        provided ID is used instead.  ``limit`` can be supplied for debugging to
        stop after processing a fixed number of entrants, which helps avoid
        spending thousands of API calls when iterating.
        """

        if existing_game_id is None:
            game = self.create_game(3)
            game_id = game["gameId"]
            constraints = game["constraints"]
            result = self.make_decision(game_id, 0)
        else:
            game_id = existing_game_id
            result = self.make_decision(game_id, 0)
            constraints = result.get("constraints")
            if constraints is None:
                constraints = [
                    {"attribute": "underground_veteran", "minCount": 500},
                    {"attribute": "international", "minCount": 650},
                    {"attribute": "fashion_forward", "minCount": 550},
                    {"attribute": "queer_friendly", "minCount": 250},
                    {"attribute": "vinyl_collector", "minCount": 200},
                    {"attribute": "german_speaker", "minCount": 800},
                ]

        counts = {c["attribute"]: 0 for c in constraints}
        admitted = 0
        rejected = 0

        processed = 0
        while result.get("status") == "running":
            person = result["nextPerson"]
            attrs = person["attributes"]
            index = person["personIndex"]

            accept = self._should_accept(attrs, counts, admitted)

            if accept:
                admitted += 1
                for attr, has in attrs.items():
                    if has and attr in counts:
                        counts[attr] += 1
            else:
                rejected += 1

            result = self.make_decision(game_id, index, accept)
            processed += 1

            if processed % 500 == 0:
                print(
                    f"Processed {processed} entrants - admitted {admitted}, rejected {rejected}",
                    flush=True,
                )

            if limit and processed >= limit:
                break

        return {
            "game_id": game_id,
            "status": result.get("status", "unknown"),
            "rejected_count": result.get("rejectedCount", rejected),
            "admitted_count": admitted,
            "final_counts": counts,
        }

    def simulate(self, entrants: int, seed: int | None = None) -> Dict:
        """Run an offline Monte-Carlo simulation for the bouncer logic."""

        rng = random.Random(seed)
        counts = {attr: 0 for attr in self.needed}
        admitted = 0
        rejected = 0

        for _ in range(entrants):
            attrs = {
                attr: rng.random() < freq for attr, freq in self.attribute_freq.items()
            }
            if self._should_accept(attrs, counts, admitted):
                if admitted < self.capacity:
                    admitted += 1
                    for attr, has in attrs.items():
                        if has:
                            counts[attr] += 1
                else:
                    rejected += 1
            else:
                rejected += 1

        return {
            "status": "simulated",
            "rejected_count": rejected,
            "admitted_count": admitted,
            "final_counts": counts,
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--strategy",
        choices=["balanced", "deficit_first", "quota_first"],
        default="balanced",
        help="admission strategy to use",
    )
    parser.add_argument(
        "--game-id",
        help="explicit game ID to resume (overrides stored ID)",
    )
    parser.add_argument(
        "--new-game",
        action="store_true",
        help="start a fresh game even if a stored ID exists",
    )
    parser.add_argument(
        "--simulate",
        type=int,
        help="run an offline simulation with the given number of entrants",
    )
    parser.add_argument("--seed", type=int, help="random seed for simulation")
    parser.add_argument(
        "--limit",
        type=int,
        help="process only this many entrants when playing the real game",
    )
    args = parser.parse_args()

    bouncer = Scenario3Bouncer(strategy=args.strategy)
    if args.simulate:
        outcome = bouncer.simulate(args.simulate, seed=args.seed)
    else:
        game_id = args.game_id
        if game_id is None and not args.new_game and GAME_ID_FILE.exists():
            game_id = GAME_ID_FILE.read_text().strip() or None
        outcome = bouncer.run(existing_game_id=game_id, limit=args.limit)
        GAME_ID_FILE.write_text(outcome["game_id"])
    print(
        f"Scenario 3 finished with status {outcome['status']}\n"
        f"Admitted: {outcome['admitted_count']}  "
        f"Rejected: {outcome['rejected_count']}\n"
        f"Final counts: {outcome['final_counts']}"
    )


if __name__ == "__main__":
    main()
