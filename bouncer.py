import requests
import json
import math
from typing import Dict, List, Optional, Tuple

class BerghainBouncer:
    def __init__(self, base_url: str = "https://berghain.challenges.listenlabs.ai"):
        self.base_url = base_url
        self.player_id = "2be060b4-fac2-4e6e-b140-e9cf1b301f83"
        
    def create_game(self, scenario: int) -> Dict:
        """Create a new game for the specified scenario"""
        url = f"{self.base_url}/new-game"
        params = {"scenario": scenario, "playerId": self.player_id}
        response = requests.get(url, params=params)
        result = response.json()
        
        if result.get("rateLimited"):
            raise Exception(f"Rate limited: {result.get('error', 'Unknown rate limit error')}")
        
        return result
    
    def make_decision(self, game_id: str, person_index: int, accept: Optional[bool] = None) -> Dict:
        """Make a decision for the current person"""
        url = f"{self.base_url}/decide-and-next"
        params = {"gameId": game_id, "personIndex": person_index}
        if accept is not None:
            params["accept"] = str(accept).lower()
        response = requests.get(url, params=params)
        result = response.json()
        
        if result.get("rateLimited"):
            raise Exception(f"Rate limited: {result.get('error', 'Unknown rate limit error')}")
        
        return result
    
    def calculate_acceptance_probability(self, person_attributes: Dict[str, bool], 
                                       constraints: List[Dict], 
                                       attribute_stats: Dict,
                                       current_counts: Dict[str, int],
                                       admitted_count: int) -> float:
        """Calculate the probability of accepting this person based on constraints and statistics"""
        remaining_capacity = 1000 - admitted_count
        if remaining_capacity <= 0:
            return 0.0
            
        correlations = attribute_stats.get("correlations", {})
        frequencies = attribute_stats["relativeFrequencies"]
        
        total_value = 0.0
        constraint_satisfaction = 0.0
        
        for constraint in constraints:
            attr = constraint["attribute"]
            min_count = constraint["minCount"]
            current_count = current_counts.get(attr, 0)
            remaining_needed = max(0, min_count - current_count)
            
            if person_attributes.get(attr, False):
                constraint_satisfaction += 1
                
                if remaining_needed > 0:
                    attr_frequency = frequencies[attr]
                    expected_future_with_attr = remaining_capacity * attr_frequency
                    
                    urgency = remaining_needed / max(1, expected_future_with_attr)
                    
                    correlation_bonus = 0.0
                    for other_attr, has_other in person_attributes.items():
                        if has_other and other_attr != attr and other_attr in correlations.get(attr, {}):
                            correlation_value = correlations[attr][other_attr]
                            if correlation_value > 0:
                                correlation_bonus += correlation_value * 0.1
                    
                    total_value += urgency * (1 + correlation_bonus)
        
        progress_ratio = admitted_count / 1000.0
        if progress_ratio < 0.3:
            threshold_modifier = 0.8
        elif progress_ratio < 0.7:
            threshold_modifier = 1.0
        else:
            threshold_modifier = 1.2
            
        if constraint_satisfaction > 0:
            return min(1.0, (total_value / constraint_satisfaction) * threshold_modifier)
        else:
            return 0.1
    
    def run_scenario(self, scenario: int) -> Dict:
        """Run a complete game for the specified scenario"""
        print(f"Starting scenario {scenario}...")
        
        game_data = self.create_game(scenario)
        game_id = game_data["gameId"]
        constraints = game_data["constraints"]
        attribute_stats = game_data["attributeStatistics"]
        
        print(f"Game ID: {game_id}")
        print(f"Constraints: {constraints}")
        
        current_counts = {constraint["attribute"]: 0 for constraint in constraints}
        admitted_count = 0
        rejected_count = 0
        person_index = 0
        
        result = self.make_decision(game_id, person_index)
        print(f"Initial result: {result}")
        
        while result.get("status") == "running":
            person = result["nextPerson"]
            person_attributes = person["attributes"]
            
            accept_prob = self.calculate_acceptance_probability(
                person_attributes, constraints, attribute_stats, 
                current_counts, admitted_count
            )
            
            accept = accept_prob > 0.5
            
            if accept:
                admitted_count += 1
                for attr, has_attr in person_attributes.items():
                    if has_attr and attr in current_counts:
                        current_counts[attr] += 1
            else:
                rejected_count += 1
            
            person_index += 1
            try:
                result = self.make_decision(game_id, person_index, accept)
                print(f"Decision {person_index}: accept={accept}, result_status={result.get('status', 'MISSING')}")
            except Exception as e:
                print(f"Error making decision for person {person_index}: {e}")
                print(f"Last result: {result}")
                raise
            
            if person_index % 100 == 0:
                print(f"Person {person_index}: Admitted {admitted_count}, Rejected {rejected_count}")
                print(f"Constraint progress: {current_counts}")
        
        final_status = result.get("status", "unknown")
        final_rejected_count = result.get("rejectedCount", rejected_count)
        
        print(f"Game completed with status: {final_status}")
        print(f"Final rejected count: {final_rejected_count}")
        print(f"Final result keys: {list(result.keys())}")
        
        return {
            "scenario": scenario,
            "status": final_status,
            "rejected_count": final_rejected_count,
            "admitted_count": admitted_count,
            "final_counts": current_counts
        }
