#!/usr/bin/env python3

import requests
import json

def test_direct_api_call():
    base_url = "https://berghain.challenges.listenlabs.ai"
    
    game_ids = [
        "7PHYP_S1e2Y",  # Scenario 3: 0/1000, Stale 8m ago
        "9x0AuplPriU",  # Scenario 2: 0/1000, Stale 8m ago
        "p5Wr9bXfdrw"   # Scenario 1: 0/1000, Stale 8m ago
    ]
    
    for game_id in game_ids:
        print(f"\n=== Testing Game ID: {game_id} ===")
        
        url = f"{base_url}/decide-and-next"
        params = {"gameId": game_id, "personIndex": 0}
        
        try:
            response = requests.get(url, params=params)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
                print(f"Status: {data.get('status', 'MISSING')}")
                
                if data.get('status') == 'running':
                    print("✅ Game is running and ready!")
                    next_person = data.get('nextPerson', {})
                    print(f"Next person index: {next_person.get('personIndex', 'MISSING')}")
                    print(f"Attributes: {next_person.get('attributes', {})}")
                    
                    if 'constraints' in data:
                        print(f"Constraints: {data['constraints']}")
                    if 'attributeStatistics' in data:
                        print(f"Attribute stats keys: {list(data['attributeStatistics'].keys())}")
                else:
                    print(f"Game status: {data.get('status')}")
                    print(f"Full response: {json.dumps(data, indent=2)}")
            else:
                print(f"Error response: {response.text}")
                
        except Exception as e:
            print(f"Exception: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_direct_api_call()
