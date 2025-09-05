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

    def _should_accept_scenario2(
        self,
        person_attributes: Dict[str, bool],
        constraints: List[Dict],
        current_counts: Dict[str, int],
        admitted_count: int,
    ) -> bool:
        """Specialized decision logic for scenario 2.

        Prioritizes creative and berlin_local attributes while ensuring we
        do not exceed the maximum number of non-locals that can be admitted
        (250 when 750 berlin locals are required). The method greedily accepts
        people who help satisfy still-missing constraints and rejects others.
        """

        needed = {c["attribute"]: c["minCount"] for c in constraints}

        is_local = person_attributes.get("berlin_local", False)
        is_creative = person_attributes.get("creative", False)
        is_techno = person_attributes.get("techno_lover", False)
        is_connected = person_attributes.get("well_connected", False)

        current_locals = current_counts.get("berlin_local", 0)
        current_creatives = current_counts.get("creative", 0)
        current_techno = current_counts.get("techno_lover", 0)
        current_connected = current_counts.get("well_connected", 0)

        max_non_local = 1000 - needed.get("berlin_local", 0)
        non_local_admitted = admitted_count - current_locals

        # Stage 1: we still need more creatives
        if current_creatives < needed.get("creative", 0):
            if is_creative and (is_local or non_local_admitted < max_non_local):
                return True
            return False

        # Stage 2: creative target met, now fill berlin locals
        if current_locals < needed.get("berlin_local", 0):
            if is_local:
                return True
            return False

        # Stage 3: satisfy remaining techno_lover and well_connected counts
        if current_techno < needed.get("techno_lover", 0) and is_techno:
            return True
        if current_connected < needed.get("well_connected", 0) and is_connected:
            return True

        # Once all constraints satisfied, accept everyone
        if all(current_counts[attr] >= need for attr, need in needed.items()):
            return True

        return False
    
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
            
            if scenario == 2:
                accept = self._should_accept_scenario2(
                    person_attributes, constraints, current_counts, admitted_count
                )
            else:
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
