#!/usr/bin/env python3
"""
Debug script to test the acceptance logic in isolation.
"""

from iterative_scenario3_optimizer import IterativeScenario3Optimizer

def test_acceptance_logic():
    optimizer = IterativeScenario3Optimizer()
    
    current_counts = {
        "vinyl_collector": 200,  # Target met
        "queer_friendly": 50,    # Still need 200 more
        "german_speaker": 300,   # Still need 500 more
        "underground_veteran": 100,  # Still need 400 more
        "fashion_dressed": 150,  # Still need 400 more
        "international": 200     # Still need 450 more
    }
    
    admitted = 561  # Current admitted count from the stuck run
    focus_trait = "vinyl_collector"
    
    print("=== Testing Acceptance Logic ===")
    print(f"Current counts: {current_counts}")
    print(f"Admitted: {admitted}")
    print(f"Focus trait: {focus_trait}")
    print()
    
    attrs1 = {"vinyl_collector": True, "queer_friendly": False, "german_speaker": False, 
              "underground_veteran": False, "fashion_dressed": False, "international": False}
    result1 = optimizer._should_accept_rare_trait_strategy(attrs1, current_counts, admitted, focus_trait)
    print(f"Person with vinyl_collector only: {result1}")
    
    attrs2 = {"vinyl_collector": False, "queer_friendly": True, "german_speaker": False, 
              "underground_veteran": False, "fashion_dressed": False, "international": False}
    result2 = optimizer._should_accept_rare_trait_strategy(attrs2, current_counts, admitted, focus_trait)
    print(f"Person with queer_friendly only: {result2}")
    
    attrs3 = {"vinyl_collector": False, "queer_friendly": False, "german_speaker": True, 
              "underground_veteran": False, "fashion_dressed": False, "international": False}
    result3 = optimizer._should_accept_rare_trait_strategy(attrs3, current_counts, admitted, focus_trait)
    print(f"Person with german_speaker only: {result3}")
    
    attrs4 = {"vinyl_collector": False, "queer_friendly": False, "german_speaker": False, 
              "underground_veteran": False, "fashion_dressed": False, "international": False}
    result4 = optimizer._should_accept_rare_trait_strategy(attrs4, current_counts, admitted, focus_trait)
    print(f"Person with no traits: {result4}")
    
    all_met_counts = {
        "vinyl_collector": 200,
        "queer_friendly": 250,
        "german_speaker": 800,
        "underground_veteran": 500,
        "fashion_dressed": 550,
        "international": 650
    }
    
    result5 = optimizer._should_accept_rare_trait_strategy(attrs4, all_met_counts, 900, focus_trait)
    print(f"All constraints met, no traits: {result5}")
    
    print()
    print("=== Constraint Analysis ===")
    remaining_capacity = 1000 - admitted
    print(f"Remaining capacity: {remaining_capacity}")
    
    for trait, target in optimizer.constraints.items():
        current = current_counts.get(trait, 0)
        deficit = max(0, target - current)
        print(f"{trait}: {current}/{target} (deficit: {deficit})")

if __name__ == "__main__":
    test_acceptance_logic()
