import requests
import json
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

    def _should_accept_scenario1(
        self,
        person_attributes: Dict[str, bool],
        constraints: List[Dict],
        current_counts: Dict[str, int],
        admitted_count: int,
        attribute_stats: Dict,
        encountered_counts: Dict[str, int],
        encountered_joint: int,
        encountered_total: int,
        optimism: float = 0.02,
    ) -> bool:
        """Adaptive acceptance rules for scenario 1.

        This version re-introduces an expectation-based component: we
        estimate future supply of each attribute from observed
        frequencies and admit single-attribute entrants when those
        projections indicate the remaining quota for the other attribute
        is likely attainable.  The heuristic is:

        * Always admit people who satisfy both attributes.
        * For single-attribute entrants, compare the remaining need for
          the opposite attribute against the number of expected future
          occurrences based on the running frequencies.  Admit if the
          forecast supply covers the deficit.
        * Once both minimum counts are met, admit everyone.

        The tracking arguments allow the caller to record statistics so
        strategies can be analysed post-game.
        """

        needed = {c["attribute"]: c["minCount"] for c in constraints}
        need_young = needed.get("young", 0) - current_counts.get("young", 0)
        need_well = needed.get("well_dressed", 0) - current_counts.get("well_dressed", 0)

        is_young = person_attributes.get("young", False)
        is_well = person_attributes.get("well_dressed", False)

        if need_young <= 0 and need_well <= 0:
            return True

        # Always admit entrants with both attributes while either quota
        # is still missing.
        if is_young and is_well:
            return True

        remaining_slots = 1000 - admitted_count
        if remaining_slots <= 0:
            return False

        # Estimate attribute frequencies from observed counts.  This retains
        # the empirical approach but we now combine it with a "balancing"
        # heuristic that favors whichever attribute is more urgently needed.
        freqs = attribute_stats.get("relativeFrequencies", {})

        if encountered_total > 0:
            # Apply a Beta(1,1) prior for smoother early estimates.
            freq_y = (encountered_counts.get("young", 0) + 1) / (encountered_total + 2)
            freq_w = (encountered_counts.get("well_dressed", 0) + 1) / (encountered_total + 2)
            freq_both = (encountered_joint + 1) / (encountered_total + 2)
        else:
            freq_y = freqs.get("young", 0.33)
            freq_w = freqs.get("well_dressed", 0.33)
            freq_both = min(freq_y, freq_w) * 0.8

        freq_y = min(1.0, freq_y + optimism)
        freq_w = min(1.0, freq_w + optimism)
        freq_both = min(1.0, freq_both + optimism)

        remaining_after = remaining_slots - 1
        freq_y_only = max(0.0, freq_y - freq_both)
        freq_w_only = max(0.0, freq_w - freq_both)
        exp_y_only = freq_y_only * remaining_after
        exp_w_only = freq_w_only * remaining_after
        exp_both = freq_both * remaining_after

        # Use joint-frequency projections. For single-attribute entrants,
        # ensure the expected future supply (including people with both
        # attributes) can still satisfy the outstanding quotas.
        if is_young and not is_well and need_young > 0:
            if need_young >= need_well:
                return True
            need_y_after = max(0, need_young - 1)
            exp_future_y = exp_y_only + exp_both
            exp_future_w = exp_w_only + exp_both
            return exp_future_w >= need_well and exp_future_y >= need_y_after

        if is_well and not is_young and need_well > 0:
            if need_well >= need_young:
                return True
            need_w_after = max(0, need_well - 1)
            exp_future_y = exp_y_only + exp_both
            exp_future_w = exp_w_only + exp_both
            return exp_future_y >= need_young and exp_future_w >= need_w_after

        # Entrants with no relevant attributes are rejected until all
        # requirements are satisfied.
        return False

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

    def run_scenario(self, scenario: int, optimism: float = 0.02) -> Dict:
        """Run a complete game for the specified scenario.

        The ``optimism`` parameter tweaks the acceptance heuristic for
        scenario 1, allowing automated sweeps over more aggressive or
        conservative strategies.
        """
        print(f"Starting scenario {scenario} with optimism {optimism}...")

        try:
            game_data = self.create_game(scenario)
            game_id = game_data["gameId"]
            constraints = game_data["constraints"]
            attribute_stats = game_data["attributeStatistics"]

            print(f"Game ID: {game_id}")
            print(f"Constraints: {constraints}")

            result = self._run_game_loop(
                game_id, scenario, constraints, attribute_stats, optimism
            )

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

    def run_scenario_until(
        self,
        scenario: int,
        target_rejections: int = 800,
        max_attempts: int = 20,
        optimism_start: float = 0.02,
        optimism_step: float = 0.05,
    ) -> Dict:
        """Repeatedly run a scenario, increasing optimism each attempt,
        until the rejected count drops below ``target_rejections`` or
        ``max_attempts`` is reached."""
        best_result = None
        last_result = None
        optimism = optimism_start
        for attempt in range(1, max_attempts + 1):
            print(f"Attempt {attempt} for scenario {scenario} (optimism={optimism:.2f})")
            result = self.run_scenario(scenario, optimism=optimism)
            last_result = result
            rejected = result.get("rejected_count", 9999)

            if result.get("status") == "completed":
                if best_result is None or rejected < best_result.get("rejected_count", 9999):
                    best_result = result

                if rejected < target_rejections:
                    print(f"Achieved target with {rejected} rejections on attempt {attempt}")
                    break

            print(f"Attempt {attempt} finished with {rejected} rejections")
            optimism += optimism_step

        return best_result if best_result is not None else last_result
    
    def _run_game_loop(
        self,
        game_id: str,
        scenario: int,
        constraints: List[Dict],
        attribute_stats: Dict,
        optimism: float = 0.02,
    ) -> Dict:
        current_counts = {constraint["attribute"]: 0 for constraint in constraints}
        encountered_counts = {constraint["attribute"]: 0 for constraint in constraints}
        encountered_joint = 0
        encountered_total = 0
        admitted_count = 0
        rejected_count = 0
        person_index = 0

        result = self.make_decision(game_id, person_index)
        print(f"Initial result: {result}")

        while result.get("status") == "running":
            person = result["nextPerson"]
            person_attributes = person["attributes"]
            current_person_index = person["personIndex"]

            if scenario == 1:
                accept = self._should_accept_scenario1(
                    person_attributes,
                    constraints,
                    current_counts,
                    admitted_count,
                    attribute_stats,
                    encountered_counts,
                    encountered_joint,
                    encountered_total,
                    optimism,
                )
            elif scenario == 2:
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

            encountered_total += 1
            for attr in encountered_counts:
                if person_attributes.get(attr, False):
                    encountered_counts[attr] += 1
            if scenario == 1 and person_attributes.get("young") and person_attributes.get("well_dressed"):
                encountered_joint += 1

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
                    if scenario == 1 and encountered_total > 0:
                        obs_y = encountered_counts["young"] / encountered_total
                        obs_w = encountered_counts["well_dressed"] / encountered_total
                        print(f"Observed frequencies: young={obs_y:.3f}, well_dressed={obs_w:.3f}")

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
        print(f"Total encountered: {encountered_total}")
        print(f"Encountered counts: {encountered_counts}")
        result_dict = {
            "scenario": scenario,
            "status": final_status,
            "rejected_count": final_rejected_count,
            "admitted_count": admitted_count,
            "final_counts": current_counts,
            "encountered_total": encountered_total,
            "encountered_counts": encountered_counts,
        }
        if scenario == 1:
            print(f"Encountered both young & well_dressed: {encountered_joint}")
            if encountered_total > 0:
                obs_y = encountered_counts.get("young", 0) / encountered_total
                obs_w = encountered_counts.get("well_dressed", 0) / encountered_total
                theoretical_min = int(max(600 / max(obs_y, 1e-9), 600 / max(obs_w, 1e-9)) - 1000)
                result_dict.update({
                    "encountered_joint": encountered_joint,
                    "observed_frequencies": {"young": obs_y, "well_dressed": obs_w},
                    "theoretical_min_rejections": theoretical_min,
                })
            else:
                result_dict["encountered_joint"] = encountered_joint

        return result_dict
