#!/usr/bin/env python3
"""Run scenario 3 with a strategy tuned to minimise rejections.

The default `bouncer.py` implementation uses a generic heuristic for
scenarios 1 and 3.  This script focuses solely on scenario 3 and applies
custom logic that aggressively fills required attribute quotas while
keeping the number of rejected entrants as low as possible.  It makes a
single game request and then only the minimal `decide-and-next` calls
necessary to complete the scenario, helping avoid rate‑limit issues.
"""

from typing import Dict

from bouncer import BerghainBouncer


class Scenario3Bouncer(BerghainBouncer):
    """Specialised bouncer with acceptance rules for scenario 3."""

    def _should_accept(
        self, attrs: Dict[str, bool], current: Dict[str, int], admitted: int
    ) -> bool:
        """Return ``True`` if admitting this person keeps all constraints feasible.

        Rather than working in stages, the algorithm checks whether accepting
        the current person would still leave enough capacity to satisfy all
        outstanding attribute requirements.  If doing so would make it
        impossible to meet the remaining quotas, the person is rejected;
        otherwise they are admitted.  This accepts as many entrants as
        possible early on, minimising unnecessary rejections.
        """

        needed = {
            "underground_veteran": 500,
            "international": 650,
            "fashion_dressed": 550,
            "queer_friendly": 250,
            "vinyl_collector": 200,
            "german_speaker": 800,
        }

        capacity = 1000
        remaining_capacity = capacity - admitted
        if remaining_capacity <= 0:
            return False

        # Simulate admitting this person and see how many slots would still be
        # required to satisfy the remaining quotas.
        future_counts = current.copy()
        for attr, has in attrs.items():
            if has and attr in future_counts:
                future_counts[attr] += 1

        deficits = {
            attr: max(0, needed[attr] - future_counts[attr]) for attr in needed
        }

        # If any single attribute would require more people than we have slots
        # left after admitting this person, we must reject them.
        if any(deficit > (remaining_capacity - 1) for deficit in deficits.values()):
            return False

        return True

    def run(self, existing_game_id: str | None = None) -> Dict:
        """Play through scenario 3 and return final statistics.

        If ``existing_game_id`` is provided, a new game is not created and the
        provided ID is used instead.  This helps minimise the number of API
        calls when reusing a pre-generated blank game.
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
                    {"attribute": "fashion_dressed", "minCount": 550},
                    {"attribute": "queer_friendly", "minCount": 250},
                    {"attribute": "vinyl_collector", "minCount": 200},
                    {"attribute": "german_speaker", "minCount": 800},
                ]

        counts = {c["attribute"]: 0 for c in constraints}
        admitted = 0
        rejected = 0

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

        return {
            "status": result.get("status", "unknown"),
            "rejected_count": result.get("rejectedCount", rejected),
            "admitted_count": admitted,
            "final_counts": counts,
        }


def main() -> None:
    bouncer = Scenario3Bouncer()
    outcome = bouncer.run()
    print(
        f"Scenario 3 finished with status {outcome['status']}\n"
        f"Admitted: {outcome['admitted_count']}  "
        f"Rejected: {outcome['rejected_count']}\n"
        f"Final counts: {outcome['final_counts']}"
    )


if __name__ == "__main__":
    main()
