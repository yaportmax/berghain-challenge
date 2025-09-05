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
        
        unmet_constraints = []
        for constraint in constraints:
            attr = constraint["attribute"]
            min_count = constraint["minCount"]
            current_count = current_counts.get(attr, 0)
            remaining_needed = max(0, min_count - current_count)
            if remaining_needed > 0:
                unmet_constraints.append((attr, remaining_needed))
        
        base_prob = 0.3
        
        helps_unmet = False
        for attr, remaining_needed in unmet_constraints:
            if person_attributes.get(attr, False):
                helps_unmet = True
                urgency_boost = min(0.5, (remaining_needed / remaining_capacity) * 3.5)
                base_prob += urgency_boost
        
        if not unmet_constraints:
            has_relevant_attr = any(person_attributes.get(constraint["attribute"], False) 
                                  for constraint in constraints)
            if has_relevant_attr:
                base_prob = 0.7
            else:
                base_prob = 0.6
        
        capacity_ratio = remaining_capacity / 1000.0
        if capacity_ratio > 0.3:
            base_prob *= 1.1
        elif capacity_ratio < 0.1 and unmet_constraints:
            base_prob *= 0.9
        
        return min(1.0, base_prob)
    
    def run_scenario_with_existing_game(self, game_id: str, scenario: int) -> Dict:
        """Run a complete game using an existing game ID"""
        print(f"Starting scenario {scenario} with existing game {game_id}...")
        
        result = self.make_decision(game_id, 0)
        if "constraints" not in result or "attributeStatistics" not in result:
            print(f"Initial result: {result}")
            if result.get("status") != "running":
                raise Exception(f"Game {game_id} is not in running state: {result.get('status')}")
        
        if scenario == 1:
            constraints = [
                {"attribute": "young", "minCount": 600},
                {"attribute": "well_dressed", "minCount": 600}
            ]
        elif scenario == 2:
            constraints = [
                {"attribute": "techno_lover", "minCount": 650},
                {"attribute": "well_connected", "minCount": 450},
                {"attribute": "creative", "minCount": 300},
                {"attribute": "berlin_local", "minCount": 750}
            ]
        elif scenario == 3:
            constraints = [
                {"attribute": "underground_veteran", "minCount": 500},
                {"attribute": "international", "minCount": 650},
                {"attribute": "fashion_dressed", "minCount": 550},
                {"attribute": "queer_friendly", "minCount": 250},
                {"attribute": "vinyl_collector", "minCount": 200},
                {"attribute": "german_speaker", "minCount": 800}
            ]
        
        if scenario == 1:
            attribute_stats = {
                "relativeFrequencies": {
                    "young": 0.502, "well_dressed": 0.601, "techno_lover": 0.651,
                    "well_connected": 0.451, "creative": 0.062, "berlin_local": 0.398,
                    "underground_veteran": 0.501, "international": 0.651, "fashion_dressed": 0.551,
                    "queer_friendly": 0.251, "vinyl_collector": 0.201, "german_speaker": 0.4565
                },
                "correlations": {}
            }
        elif scenario == 2:
            attribute_stats = {
                "relativeFrequencies": {
                    "young": 0.502, "well_dressed": 0.601, "techno_lover": 0.651,
                    "well_connected": 0.451, "creative": 0.062, "berlin_local": 0.398,
                    "underground_veteran": 0.501, "international": 0.651, "fashion_dressed": 0.551,
                    "queer_friendly": 0.251, "vinyl_collector": 0.201, "german_speaker": 0.4565
                },
                "correlations": {}
            }
        else:  # scenario == 3
            attribute_stats = {
                "relativeFrequencies": {
                    "young": 0.502, "well_dressed": 0.601, "techno_lover": 0.651,
                    "well_connected": 0.451, "creative": 0.062, "berlin_local": 0.398,
                    "underground_veteran": 0.501, "international": 0.651, "fashion_dressed": 0.551,
                    "queer_friendly": 0.251, "vinyl_collector": 0.201, "german_speaker": 0.4565
                },
                "correlations": {
                    "german_speaker": {"international": -0.717}
                }
            }
        
        print(f"Game ID: {game_id}")
        print(f"Constraints: {constraints}")

    def run_scenario(self, scenario: int) -> Dict:
        """Run a complete game for the specified scenario"""
        print(f"Starting scenario {scenario}...")
        
        try:
            game_data = self.create_game(scenario)
            game_id = game_data["gameId"]
            constraints = game_data["constraints"]
            attribute_stats = game_data["attributeStatistics"]
            
            print(f"Game ID: {game_id}")
            print(f"Constraints: {constraints}")
            
            result = self._run_game_loop(game_id, scenario, constraints, attribute_stats)
            
            if "status" not in result:
                result["status"] = "unknown"
            
            return result
            
        except Exception as e:
            print(f"Error in scenario {scenario}: {e}")
            return {
                "scenario": scenario,
                "status": "failed",
                "rejected_count": 0,
                "admitted_count": 0,
                "final_counts": {},
                "reason": str(e)
            }
    
    def _run_game_loop(self, game_id: str, scenario: int, constraints: List[Dict], attribute_stats: Dict) -> Dict:
        current_counts = {constraint["attribute"]: 0 for constraint in constraints}
        admitted_count = 0
        rejected_count = 0
        person_index = 0
        
        result = self.make_decision(game_id, person_index)
        print(f"Initial result: {result}")
        
        while result.get("status") == "running":
            person = result["nextPerson"]
            person_attributes = person["attributes"]
            current_person_index = person["personIndex"]
            
            accept_prob = self.calculate_acceptance_probability(
                person_attributes, constraints, attribute_stats, 
                current_counts, admitted_count
            )
            
            accept = accept_prob > 0.4
            
            if accept:
                admitted_count += 1
                for attr, has_attr in person_attributes.items():
                    if has_attr and attr in current_counts:
                        current_counts[attr] += 1
            else:
                rejected_count += 1
            
            try:
                result = self.make_decision(game_id, current_person_index, accept)
                
                if "error" in result:
                    print(f"API Error at person {current_person_index}: {result['error']}")
                    return {
                        "scenario": scenario,
                        "status": "failed",
                        "rejected_count": rejected_count,
                        "admitted_count": admitted_count,
                        "final_counts": current_counts,
                        "reason": result["error"]
                    }
                
                if "admittedCount" in result:
                    admitted_count = result["admittedCount"]
                if "rejectedCount" in result:
                    rejected_count = result["rejectedCount"]
                
                game_status = result.get("status", "running")
                if game_status != "running":
                    print(f"Game ended with status: {game_status}")
                    break
                    
                if current_person_index % 100 == 0:
                    print(f"Person {current_person_index}: Admitted {admitted_count}, Rejected {rejected_count}")
                    print(f"Constraint progress: {current_counts}")
                    
            except Exception as e:
                print(f"Error making decision for person {current_person_index}: {e}")
                print(f"Last result: {result}")
                return {
                    "scenario": scenario,
                    "status": "failed",
                    "rejected_count": rejected_count,
                    "admitted_count": admitted_count,
                    "final_counts": current_counts,
                    "reason": str(e)
                }
        
        final_status = result.get("status", "unknown")
        final_rejected_count = result.get("rejectedCount", rejected_count)
        
        print(f"Game completed with status: {final_status}")
        print(f"Final rejected count: {final_rejected_count}")
        
        return {
            "scenario": scenario,
            "status": final_status,
            "rejected_count": final_rejected_count,
            "admitted_count": admitted_count,
            "final_counts": current_counts
        }
