#!/usr/bin/env python3

"""
Debug script to understand why acceptance probability is too low when all constraints are met
"""

from bouncer import BerghainBouncer

def debug_all_constraints_met():
    """Debug the acceptance probability when all constraints are met but capacity remains"""
    bouncer = BerghainBouncer()
    
    constraints = [
        {"attribute": "young", "minCount": 600},
        {"attribute": "well_dressed", "minCount": 600}
    ]
    
    attribute_stats = {
        "relativeFrequencies": {
            "young": 0.502, 
            "well_dressed": 0.601
        },
        "correlations": {}
    }
    
    print("=== Debugging All Constraints Met Scenario ===\n")
    
    current_counts = {"young": 600, "well_dressed": 600}
    admitted_count = 929
    remaining_capacity = 1000 - admitted_count
    
    print(f"Current counts: {current_counts}")
    print(f"Admitted count: {admitted_count}")
    print(f"Remaining capacity: {remaining_capacity}")
    print(f"Both constraints met: young {current_counts['young']}/600, well_dressed {current_counts['well_dressed']}/600\n")
    
    test_cases = [
        {"young": True, "well_dressed": True, "desc": "Person with both attributes"},
        {"young": True, "well_dressed": False, "desc": "Person with young only"},
        {"young": False, "well_dressed": True, "desc": "Person with well_dressed only"},
        {"young": False, "well_dressed": False, "desc": "Person with no relevant attributes"}
    ]
    
    for person_attrs in test_cases:
        desc = person_attrs.pop("desc")
        prob = bouncer.calculate_acceptance_probability(
            person_attrs, constraints, attribute_stats, current_counts, admitted_count
        )
        print(f"{desc}: {person_attrs}")
        print(f"  Acceptance probability: {prob:.3f}")
        print(f"  Would accept (>0.4): {prob > 0.4}")
        print(f"  Expected: Should accept some people to fill remaining {remaining_capacity} capacity!")
        print()

if __name__ == "__main__":
    debug_all_constraints_met()
