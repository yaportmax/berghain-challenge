#!/usr/bin/env python3

from bouncer import BerghainBouncer
import json

def main():
    bouncer = BerghainBouncer()
    results = []
    total_rejections = 0
    
    print("=== Berghain Bouncer Challenge ===")
    print("Running all 3 scenarios...\n")
    
    for scenario in [1, 2, 3]:
        try:
            result = bouncer.run_scenario(scenario)
            results.append(result)
            
            if result["status"] == "completed":
                total_rejections += result["rejected_count"]
                print(f"✅ Scenario {scenario}: {result['rejected_count']} rejections")
            else:
                print(f"❌ Scenario {scenario}: Failed - {result.get('reason', 'Unknown')}")
            
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Scenario {scenario}: Error - {str(e)}")
            import traceback
            traceback.print_exc()
            print("-" * 50)
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Total rejections across all scenarios: {total_rejections}")
    print(f"Current leaderboard best: 7893")
    
    if total_rejections > 0 and total_rejections < 7893:
        print(f"🎉 NEW RECORD! Improved by {7893 - total_rejections} rejections!")
    
    with open("results.json", "w") as f:
        json.dump({
            "total_rejections": total_rejections,
            "scenarios": results,
            "timestamp": "2025-09-05"
        }, f, indent=2)
    
    print(f"\nDetailed results saved to results.json")

if __name__ == "__main__":
    main()
