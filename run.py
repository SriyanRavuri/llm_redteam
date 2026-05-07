"""
Quickstart runner. Trains the input classifier (if not yet trained) and runs
the full attack-template evaluation. Equivalent to:

    python classifier/model.py
    python evaluation/run_evaluation.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from classifier.model import train_classifier  # noqa: E402
from evaluation.run_evaluation import run_evaluation  # noqa: E402


def main() -> None:
    print("Step 1 — training input classifier")
    train_classifier()
    print("\nStep 2 — running full attack-template evaluation")
    run_evaluation(output_dir=str(PROJECT_ROOT / "results"))


if __name__ == "__main__":
    main()
