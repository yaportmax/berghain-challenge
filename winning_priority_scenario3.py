#!/usr/bin/env python3
"""
Winning priority strategy for scenario 3 that ensures scenario completion.

Strategy:
1. Focus on queer_friendly, vinyl_collector, and german_speaker initially
2. Accept people with at least one priority trait OR anyone who helps with severely unmet constraints
3. Use early transition to constraint-filling mode to ensure scenario completion
4. Prioritize winning over strict adherence to priority-only rule
"""

import json
import time
from typing import Dict, List, Set
from bouncer import BerghainBouncer


class WinningPriorityScenario3(BerghainBouncer):
    """Winning priority optimizer that ensures scenario completion."""
    
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
        
    def _get_active_priority_traits(self, current: Dict[str, int]) -> Set[str]:
        """Get priority traits that haven't reached their cap yet."""
        active_traits = set()
        for trait in self.priority_traits:
            if current.get(trait, 0) < self.constraints[trait]:
                active_traits.add(trait)
        return active_traits
        
    def _should_accept_winning_priority(
        self, 
        attrs: Dict[str, bool], 
        current: Dict[str, int], 
        admitted: int
    ) -> bool:
        """
        Winning priority strategy that ensures scenario completion:
        1. Accept people with priority traits (if not capped)
        2. ALSO accept people who help with large constraint deficits
        3. Transition early to ensure all constraints can be met
        """
        remaining_capacity = 1000 - admitted
        if remaining_capacity <= 0:
            return False
            
        active_priority_traits = self._get_active_priority_traits(current)
        
        if active_priority_traits:
            has_active_priority_trait = any(
                attrs.get(trait, False) for trait in active_priority_traits
            )
            if has_active_priority_trait:
                return True
        
        large_deficits = []
        for trait, target in self.constraints.items():
            current_count = current.get(trait, 0)
            deficit = target - current_count
            
            if deficit > 0 and attrs.get(trait, False):
                urgency_ratio = deficit / remaining_capacity if remaining_capacity > 0 else 1.0
                
                if deficit >= 300:  # Very large deficit
                    return True
                elif deficit >= 150 and urgency_ratio > 0.2:  # Large deficit with urgency
                    return True
                elif deficit >= 50 and urgency_ratio > 0.4:  # Medium deficit with high urgency
                    return True
                elif remaining_capacity <= 300:  # Late game - accept any help
                    return True
                    
        all_constraints_met = all(
            current.get(trait, 0) >= target 
            for trait, target in self.constraints.items()
        )
        
        return all_constraints_met
        
    def run_winning_priority_strategy(self) -> Dict:
        """Run scenario 3 with winning priority strategy."""
        print("=== Winning Priority Scenario 3 Strategy ===")
        print("Priority traits: queer_friendly, vinyl_collector, german_speaker")
        print("Strategy: Priority traits + early constraint filling to ensure scenario completion")
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
            
            accept = self._should_accept_winning_priority(attrs, counts, admitted)
            
            if accept:
                admitted += 1
                for attr, has in attrs.items():
                    if has and attr in counts:
                        counts[attr] += 1
            else:
                rejected += 1
                
            result = self.make_decision(game_id, index, accept)
            
            if index % 200 == 0:
                active_traits = self._get_active_priority_traits(counts)
                remaining = 1000 - admitted
                print(f"Person {index}: Remaining capacity: {remaining}")
                print(f"  Active priority traits: {active_traits}")
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
            "strategy": "winning_priority_with_early_transition",
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
    optimizer = WinningPriorityScenario3()
    result = optimizer.run_winning_priority_strategy()
    
    output = {
        "strategy": "winning_priority_with_early_transition",
        "priority_traits": list(optimizer.priority_traits),
        "constraints": optimizer.constraints,
        "result": result,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    with open("winning_priority_result.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\n=== WINNING PRIORITY STRATEGY RESULTS ===")
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
        print("Unmet constraints:")
        for trait, target in optimizer.constraints.items():
            count = result['final_counts'].get(trait, 0)
            if count < target:
                deficit = target - count
                print(f"  - {trait}: {count}/{target} (need {deficit} more)")


if __name__ == "__main__":
    main()
