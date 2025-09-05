#!/usr/bin/env python3

import requests
import json

def test_existing_game(game_id):
    base_url = "https://berghain.challenges.listenlabs.ai"
    
    print(f"Testing game ID: {game_id}")
    
    url = f"{base_url}/decide-and-next"
    params = {"gameId": game_id, "personIndex": 0}
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("-" * 50)

game_ids = [
    "p5Wr9bXfdrw",  # Scenario 1
    "9x0AuplPriU",  # Scenario 2  
    "7PHYP_S1e2Y"   # Scenario 3
]

for game_id in game_ids:
    test_existing_game(game_id)
