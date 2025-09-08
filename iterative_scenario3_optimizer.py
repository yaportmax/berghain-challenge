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
        
    def _should_accept_rare_trait_strategy(
        self, 
        attrs: Dict[str, bool], 
        current: Dict[str, int], 
        admitted: int,
        focus_trait: str
    ) -> bool:
        """
        Accept people who have the focus trait OR help with other unmet constraints.
        This prioritizes the rarest traits while still making progress on others.
        """
        remaining_capacity = 1000 - admitted
        if remaining_capacity <= 0:
            return False
            
        if attrs.get(focus_trait, False) and current.get(focus_trait, 0) < self.constraints[focus_trait]:
            return True
            
        for trait, target in self.constraints.items():
            if attrs.get(trait, False) and current.get(trait, 0) < target:
                return True
            
        all_constraints_met = all(
            current.get(trait, 0) >= target 
            for trait, target in self.constraints.items()
        )
        
        if all_constraints_met:
            return True
            
        return False
        
    def run_with_strategy(self, focus_trait: str, existing_game_id: str | None = None) -> Dict:
        """Run scenario 3 with focus on a specific rare trait."""
        print(f"Running scenario 3 with focus on: {focus_trait}")
        print(f"Trait frequency: {self.trait_frequencies[focus_trait]:.3f}")
        print(f"Target count: {self.constraints[focus_trait]}/1000")
        
        if existing_game_id:
            game_id = existing_game_id
            result = self.make_decision(game_id, 0)
        else:
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
            
            accept = self._should_accept_rare_trait_strategy(
                attrs, counts, admitted, focus_trait
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
                print(f"Person {index}: Focus trait {focus_trait}: {counts.get(focus_trait, 0)}/{self.constraints[focus_trait]}")
                print(f"  Admitted: {admitted}, Rejected: {rejected}")
                
        final_status = result.get("status", "unknown")
        if final_status == "running":
            final_status = "completed"
            
        return {
            "focus_trait": focus_trait,
            "status": final_status,
            "rejected_count": result.get("rejectedCount", rejected),
            "admitted_count": admitted,
            "final_counts": counts,
            "game_id": game_id
        }
        
    def run_iterative_optimization(self, max_iterations: int = 6) -> List[Dict]:
        """Run iterative optimization focusing on each trait in order of rarity."""
        results = []
        
        print("=== Iterative Scenario 3 Optimization ===")
        print("Strategy: Focus on rarest traits first")
        print(f"Trait priority order: {self.trait_priority}")
        print()
        
        for i, focus_trait in enumerate(self.trait_priority):
            if i >= max_iterations:
                break
                
            print(f"\n--- Iteration {i+1}/{min(max_iterations, len(self.trait_priority))} ---")
            
            try:
                result = self.run_with_strategy(focus_trait)
                results.append(result)
                
                print(f"✅ Completed with {result['rejected_count']} rejections")
                print(f"Final counts: {result['final_counts']}")
                
                if i < min(max_iterations, len(self.trait_priority)) - 1:
                    print("Waiting 15 seconds before next iteration...")
                    time.sleep(15)
                    
            except Exception as e:
                print(f"❌ Error in iteration {i+1}: {e}")
                if "rate" in str(e).lower() or "limit" in str(e).lower():
                    print("Hit rate limit. Stopping optimization.")
                    break
                results.append({
                    "focus_trait": focus_trait,
                    "status": "failed",
                    "error": str(e)
                })
                
        return results
        
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
    results = optimizer.run_iterative_optimization()
    
    output = optimizer.save_results(results)
    
    print("\n=== OPTIMIZATION SUMMARY ===")
    successful_runs = [r for r in results if r.get("status") in ["completed", "finished"]]
    
    if successful_runs:
        best_result = min(successful_runs, key=lambda x: x.get("rejected_count", float('inf')))
        print(f"Best result: {best_result['rejected_count']} rejections")
        print(f"Focus trait: {best_result['focus_trait']}")
        print(f"Final counts: {best_result['final_counts']}")
        
        avg_rejections = sum(r.get("rejected_count", 0) for r in successful_runs) / len(successful_runs)
        print(f"Average rejections: {avg_rejections:.1f}")
    else:
        print("No successful runs completed.")


if __name__ == "__main__":
    main()
