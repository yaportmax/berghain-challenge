#!/usr/bin/env python3

import requests
import json

def test_new_game_creation():
    base_url = "https://berghain.challenges.listenlabs.ai"
    player_id = "2be060b4-fac2-4e6e-b140-e9cf1b301f83"
    
    print("=== Testing New Game Creation ===")
    
    url = f"{base_url}/new-game"
    params = {"scenario": 1, "playerId": player_id}
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            if 'gameId' in data:
                game_id = data['gameId']
                print(f"✅ New Game ID: {game_id}")
                print(f"Game ID type: {type(game_id)}")
                print(f"Game ID length: {len(game_id)}")
                
                print(f"\n=== Testing with new game ID ===")
                decide_url = f"{base_url}/decide-and-next"
                decide_params = {"gameId": game_id, "personIndex": 0}
                
                decide_response = requests.get(decide_url, params=decide_params)
                print(f"Decide API Status Code: {decide_response.status_code}")
                
                if decide_response.status_code == 200:
                    decide_data = decide_response.json()
                    print(f"✅ Decide API works! Status: {decide_data.get('status')}")
                    print(f"Response keys: {list(decide_data.keys())}")
                else:
                    print(f"❌ Decide API failed: {decide_response.text}")
            else:
                print(f"❌ No gameId in response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Failed to create game: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_new_game_creation()
