#!/usr/bin/env python3

import requests
import json

def test_running_games():
    base_url = "https://berghain.challenges.listenlabs.ai"
    
    running_games = {
        1: "Uv4xoUs2qcI",  # Scenario 1: 0/1000, Running 1m ago
        2: "j4CXN7VpuoA",  # Scenario 2: 0/1000, Running 56s ago
        3: "7PHYP_S1e2Y"   # Scenario 3: 0/1000, Stale 13m ago (but should still work)
    }
    
    for scenario, game_id in running_games.items():
        print(f"\n=== Testing Scenario {scenario} - Game ID: {game_id} ===")
        
        url = f"{base_url}/decide-and-next"
        params = {"gameId": game_id, "personIndex": 0}
        
        try:
            response = requests.get(url, params=params)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Game is accessible!")
                print(f"Status: {data.get('status', 'MISSING')}")
                print(f"Response keys: {list(data.keys())}")
                
                if data.get('status') == 'running':
                    next_person = data.get('nextPerson', {})
                    print(f"Next person index: {next_person.get('personIndex', 'MISSING')}")
                    print(f"Attributes: {list(next_person.get('attributes', {}).keys())}")
                    
                    print(f"\n--- Testing decision making ---")
                    decision_params = {"gameId": game_id, "personIndex": 1, "accept": "false"}
                    decision_response = requests.get(url, params=decision_params)
                    print(f"Decision Status Code: {decision_response.status_code}")
                    
                    if decision_response.status_code == 200:
                        decision_data = decision_response.json()
                        print(f"✅ Decision API works!")
                        print(f"Decision response keys: {list(decision_data.keys())}")
                        print(f"Status after decision: {decision_data.get('status', 'MISSING')}")
                    else:
                        print(f"❌ Decision failed: {decision_response.text}")
                else:
                    print(f"Game not running: {data}")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"Exception: {e}")
        
        print("-" * 60)

if __name__ == "__main__":
    test_running_games()
