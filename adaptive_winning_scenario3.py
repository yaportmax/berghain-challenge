#!/usr/bin/env python3
"""
Adaptive winning strategy for scenario 3 that ensures all constraints are met.

Strategy:
1. Start by prioritizing queer_friendly, vinyl_collector, and german_speaker
2. Gradually become more permissive as capacity runs out to ensure scenario completion
3. Use dynamic thresholds based on remaining capacity and constraint deficits
4. Prioritize winning over strict adherence to priority trait rules
"""

import json
import time
from typing import Dict, List, Set
from bouncer import BerghainBouncer


class AdaptiveWinningScenario3(BerghainBouncer):
    """Adaptive winning optimizer that ensures all constraints are met."""
    
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
        
    def _should_accept_adaptive_strategy(
        self, 
        attrs: Dict[str, bool], 
        current: Dict[str, int], 
        admitted: int
    ) -> bool:
        """
        Adaptive strategy that becomes more permissive as capacity runs out:
        1. Early: Prefer priority traits but accept anyone who helps significantly
        2. Mid: Accept priority traits OR anyone who helps with large deficits
        3. Late: Accept anyone who helps with any unmet constraint
        """
        remaining_capacity = 1000 - admitted
        if remaining_capacity <= 0:
            return False
            
        urgency_factor = 1.0 - (remaining_capacity / 1000.0)  # 0.0 to 1.0
        
        for trait in self.priority_traits:
            if attrs.get(trait, False) and current.get(trait, 0) < self.constraints[trait]:
                return True
        
        large_deficits = []
        medium_deficits = []
        small_deficits = []
        
        for trait, target in self.constraints.items():
            current_count = current.get(trait, 0)
            deficit = target - current_count
            
            if deficit > 0 and attrs.get(trait, False):
                if deficit >= 200:  # Large deficit
                    large_deficits.append(trait)
                elif deficit >= 100:  # Medium deficit
                    medium_deficits.append(trait)
                elif deficit > 0:  # Small deficit
                    small_deficits.append(trait)
        
        if admitted < 400:
            return len(large_deficits) > 0
            
        elif admitted < 700:
            return len(large_deficits) > 0 or len(medium_deficits) > 0
            
        elif admitted < 900:
            return len(large_deficits) > 0 or len(medium_deficits) > 0 or len(small_deficits) > 0
            
        else:
            for trait, target in self.constraints.items():
                if attrs.get(trait, False) and current.get(trait, 0) < target:
                    return True
                    
        all_constraints_met = all(
            current.get(trait, 0) >= target 
            for trait, target in self.constraints.items()
        )
        
        return all_constraints_met
        
    def run_adaptive_strategy(self) -> Dict:
        """Run scenario 3 with adaptive strategy."""
        print("=== Adaptive Winning Scenario 3 Strategy ===")
        print("Priority traits: queer_friendly, vinyl_collector, german_speaker")
        print("Strategy: Adaptive phases that become more permissive to ensure scenario completion")
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
            
            accept = self._should_accept_adaptive_strategy(attrs, counts, admitted)
            
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
                phase = "Early" if admitted < 400 else "Mid" if admitted < 700 else "Late" if admitted < 900 else "Final"
                print(f"Person {index} ({phase} phase): Remaining capacity: {remaining}")
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
            "strategy": "adaptive_winning_phases",
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
    optimizer = AdaptiveWinningScenario3()
    result = optimizer.run_adaptive_strategy()
    
    output = {
        "strategy": "adaptive_winning_phases",
        "priority_traits": list(optimizer.priority_traits),
        "constraints": optimizer.constraints,
        "result": result,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    with open("adaptive_optimization_result.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\n=== ADAPTIVE WINNING STRATEGY RESULTS ===")
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
