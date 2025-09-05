#!/usr/bin/env python3

from bouncer import BerghainBouncer
import json
import time

def final_test():
    bouncer = BerghainBouncer()
    results = []
    total_rejections = 0
    
    print("=== Final Berghain Bouncer Test ===")
    print("Creating fresh games for each scenario...\n")
    
    for scenario in [1, 2, 3]:
        print(f"Testing Scenario {scenario}...")
        
        try:
            result = bouncer.run_scenario(scenario)
            results.append(result)
            
            if result["status"] == "completed":
                total_rejections += result["rejected_count"]
                print(f"✅ Scenario {scenario}: {result['rejected_count']} rejections")
                print(f"   Admitted: {result['admitted_count']}")
                print(f"   Final counts: {result['final_counts']}")
            elif result["status"] == "failed":
                print(f"❌ Scenario {scenario}: Failed - {result.get('reason', 'Unknown')}")
            else:
                print(f"⚠️ Scenario {scenario}: Status {result['status']}")
            
        except Exception as e:
            print(f"❌ Scenario {scenario}: Exception - {str(e)}")
            if "Rate limited" in str(e) or "rateLimited" in str(e):
                print("Hit rate limit. Stopping test.")
                break
        
        print("-" * 50)
        
        if scenario < 3:
            print("Waiting 5 seconds before next scenario...")
            time.sleep(5)
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Total rejections across all scenarios: {total_rejections}")
    print(f"Current leaderboard best: 7893")
    
    if total_rejections > 0 and total_rejections < 7893:
        print(f"🎉 NEW RECORD! Improved by {7893 - total_rejections} rejections!")
    elif total_rejections > 0:
        print(f"Result: {total_rejections} rejections (vs leaderboard best: 7893)")
    
    with open("final_test_results.json", "w") as f:
        json.dump({
            "total_rejections": total_rejections,
            "scenarios": results,
            "timestamp": "2025-09-05T02:36:00Z"
        }, f, indent=2)
    
    print(f"\nDetailed results saved to final_test_results.json")
    
    return results

if __name__ == "__main__":
    final_test()
