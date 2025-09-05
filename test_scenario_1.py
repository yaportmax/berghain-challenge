#!/usr/bin/env python3

"""
Test script to run only scenario 1 and check if rejections are under 800.
"""

from bouncer import BerghainBouncer
import time

def test_scenario_1():
    bouncer = BerghainBouncer()
    
    print("=== Testing Optimized Scenario 1 ===")
    print("Target: Reduce rejections from ~1766 to under 800\n")
    
    try:
        result = bouncer.run_scenario(1)
        
        if result["status"] == "completed":
            rejections = result["rejected_count"]
            admitted = result["admitted_count"]
            final_counts = result["final_counts"]
            
            print(f"✅ Scenario 1 completed!")
            print(f"Rejections: {rejections}")
            print(f"Admitted: {admitted}")
            print(f"Final counts: {final_counts}")
            print(f"Young constraint: {final_counts.get('young', 0)}/600")
            print(f"Well_dressed constraint: {final_counts.get('well_dressed', 0)}/600")
            
            if rejections < 800:
                print(f"🎉 SUCCESS! Rejections ({rejections}) are under 800!")
                return True
            else:
                print(f"❌ Still too many rejections: {rejections} (target: <800)")
                return False
                
        else:
            print(f"❌ Scenario 1 failed with status: {result['status']}")
            print(f"Reason: {result.get('reason', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during scenario 1: {str(e)}")
        if "Rate limited" in str(e):
            print("Hit rate limit. Try again later or use existing game ID.")
        return False

if __name__ == "__main__":
    success = test_scenario_1()
    if success:
        print("\nOptimization successful! Ready to commit changes.")
    else:
        print("\nOptimization needs further tuning.")
