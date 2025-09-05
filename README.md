# Berghain Bouncer Challenge Solution

This repository contains an optimal bouncer algorithm for the Berghain challenge from Listen Labs.

## Challenge Overview

You're the bouncer at a night club. Your goal is to fill the venue with N=1000 people while satisfying constraints like "at least 40% Berlin locals", or "at least 80% wearing all black". People arrive one by one, and you must immediately decide whether to let them in or turn them away. Your challenge is to fill the venue with as few rejections as possible while meeting all minimum requirements.

## Solution Strategy

The algorithm uses a dynamic acceptance probability calculation based on:

1. **Constraint Urgency**: How far behind we are on each constraint relative to expected future opportunities
2. **Attribute Correlations**: Bonus for people with positively correlated attributes
3. **Game Progress**: Dynamic thresholds that adapt based on how full the venue is
4. **Rare Attribute Prioritization**: Early selectivity for low-frequency attributes

## Scenarios

- **Scenario 1**: 2 constraints (young: 60%, well_dressed: 60%)
- **Scenario 2**: 4 constraints including challenging berlin_local requirement (75% needed, 39.8% frequency)
- **Scenario 3**: 6 constraints with very challenging german_speaker requirement (80% needed, 45.65% frequency)

## Usage

```bash
python main.py
```

## Results

Current leaderboard best: 7893 total rejections
Our algorithm: [To be updated after testing]

## Files

- `bouncer.py`: Core algorithm implementation
- `main.py`: Execution script for all scenarios
- `results.json`: Detailed performance results

## API Endpoints

- Create new game: `/new-game?scenario={1,2,3}&playerId=2be060b4-fac2-4e6e-b140-e9cf1b301f83`
- Make decision: `/decide-and-next?gameId={uuid}&personIndex={n}&accept={true/false}`

## Algorithm Details

The key insight is that this is a constrained optimization problem where we need to balance immediate decisions with future opportunities. The algorithm prioritizes rare attributes early (like creative at 6.2% frequency needing 300/1000 people) while using correlation data to identify high-value candidates who satisfy multiple constraints.

The most challenging scenario is #3 with the german_speaker constraint requiring 800/1000 people but only 45.65% frequency, combined with strong negative correlation with international (-0.717).
