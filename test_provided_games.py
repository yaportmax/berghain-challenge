#!/usr/bin/env python3

from bouncer import BerghainBouncer
import json

def test_provided_games():
    bouncer = BerghainBouncer()
    
    provided_games = {
        1: "569d11ab-2fff-4b6a-bcaa-1911634476a0",  # Scenario 1
        1: "952043b1-4ce8-48d4-85e5-b3d2df1400a4",  # Another Scenario 1 game
    }
    
    print("=== Testing Provided Game IDs ===")
    
    for scenario, game_id in provided_games.items():
        print(f"\nTesting Scenario {scenario} with Game ID: {game_id}")
        
        try:
            result = bouncer.make_decision(game_id, 0)
            print(f"Initial API call successful: {result.get('status', 'no status')}")
            
            if result.get('status') == 'running':
                person = result.get('nextPerson', {})
                print(f"First person index: {person.get('personIndex', 'missing')}")
                print(f"First person attributes: {person.get('attributes', {})}")
                
                decision_result = bouncer.make_decision(game_id, 1, False)
                print(f"Decision result status: {decision_result.get('status', 'no status')}")
                print(f"Decision result keys: {list(decision_result.keys())}")
                
            else:
                print(f"Game not running: {result}")
                
        except Exception as e:
            print(f"Error testing game {game_id}: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_provided_games()
