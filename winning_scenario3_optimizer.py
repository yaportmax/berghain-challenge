#!/usr/bin/env python3
"""
Winning optimization strategy for scenario 3 focusing on the 3 rarest traits.

Strategy per user requirements:
1. Focus on queer_friendly, vinyl_collector, and german_speaker (3 rarest traits)
2. Only accept people who have at least one of those 3 traits (until each is capped)
3. Once a trait is capped, stop factoring it into targeting
4. Ensure all 6 constraints are met within 1000 people to win the scenario
5. Prioritize winning over minimizing rejections

Adaptive phases:
- Early (0-600): Strict priority trait focus only
- Mid (600-800): Priority traits OR other unmet constraints  
- Late (800-1000): Accept anyone who helps with any unmet constraint
"""

import json
import time
from typing import Dict, List, Set
from bouncer import BerghainBouncer


class WinningScenario3Optimizer(BerghainBouncer):
    """Winning optimizer prioritizing the 3 rarest traits for scenario 3."""
    
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
        """Get priority traits that haven't reached their target yet."""
        active_traits = set()
        for trait in self.priority_traits:
            if current.get(trait, 0) < self.constraints[trait]:
                active_traits.add(trait)
        return active_traits
        
    def _should_accept_winning_strategy(
        self, 
        attrs: Dict[str, bool], 
        current: Dict[str, int], 
        admitted: int
    ) -> bool:
        """
        Adaptive strategy to ensure scenario completion:
        1. Early phase (0-600): Only accept people with priority traits
        2. Mid phase (600-800): Accept priority traits OR other unmet constraints  
        3. Late phase (800-1000): Accept anyone who helps with any unmet constraint
        """
        remaining_capacity = 1000 - admitted
        if remaining_capacity <= 0:
            return False
            
        active_priority_traits = self._get_active_priority_traits(current)
        
        if admitted < 600:
            if not active_priority_traits:
                for trait, target in self.constraints.items():
                    if attrs.get(trait, False) and current.get(trait, 0) < target:
                        return True
                return False
            
            has_priority_trait = any(
                attrs.get(trait, False) for trait in active_priority_traits
            )
            return has_priority_trait
            
        elif admitted < 800:
            if active_priority_traits:
                has_priority_trait = any(
                    attrs.get(trait, False) for trait in active_priority_traits
                )
                if has_priority_trait:
                    return True
                
            for trait, target in self.constraints.items():
                if attrs.get(trait, False) and current.get(trait, 0) < target:
                    return True
            return False
            
        else:
            for trait, target in self.constraints.items():
                if attrs.get(trait, False) and current.get(trait, 0) < target:
                    return True
                    
            all_constraints_met = all(
                current.get(trait, 0) >= target 
                for trait, target in self.constraints.items()
            )
            
            return all_constraints_met
        
    def run_winning_strategy(self) -> Dict:
        """Run scenario 3 with winning strategy on 3 rarest traits."""
        print("=== Winning Scenario 3 Strategy ===")
        print("Priority traits: queer_friendly, vinyl_collector, german_speaker")
        print("Strategy: Adaptive phases to ensure all constraints met within 1000 people")
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
            
            accept = self._should_accept_winning_strategy(attrs, counts, admitted)
            
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
                phase = "Early" if admitted < 600 else "Mid" if admitted < 800 else "Late"
                print(f"Person {index} ({phase} phase): Active priority traits: {active_traits}")
                print(f"  Priority counts: queer_friendly={counts.get('queer_friendly', 0)}/250, "
                      f"vinyl_collector={counts.get('vinyl_collector', 0)}/200, "
                      f"german_speaker={counts.get('german_speaker', 0)}/800")
                print(f"  All counts: {counts}")
                print(f"  Admitted: {admitted}, Rejected: {rejected}")
                
        final_status = result.get("status", "unknown")
        if final_status == "running":
            final_status = "completed"
            
        constraints_met = all(
            counts.get(trait, 0) >= target 
            for trait, target in self.constraints.items()
        )
        
        return {
            "strategy": "winning_3_rarest_traits_adaptive",
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
        
    def save_results(self, result: Dict, filename: str = "winning_optimization_result.json"):
        """Save optimization result to file."""
        output = {
            "strategy_description": "Adaptive phases focusing on 3 rarest traits to win scenario",
            "priority_traits": list(self.priority_traits),
            "constraints": self.constraints,
            "result": result,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        with open(filename, "w") as f:
            json.dump(output, f, indent=2)
            
        print(f"\nResults saved to {filename}")
        return output


def main():
    optimizer = WinningScenario3Optimizer()
    result = optimizer.run_winning_strategy()
    
    output = optimizer.save_results(result)
    
    print("\n=== WINNING STRATEGY RESULTS ===")
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
