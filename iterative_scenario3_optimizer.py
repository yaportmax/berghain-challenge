#!/usr/bin/env python3
"""
Iterative optimization strategy for scenario 3 focusing on rarest traits first.

Strategy:
1. Start with rarest trait (vinyl_collector: 0.201 frequency, need 200/1000)
2. Then queer_friendly (0.251 frequency, need 250/1000) 
3. Then german_speaker (0.4565 frequency, need 800/1000)
4. Then underground_veteran (0.501 frequency, need 500/1000)
5. Then fashion_dressed (0.551 frequency, need 550/1000)
6. Finally international (0.651 frequency, need 650/1000)

Accept people who have the current focus trait OR all other required traits.
Run games to completion and record results between iterations.
"""

import json
import time
from typing import Dict, List
from bouncer import BerghainBouncer


class IterativeScenario3Optimizer(BerghainBouncer):
    """Iterative optimizer focusing on rarest traits first for scenario 3."""
    
    def __init__(self):
        super().__init__()
        self.trait_frequencies = {
            "vinyl_collector": 0.201,      
            "queer_friendly": 0.251,       
            "german_speaker": 0.4565,      
            "underground_veteran": 0.501,  
            "fashion_dressed": 0.551,      
            "international": 0.651         
        }
        
        self.constraints = {
            "vinyl_collector": 200,
            "queer_friendly": 250,
            "german_speaker": 800,
            "underground_veteran": 500,
            "fashion_dressed": 550,
            "international": 650
        }
        
        self.trait_priority = sorted(
            self.trait_frequencies.keys(), 
            key=lambda x: self.trait_frequencies[x]
        )
        
    def _should_accept_priority_strategy(
        self, 
        attrs: Dict[str, bool], 
        current: Dict[str, int], 
        admitted: int
    ) -> bool:
        """
        Accept people who have at least one of the 3 priority traits OR help with any unmet constraint.
        Priority traits: queer_friendly, vinyl_collector, german_speaker
        """
        remaining_capacity = 1000 - admitted
        if remaining_capacity <= 0:
            return False
            
        priority_traits = {"queer_friendly", "vinyl_collector", "german_speaker"}
        for trait in priority_traits:
            if attrs.get(trait, False) and current.get(trait, 0) < self.constraints[trait]:
                return True
        
        # Accept people who help with ANY unmet constraint to ensure scenario completion
        for trait, target in self.constraints.items():
            if attrs.get(trait, False) and current.get(trait, 0) < target:
                return True
            
        all_constraints_met = all(
            current.get(trait, 0) >= target 
            for trait, target in self.constraints.items()
        )
        
        return all_constraints_met
        
    def run_priority_strategy(self) -> Dict:
        """Run scenario 3 with priority on the 3 rarest traits."""
        print("=== Priority Traits Scenario 3 Strategy ===")
        print("Priority traits: queer_friendly, vinyl_collector, german_speaker")
        print("Strategy: Accept people with at least one priority trait OR anyone who helps with unmet constraints")
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
            
            accept = self._should_accept_priority_strategy(
                attrs, counts, admitted
            )
            
            if accept:
                admitted += 1
                for attr, has in attrs.items():
                    if has and attr in counts:
                        counts[attr] += 1
            else:
                rejected += 1
                
            result = self.make_decision(game_id, index, accept)
            
            if index % 200 == 0:
                priority_traits = {"queer_friendly", "vinyl_collector", "german_speaker"}
                active_priority = [t for t in priority_traits if counts.get(t, 0) < self.constraints[t]]
                print(f"Person {index}: Active priority traits: {active_priority}")
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
            "strategy": "priority_3_rarest_traits",
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
        
    def run_single_priority_game(self) -> Dict:
        """Run a single game with priority traits strategy."""
        try:
            result = self.run_priority_strategy()
            print(f"✅ Completed with {result['rejected_count']} rejections")
            print(f"Scenario won: {result['scenario_won']}")
            print(f"Final counts: {result['final_counts']}")
            return result
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                "strategy": "priority_3_rarest_traits",
                "status": "failed",
                "scenario_won": False,
                "error": str(e)
            }
        
    def save_results(self, results: List[Dict], filename: str = "iterative_optimization_results.json"):
        """Save optimization results to file."""
        output = {
            "strategy": "rare_traits_first",
            "trait_priority": self.trait_priority,
            "trait_frequencies": self.trait_frequencies,
            "constraints": self.constraints,
            "results": results,
            "total_iterations": len(results),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        with open(filename, "w") as f:
            json.dump(output, f, indent=2)
            
        print(f"\nResults saved to {filename}")
        return output


def main():
    optimizer = IterativeScenario3Optimizer()
    result = optimizer.run_single_priority_game()
    
    output = {
        "strategy": "priority_3_rarest_traits",
        "priority_traits": ["queer_friendly", "vinyl_collector", "german_speaker"],
        "constraints": optimizer.constraints,
        "result": result,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    with open("priority_optimization_result.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\n=== PRIORITY STRATEGY RESULTS ===")
    print(f"Scenario won: {result.get('scenario_won', False)}")
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Rejections: {result.get('rejected_count', 'unknown')}")
    print(f"Admitted: {result.get('admitted_count', 'unknown')}")
    
    if result.get('final_counts'):
        print("\nConstraint achievement:")
        for trait, target in optimizer.constraints.items():
            count = result['final_counts'].get(trait, 0)
            met = result.get('constraints_met', {}).get(trait, False)
            percentage = (count / target) * 100
            status = "✅" if met else "❌"
            print(f"  {status} {trait}: {count}/{target} ({percentage:.1f}%)")
    
    if result.get('scenario_won'):
        print("\n🎉 SCENARIO 3 WON! All constraints met within 1000 people.")
    else:
        print("\n❌ Scenario not won. Some constraints not met.")


if __name__ == "__main__":
    main()
