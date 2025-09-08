#!/usr/bin/env python3
"""
Analyze the iterative optimization results.
"""

import json

def analyze_results():
    with open('iterative_optimization_results.json', 'r') as f:
        data = json.load(f)

    print('=== ITERATIVE OPTIMIZATION RESULTS ANALYSIS ===')
    print(f'Strategy: {data["strategy"]}')
    print(f'Total iterations: {data["total_iterations"]}')
    print()

    results = data['results']
    print('Results by focus trait:')
    for r in results:
        print(f'  {r["focus_trait"]}: {r["rejected_count"]} rejections, {r["admitted_count"]} admitted')
        
    print()
    best_result = min(results, key=lambda x: x['rejected_count'])
    print(f'Best result: {best_result["rejected_count"]} rejections (focus: {best_result["focus_trait"]})')
    avg_rejections = sum(r['rejected_count'] for r in results) / len(results)
    print(f'Average rejections: {avg_rejections:.1f}')

    print()
    print('Fashion_dressed counts (checking for API issue):')
    for r in results:
        print(f'  {r["focus_trait"]}: {r["final_counts"]["fashion_dressed"]}')
        
    print()
    print('Constraint achievement analysis:')
    constraints = data['constraints']
    for trait, target in constraints.items():
        print(f'\n{trait} (target: {target}):')
        for r in results:
            count = r['final_counts'][trait]
            percentage = (count / target) * 100
            print(f'  {r["focus_trait"]}: {count}/{target} ({percentage:.1f}%)')

if __name__ == "__main__":
    analyze_results()
