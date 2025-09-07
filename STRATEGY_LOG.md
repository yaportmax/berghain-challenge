# Scenario 1 Strategy Attempts

This document records the evolving strategies and outcomes while trying to minimise rejections below 800 in scenario 1.

## Deterministic quota check
- **Description:** Accept both attributes immediately. For single-attribute entrants, admit only if enough slots remain to satisfy the other quota in the worst case.
- **Result:** Typical games ended with ~920 rejections.
- **Notes:** Guaranteeing quotas is safe but overly conservative when the distribution of attributes is favourable.

## Frequency-based expectation
- **Description:** Track observed frequencies of `young` and `well_dressed` and estimate future supply. Admit single-attribute entrants when expected remaining occurrences of the opposite attribute cover its remaining deficit.
- **Result:** Further testing required; early runs showed rejection counts around 900–950 depending on observed frequencies.
- **Notes:** Allows more optimistic admissions, potentially reducing rejections when attribute frequencies exceed one third.

### Attempt with expected-supply heuristic
- **Outcome:** First automated run encountered 3,394 entrants and finished with 2,394 rejections.
- **Observation:** The heuristic rejected too many single-attribute entrants early, leading to excessive total entrants before quotas were met.
- **Next steps:** Incorporate joint probability of attributes to better estimate overlapping supply and avoid over-rejecting.

## Bayesian optimistic frequencies
- **Description:** Use a Beta prior with an upper confidence bound when estimating attribute frequencies. This keeps early estimates optimistic, encouraging admission of single-attribute entrants when future supply might still satisfy the other quota.
- **Result:** Initial run completed with 2,780 rejections.
- **Notes:** The optimistic frequencies reduce early rejections but still rely on favourable distributions to reach the sub-800 target.

## Empirical frequency heuristic with optimism
- **Description:** Reverted to the earlier expectation-based approach using only observed attribute frequencies.
  Added a small +0.02 optimism factor to each frequency to lean toward accepting single-attribute entrants when supply may be ample.
- **Result:** Pending further testing; baseline run after the tweak finished with ~920 rejections.
- **Notes:** Serves as the new baseline for additional tweaks aimed at pushing below 900 and ultimately under 800 rejections.

## Joint-frequency heuristic with optimism sweep
- **Description:** Tracks joint `young & well_dressed` occurrences and feeds them into the acceptance heuristic.
  Introduced a tunable optimism parameter and a runner that increases optimism on successive attempts to explore more aggressive strategies.
- **Result:** Sweep across optimism values (0.02→0.5) produced a best run with 933 rejections; sub-800 still unachieved.
- **Notes:** More data is needed to determine whether higher optimism or alternative heuristics can exploit favourable attribute distributions.

## Balance-aware frequency heuristic
- **Description:** Combines observed-frequency projections with a balancing rule
  that admits single-attribute entrants only when their required quota is at
  least as urgent as the opposite attribute. This aims to keep young and
  well_dressed counts aligned while still using optimistic frequency estimates
  to accept extra entrants when future supply appears sufficient.
- **Result:** Initial tests after the update still hovered around ~920
  rejections; no sub-800 run has been observed yet.
- **Notes:** Further optimisation or more favourable attribute distributions may
  be necessary to push below 800.

## Joint-frequency supply forecast
- **Description:** Extended the scenario 1 helper to estimate future young-only,
  well_dressed-only, and joint entrants separately. Single-attribute entrants
  are now admitted only when these projections indicate the remaining mix can
  still satisfy both quotas.
- **Result:** Sweeping optimism values showed a minimum of **921** rejections at
  optimism=0.8; higher optimism eventually increased rejections as the missing
  attribute became scarce.
- **Notes:** Joint projections reduce rejections versus previous heuristics but
  runs remain above the sub-800 target, suggesting that the observed ~31%
  young frequency leaves little room for further gains without exceptionally
  favourable draws.

## Beta-smoothed joint forecast with theoretical floor
- **Description:** Apply a Beta(1,1) prior when estimating attribute
  frequencies and continue to project joint/solo supply. After each game,
  compute the observed attribute frequencies and the theoretical minimum
  rejections implied by those frequencies.
- **Result:** A run at optimism=0.05 required 2,361 entrants and rejected
  1,361 people. Observed frequencies were ~32.2% young and ~31.6%
  well_dressed, yielding a theoretical minimum of about 901 rejections.
- **Notes:** The theoretical floor still exceeded the sub-800 goal, implying
  that substantially higher attribute supply is necessary to reach the target.
