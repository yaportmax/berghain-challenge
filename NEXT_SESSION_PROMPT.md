# Berghain Bouncer Algorithm Optimization - Continue from Previous Session

## Context
You're continuing work on the Berghain challenge (https://berghain.challenges.listenlabs.ai/) to optimize a bouncer algorithm that minimizes rejections while meeting venue constraints.

## Current Status
- Successfully implemented a working bouncer algorithm in `bouncer.py`
- Algorithm can successfully run games and make decisions via the API
- **Problem identified**: Algorithm is too aggressive in rejecting people after meeting one constraint
- **Test result**: Scenario 1 had ~1766+ rejections (target: under 800)
- **Issue**: After reaching 600 young people, algorithm started rejecting everyone, even though it still needed well_dressed people (only had 592/600)

## API Details
- Player ID: `2be060b4-fac2-4e6e-b140-e9cf1b301f83`
- Base URL: `https://berghain.challenges.listenlabs.ai`
- Available game IDs for testing: `569d11ab-2fff-4b6a-bcaa-1911634476a0`, `952043b1-4ce8-48d4-85e5-b3d2df1400a4`
- Current leaderboard best: 7893 total rejections across all 3 scenarios
- User's leaderboard name: "Max Y"
- User's email: yaportmax@gmail.com

## Scenario Constraints
- **Scenario 1**: young (600/1000), well_dressed (600/1000)
- **Scenario 2**: techno_lover (650), well_connected (450), creative (300), berlin_local (750)  
- **Scenario 3**: underground_veteran (500), international (650), fashion_forward (550), queer_friendly (250), vinyl_collector (200), german_speaker (800)

## Key Issues to Fix
1. **Constraint Logic**: Algorithm stops accepting people after meeting one constraint, even when other constraints are unmet
2. **Acceptance Probability**: Current logic in `calculate_acceptance_probability()` is too conservative
3. **Threshold Logic**: Need better balance between meeting constraints and minimizing rejections
4. **Early Termination**: Algorithm incorrectly stops accepting when it should continue for unmet constraints

## Test Results from Previous Session
```
Person 1800: Admitted 921, Rejected 880
Constraint progress: {'young': 600, 'well_dressed': 578}
Person 1900: Admitted 935, Rejected 966
Constraint progress: {'young': 602, 'well_dressed': 592}
Person 2000: Admitted 935, Rejected 1066
Constraint progress: {'young': 602, 'well_dressed': 592}
```
The algorithm stopped accepting at 935 people (65 short of 1000) and kept rejecting even though well_dressed was only at 592/600.

## Next Steps
1. **Fix the acceptance logic** to continue accepting people who help with unmet constraints
2. **Improve the probability calculation** to be less aggressive about rejecting
3. **Add logic to fill remaining capacity** when close to 1000 people
4. **Test specifically on scenario 1** until rejections are under 800
5. **Then optimize scenarios 2 and 3**
6. **Run rate-limited** (one game at a time) to avoid API limits

## Files to Focus On
- `bouncer.py` - Main algorithm (needs optimization in `calculate_acceptance_probability` method)
- `final_test.py` - Test runner (working)
- `main.py` - Alternative test runner

## Specific Algorithm Changes Needed
1. In `calculate_acceptance_probability()`:
   - Don't return 0.1 for people who don't help with constraints if venue isn't full
   - Continue accepting people who help with ANY unmet constraint
   - Add logic to accept people when close to capacity (e.g., when admitted_count > 900)

2. Add better end-game logic:
   - When admitted_count > 900, be more aggressive about accepting
   - When any constraint is unmet and capacity remains, prioritize those constraints

## Repository Status
- Branch: `devin/1757038291-berghain-bouncer-algorithm`
- All test files and algorithm implementation are ready
- Previous session successfully ran API calls and identified the core issue

## Goal
Get scenario 1 under 800 rejections, then optimize all scenarios for minimum total rejections to beat the current leaderboard best of 7893.

## Rate Limiting Note
To avoid API rate limits, run only one game/scenario at a time. The user has access to existing blank games that can be reused instead of creating new ones.
