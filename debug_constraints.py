#!/usr/bin/env python3

"""
Debug script to test constraint detection logic
"""

from bouncer import BerghainBouncer

def debug_constraint_detection():
    bouncer = BerghainBouncer()
    
    constraints = [
        {"attribute": "young", "minCount": 600},
        {"attribute": "well_dressed", "minCount": 600}
    ]
    
    current_counts = {"young": 598, "well_dressed": 582}
    
    print("=== Debugging Constraint Detection ===")
    print(f"Constraints: {constraints}")
    print(f"Current counts: {current_counts}")
    
    unmet_constraints = []
    for constraint in constraints:
        attr = constraint["attribute"]
        min_count = constraint["minCount"]
        current_count = current_counts.get(attr, 0)
        remaining_needed = max(0, min_count - current_count)
        print(f"{attr}: {current_count}/{min_count}, remaining needed: {remaining_needed}")
        if remaining_needed > 0:
            unmet_constraints.append((attr, remaining_needed))
    
    print(f"Unmet constraints: {unmet_constraints}")
    print(f"All constraints met: {len(unmet_constraints) == 0}")
    
    person_well_dressed = {"young": False, "well_dressed": True}
    admitted_count = 898
    
    attribute_stats = {
        "relativeFrequencies": {"young": 0.502, "well_dressed": 0.601},
        "correlations": {}
    }
    
    prob = bouncer.calculate_acceptance_probability(
        person_well_dressed, constraints, attribute_stats, current_counts, admitted_count
    )
    
    print(f"\nPerson with well_dressed attribute:")
    print(f"Acceptance probability: {prob:.3f}")
    print(f"Would accept (>0.5): {prob > 0.5}")
    print(f"This should be HIGH since well_dressed needs 18 more!")

if __name__ == "__main__":
    debug_constraint_detection()
