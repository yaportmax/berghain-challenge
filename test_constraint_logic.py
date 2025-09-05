#!/usr/bin/env python3

"""
Test script to analyze the constraint logic issues in the bouncer algorithm.
This helps understand why the algorithm stops accepting after meeting one constraint.
"""

from bouncer import BerghainBouncer

def test_acceptance_probability():
    """Test the acceptance probability calculation with different constraint scenarios"""
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
    
    print("=== Testing Constraint Logic Issues ===\n")
    
    current_counts_1 = {"young": 600, "well_dressed": 592}
    person_well_dressed = {"young": False, "well_dressed": True}
    admitted_count_1 = 592
    
    prob_1 = bouncer.calculate_acceptance_probability(
        person_well_dressed, constraints, attribute_stats, current_counts_1, admitted_count_1
    )
    print(f"Case 1 - One constraint met, one unmet (young: 600/600, well_dressed: 592/600)")
    print(f"Person has well_dressed only: {person_well_dressed}")
    print(f"Acceptance probability: {prob_1:.3f}")
    print(f"Would accept (>0.2): {prob_1 > 0.2}\n")
    
    current_counts_2 = {"young": 600, "well_dressed": 604}
    person_any = {"young": True, "well_dressed": False}
    admitted_count_2 = 946  # From the test run
    
    prob_2 = bouncer.calculate_acceptance_probability(
        person_any, constraints, attribute_stats, current_counts_2, admitted_count_2
    )
    print(f"Case 2 - Both constraints met (young: 600/600, well_dressed: 604/600)")
    print(f"Person has young only: {person_any}")
    print(f"Admitted count: {admitted_count_2}, Remaining capacity: {1000 - admitted_count_2}")
    print(f"Acceptance probability: {prob_2:.3f}")
    print(f"Would accept (>0.2): {prob_2 > 0.2}")
    print(f"This should accept some people to fill remaining capacity!\n")
    
    person_none = {"young": False, "well_dressed": False}
    prob_3 = bouncer.calculate_acceptance_probability(
        person_none, constraints, attribute_stats, current_counts_2, admitted_count_2
    )
    print(f"Case 3 - Both constraints met, person has no relevant attributes")
    print(f"Person has no attributes: {person_none}")
    print(f"Acceptance probability: {prob_3:.3f}")
    print(f"Would accept (>0.2): {prob_3 > 0.2}")
    print(f"Should still accept some to minimize rejections!")

if __name__ == "__main__":
    test_acceptance_probability()
