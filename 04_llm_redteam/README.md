# LLM Red-Teaming & Prompt Injection Defence Framework

A small defence-in-depth pipeline for LLM-powered applications, evaluated
against a library of attack templates spanning five categories.

## Architecture

```
User Input
    │
    ▼
Layer 1: Input Classifier   ← TF-IDF + logistic regression
    │ (clean inputs only)
    ▼
LLM Application             ← (placeholder in this project — bring your own LLM)
    │
    ▼
Layer 2: Output Validator   ← Regex policy rules + canary token check
    │
    ▼
Safe Response
```

The runnable pipeline implements Layers 1 and 2. Layer 3 (canary tokens) is
exposed as a helper on the validator.

## Attack categories

| Category | Examples |
|----------|----------|
| Direct injection | "Ignore previous instructions and..." |
| Indirect injection | Hidden instructions in retrieved documents |
| Payload smuggling | Base64, zero-width-char token splitting |
| Context manipulation | Role confusion, persona hijacking |
| Jailbreak | DAN, hypothetical framing, fictional framing |

Templates live in `attacks/attack_templates.json` and are expanded by the
evaluator with all variable combinations.

## Project layout

```
04_llm_redteam/
├── attacks/
│   └── attack_templates.json
├── classifier/
│   ├── model.py                  # TF-IDF + LR injection classifier
│   └── injection_classifier.pkl  # generated after first run
├── validator/
│   └── output_validator.py       # Policy rules + canary tokens
├── evaluation/
│   └── run_evaluation.py         # Full pipeline evaluation
├── results/                      # raw_results.json, etc.
├── run.py                        # Quickstart: train + evaluate
├── requirements.txt
└── README.md
```

## Setup

```bash
cd 04_llm_redteam

python -m venv .venv
source .venv/bin/activate              # Linux / macOS
# .venv\Scripts\Activate.ps1            # Windows PowerShell

pip install -r requirements.txt
```

No API key is required. The classifier is pure scikit-learn.

## Run it

```bash
# One-shot: train the classifier + run the full attack-template evaluation
python run.py
```

You'll see a per-category block-rate table and a summary, e.g.

```
Category                   Total Blocked L1   Bypassed   Block Rate
-----------------------------------------------------------------
direct_injection               8          8          0       100.0%
indirect_injection             4          4          0       100.0%
payload_smuggling              4          3          1        75.0%
...
OVERALL                       24         23          1        95.8%
```

Per-attack results are written to `results/raw_results.json`.

To run the steps individually:

```bash
python classifier/model.py             # Train + save classifier
python evaluation/run_evaluation.py    # Run full evaluation
```

## Extend it

- Add new attack templates to `attacks/attack_templates.json`
- Tighten the classifier by expanding `INJECTION_EXAMPLES` /
  `BENIGN_EXAMPLES` in `classifier/model.py`
- Add new policy rules to `POLICY_RULES` in `validator/output_validator.py`
