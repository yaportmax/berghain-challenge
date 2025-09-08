#!/usr/bin/env python3
"""
Final winning strategy for scenario 3 that ensures all constraints are met.

Strategy:
1. Priority traits: queer_friendly, vinyl_collector, german_speaker (3 rarest)
2. Accept people with priority traits OR anyone who helps with severely unmet constraints
3. Use dynamic thresholds based on remaining capacity to ensure scenario completion
4. Prioritize winning over minimizing rejections
"""

import json
import time
from typing import Dict, List, Set
from bouncer import BerghainBouncer


class FinalWinningScenario3(BerghainBouncer):
    """Final winning optimizer that ensures all constraints are met."""
    
    def __init__(self):
        super().__init__()
        self.constraints = {
            "vinyl_collector": 200,
            "queer_friendly": 250,
            "german_speaker": 800,
            "underground_veteran": 500,
            "fashion_dressed": 550,
            "international": 650
        }
        
        self.priority_traits = {"queer_friendly", "vinyl_collector", "german_speaker"}
        
    def _should_accept_final_strategy(
        self, 
        attrs: Dict[str, bool], 
        current: Dict[str, int], 
        admitted: int
    ) -> bool:
        """
        Final strategy that ensures scenario completion:
        1. Always accept people with priority traits (if not capped)
        2. Accept people who help with any unmet constraint
        3. Use urgency thresholds based on remaining capacity
        """
        remaining_capacity = 1000 - admitted
        if remaining_capacity <= 0:
            return False
            
        for trait in self.priority_traits:
            if attrs.get(trait, False) and current.get(trait, 0) < self.constraints[trait]:
                return True
        
        for trait, target in self.constraints.items():
            current_count = current.get(trait, 0)
            deficit = target - current_count
            
            if deficit > 0 and attrs.get(trait, False):
                urgency_threshold = deficit / remaining_capacity if remaining_capacity > 0 else 1.0
                
                if deficit >= 100:  # Large deficit
                    return True
                elif deficit >= 50 and urgency_threshold > 0.1:  # Medium deficit with urgency
                    return True
                elif deficit >= 20 and urgency_threshold > 0.2:  # Small deficit with high urgency
                    return True
                elif remaining_capacity <= 200:  # Late game - accept any help
                    return True
                    
        all_constraints_met = all(
            current.get(trait, 0) >= target 
            for trait, target in self.constraints.items()
        )
        
        return all_constraints_met
        
    def run_final_strategy(self) -> Dict:
        """Run scenario 3 with final winning strategy."""
        print("=== Final Winning Scenario 3 Strategy ===")
        print("Priority traits: queer_friendly, vinyl_collector, german_speaker")
        print("Strategy: Aggressive constraint completion with urgency thresholds")
        print()
        
        game = self.create_game(3)
        game_id = game["gameId"]
        result = self.make_decision(game_id, 0)
            
        counts = {attr: 0 for attr in self.constraints}
        admitted = 0
        rejected = 0
        
        while result.get("status") == "running":
            person = result["nextPerson"]
            attrs = person["attributes"]
            index = person["personIndex"]
            
            accept = self._should_accept_final_strategy(attrs, counts, admitted)
            
            if accept:
                admitted += 1
                for attr, has in attrs.items():
                    if has and attr in counts:
                        counts[attr] += 1
            else:
                rejected += 1
                
            result = self.make_decision(game_id, index, accept)
            
            if index % 200 == 0:
                remaining = 1000 - admitted
                print(f"Person {index}: Remaining capacity: {remaining}")
                print(f"  Priority counts: queer_friendly={counts.get('queer_friendly', 0)}/250, "
                      f"vinyl_collector={counts.get('vinyl_collector', 0)}/200, "
                      f"german_speaker={counts.get('german_speaker', 0)}/800")
                
                deficits = {}
                for trait, target in self.constraints.items():
                    deficit = max(0, target - counts.get(trait, 0))
                    deficits[trait] = deficit
                print(f"  Deficits: {deficits}")
                print(f"  Admitted: {admitted}, Rejected: {rejected}")
                
        final_status = result.get("status", "unknown")
        if final_status == "running":
            final_status = "completed"
            
        constraints_met = all(
            counts.get(trait, 0) >= target 
            for trait, target in self.constraints.items()
        )
        
        return {
            "strategy": "final_winning_aggressive",
            "status": final_status,
            "scenario_won": constraints_met,
            "rejected_count": result.get("rejectedCount", rejected),
            "admitted_count": admitted,
            "final_counts": counts,
            "constraints_met": {
                trait: counts.get(trait, 0) >= target
                for trait, target in self.constraints.items()
            },
            "game_id": game_id
        }


def main():
    optimizer = FinalWinningScenario3()
    result = optimizer.run_final_strategy()
    
    print("\n=== FINAL WINNING STRATEGY RESULTS ===")
    print(f"Scenario won: {result['scenario_won']}")
    print(f"Status: {result['status']}")
    print(f"Rejections: {result['rejected_count']}")
    print(f"Admitted: {result['admitted_count']}")
    print()
    
    print("Constraint achievement:")
    for trait, target in optimizer.constraints.items():
        count = result['final_counts'].get(trait, 0)
        met = result['constraints_met'][trait]
        percentage = (count / target) * 100
        status = "✅" if met else "❌"
        print(f"  {status} {trait}: {count}/{target} ({percentage:.1f}%)")
        
    if result['scenario_won']:
        print("\n🎉 SCENARIO 3 WON! All constraints met within 1000 people.")
    else:
        print("\n❌ Scenario not won. Some constraints not met.")


if __name__ == "__main__":
    main()
