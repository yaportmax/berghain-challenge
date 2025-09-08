#!/usr/bin/env python3
"""
Strict priority strategy for scenario 3 that follows user requirements exactly.

Strategy per user requirements:
1. Focus on queer_friendly, vinyl_collector, and german_speaker (3 rarest traits)
2. ONLY accept people with AT LEAST ONE of those 3 traits
3. Once a trait reaches its cap, stop factoring it into targeting decisions
4. Continue until all 6 constraints are met within 1000 people
5. Prioritize winning the scenario over minimizing rejections
"""

import json
import time
from typing import Dict, List, Set
from bouncer import BerghainBouncer


class StrictPriorityScenario3(BerghainBouncer):
    """Strict priority optimizer that follows user requirements exactly."""
    
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
        
    def _should_accept_strict_priority(
        self, 
        attrs: Dict[str, bool], 
        current: Dict[str, int], 
        admitted: int
    ) -> bool:
        """
        Strict priority strategy per user requirements:
        1. ONLY accept people with at least one active priority trait
        2. Once a trait is capped, stop factoring it in
        3. Continue until venue is full (1000 people)
        """
        remaining_capacity = 1000 - admitted
        if remaining_capacity <= 0:
            return False
            
        active_priority_traits = self._get_active_priority_traits(current)
        
        if active_priority_traits:
            has_active_priority_trait = any(
                attrs.get(trait, False) for trait in active_priority_traits
            )
            return has_active_priority_trait
            
        remaining_deficits = {}
        for trait, target in self.constraints.items():
            deficit = max(0, target - current.get(trait, 0))
            remaining_deficits[trait] = deficit
            
        for trait, deficit in remaining_deficits.items():
            if deficit > 0 and attrs.get(trait, False):
                return True
                
        all_constraints_met = all(deficit == 0 for deficit in remaining_deficits.values())
        return all_constraints_met
        
    def run_strict_priority_strategy(self) -> Dict:
        """Run scenario 3 with strict priority strategy."""
        print("=== Strict Priority Scenario 3 Strategy ===")
        print("Priority traits: queer_friendly, vinyl_collector, german_speaker")
        print("Strategy: ONLY accept people with at least one priority trait until capped, then strategically fill remaining constraints")
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
            
            accept = self._should_accept_strict_priority(attrs, counts, admitted)
            
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
                print(f"  All counts: {counts}")
                print(f"  Admitted: {admitted}, Rejected: {rejected}")
                
                capped_traits = [t for t in self.priority_traits if counts.get(t, 0) >= self.constraints[t]]
                if capped_traits:
                    print(f"  Capped priority traits: {capped_traits}")
                
        final_status = result.get("status", "unknown")
        if final_status == "running":
            final_status = "completed"
            
        constraints_met = all(
            counts.get(trait, 0) >= target 
            for trait, target in self.constraints.items()
        )
        
        return {
            "strategy": "strict_priority_traits_only",
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
    optimizer = StrictPriorityScenario3()
    result = optimizer.run_strict_priority_strategy()
    
    output = {
        "strategy": "strict_priority_traits_only",
        "priority_traits": list(optimizer.priority_traits),
        "constraints": optimizer.constraints,
        "result": result,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    with open("strict_priority_result.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\n=== STRICT PRIORITY STRATEGY RESULTS ===")
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
