#!/usr/bin/env python3

import requests
import json

def debug_api_flow():
    base_url = "https://berghain.challenges.listenlabs.ai"
    game_id = "952043b1-4ce8-48d4-85e5-b3d2df1400a4"  # Provided game ID
    
    print("=== Debugging API Flow ===")
    
    print("\n1. Getting first person...")
    url = f"{base_url}/decide-and-next"
    params = {"gameId": game_id, "personIndex": 0}
    
    response = requests.get(url, params=params)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get('status') == 'running':
        person = result['nextPerson']
        person_index = person['personIndex']
        print(f"Got person at index: {person_index}")
        
        print(f"\n2. Making decision for person {person_index} (reject)...")
        params = {"gameId": game_id, "personIndex": person_index, "accept": "false"}
        
        response = requests.get(url, params=params)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get('status') == 'running':
            next_person = result['nextPerson']
            next_person_index = next_person['personIndex']
            print(f"Next person index: {next_person_index}")
            
            print(f"\n3. Making decision for person {next_person_index} (accept)...")
            params = {"gameId": game_id, "personIndex": next_person_index, "accept": "true"}
            
            response = requests.get(url, params=params)
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Game not running after first decision: {result}")
    else:
        print(f"Game not running initially: {result}")

if __name__ == "__main__":
    debug_api_flow()
