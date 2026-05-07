"""
run_evaluation.py — evaluates the full defence pipeline against all attack templates.

Usage:
    python evaluation/run_evaluation.py --output results/
"""

import argparse
import json
from pathlib import Path
from collections import defaultdict

from classifier.model import InputClassifier
from validator.output_validator import OutputValidator


def load_templates(path: str = "attacks/attack_templates.json") -> list:
    with open(path) as f:
        data = json.load(f)
    return data["templates"]


def expand_template(template: dict) -> list:
    """Expand a template with all variable combinations."""
    text = template["template"]
    variables = template.get("variables", {})
    if not variables:
        return [text]

    expanded = [text]
    for var_name, values in variables.items():
        new_expanded = []
        for t in expanded:
            for val in values:
                new_expanded.append(t.replace("{" + var_name + "}", val))
        expanded = new_expanded
    return expanded


def run_evaluation(output_dir: str = "results/"):
    Path(output_dir).mkdir(exist_ok=True)

    classifier = InputClassifier()
    validator = OutputValidator()
    templates = load_templates()

    results = []
    category_stats = defaultdict(lambda: {"total": 0, "blocked_l1": 0, "bypassed": 0})

    print(f"Evaluating {len(templates)} attack templates...\n")

    for template in templates:
        category = template["category"]
        expected_defence = template["expected_defence"]
        attacks = expand_template(template)

        for attack_text in attacks:
            category_stats[category]["total"] += 1

            # Layer 1: Input classifier
            l1_result = classifier.predict(attack_text)
            if l1_result["is_injection"]:
                category_stats[category]["blocked_l1"] += 1
                results.append({
                    "template_id": template["id"],
                    "category": category,
                    "attack_text": attack_text[:100] + "...",
                    "blocked_by": "layer_1_classifier",
                    "bypassed": False
                })
            else:
                # Layer 2: Simulate output (in real eval, call LLM here)
                # For this demo, we flag unblocked injections as potential bypasses
                category_stats[category]["bypassed"] += 1
                results.append({
                    "template_id": template["id"],
                    "category": category,
                    "attack_text": attack_text[:100] + "...",
                    "blocked_by": None,
                    "bypassed": True
                })

    # Generate report
    total = sum(s["total"] for s in category_stats.values())
    total_blocked = sum(s["blocked_l1"] for s in category_stats.values())
    total_bypassed = sum(s["bypassed"] for s in category_stats.values())

    print(f"{'Category':<25} {'Total':>6} {'Blocked L1':>10} {'Bypassed':>10} {'Block Rate':>12}")
    print("-" * 65)
    for cat, stats in category_stats.items():
        rate = stats["blocked_l1"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"{cat:<25} {stats['total']:>6} {stats['blocked_l1']:>10} "
              f"{stats['bypassed']:>10} {rate:>11.1f}%")

    print("-" * 65)
    overall_rate = total_blocked / total * 100 if total > 0 else 0
    print(f"{'OVERALL':<25} {total:>6} {total_blocked:>10} {total_bypassed:>10} {overall_rate:>11.1f}%")

    # Save results
    with open(f"{output_dir}/raw_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_dir}/raw_results.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/")
    args = parser.parse_args()
    run_evaluation(args.output)
