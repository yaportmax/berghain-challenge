#!/usr/bin/env python3

from bouncer import BerghainBouncer
import json

def run_complete_test():
    bouncer = BerghainBouncer()
    results = []
    total_rejections = 0
    
    print("=== Complete Berghain Bouncer Test ===")
    print("Testing fixed algorithm with working game ID...\n")
    
    working_game_id = "569d11ab-2fff-4b6a-bcaa-1911634476a0"
    
    print(f"Testing Scenario 1 with Game ID: {working_game_id}")
    
    try:
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
        
        result = bouncer._run_game_loop(working_game_id, 1, constraints, attribute_stats)
        results.append(result)
        
        if result["status"] == "completed":
            total_rejections += result["rejected_count"]
            print(f"✅ Scenario 1: {result['rejected_count']} rejections")
            print(f"   Admitted: {result['admitted_count']}")
            print(f"   Final counts: {result['final_counts']}")
        else:
            print(f"❌ Scenario 1: {result['status']} - {result.get('reason', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Scenario 1: Error - {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n=== RESULTS ===")
    print(f"Total rejections: {total_rejections}")
    print(f"Current leaderboard best: 7893")
    
    if total_rejections > 0 and total_rejections < 7893:
        print(f"🎉 NEW RECORD! Improved by {7893 - total_rejections} rejections!")
    elif total_rejections > 0:
        print(f"Result: {total_rejections} rejections (vs leaderboard best: 7893)")
    
    with open("complete_test_results.json", "w") as f:
        json.dump({
            "total_rejections": total_rejections,
            "scenarios": results,
            "timestamp": "2025-09-05T02:35:35Z"
        }, f, indent=2)
    
    print(f"\nDetailed results saved to complete_test_results.json")

if __name__ == "__main__":
    run_complete_test()
