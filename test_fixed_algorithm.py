#!/usr/bin/env python3

from bouncer import BerghainBouncer
import json

def test_fixed_algorithm():
    bouncer = BerghainBouncer()
    
    game_ids = [
        "569d11ab-2fff-4b6a-bcaa-1911634476a0",  # Scenario 1
        "952043b1-4ce8-48d4-85e5-b3d2df1400a4",  # Another Scenario 1 game
    ]
    
    print("=== Testing Fixed Algorithm ===")
    
    for i, game_id in enumerate(game_ids, 1):
        print(f"\nTesting with Game ID {i}: {game_id}")
        
        try:
            current_counts = {"young": 0, "well_dressed": 0}
            admitted_count = 0
            rejected_count = 0
            
            result = bouncer.make_decision(game_id, 0)
            print(f"Initial result: {result.get('status', 'no status')}")
            
            for iteration in range(5):
                if result.get("status") != "running":
                    break
                    
                person = result["nextPerson"]
                person_attributes = person["attributes"]
                current_person_index = person["personIndex"]
                
                print(f"  Person {current_person_index}: {person_attributes}")
                
                accept = person_attributes.get("young", False) or person_attributes.get("well_dressed", False)
                
                if accept:
                    admitted_count += 1
                    for attr, has_attr in person_attributes.items():
                        if has_attr and attr in current_counts:
                            current_counts[attr] += 1
                else:
                    rejected_count += 1
                
                print(f"  Decision: {'ACCEPT' if accept else 'REJECT'}")
                
                result = bouncer.make_decision(game_id, current_person_index, accept)
                
                if "error" in result:
                    print(f"  ERROR: {result['error']}")
                    break
                else:
                    print(f"  API Response: {result.get('status', 'no status')}")
                    print(f"  Counts: Admitted={result.get('admittedCount', admitted_count)}, Rejected={result.get('rejectedCount', rejected_count)}")
            
            print(f"Test completed for game {game_id}")
            
        except Exception as e:
            print(f"Error testing game {game_id}: {e}")
        
        print("-" * 60)

if __name__ == "__main__":
    test_fixed_algorithm()
