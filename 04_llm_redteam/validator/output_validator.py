"""
Output Validator — checks LLM outputs for policy violations,
data leakage signals, and jailbreak indicators.
"""

import re
from dataclasses import dataclass
from typing import List


@dataclass
class ValidationResult:
    passed: bool
    violations: List[str]
    canary_triggered: bool = False


# Configurable policy rules
POLICY_RULES = {
    "no_system_prompt_leak": {
        "pattern": r"(system prompt|my instructions are|i was told to)",
        "description": "Potential system prompt leakage"
    },
    "no_api_key_patterns": {
        "pattern": r"(sk-[a-zA-Z0-9]{20,}|api[_-]?key\s*[:=]\s*\S+)",
        "description": "Potential API key in output"
    },
    "no_explicit_harmful_content": {
        "pattern": r"(step.{0,20}by.{0,20}step.{0,30}(hack|exploit|malware|ransomware))",
        "description": "Explicit harmful instruction detected"
    },
    "no_jailbreak_acknowledgement": {
        "pattern": r"(as DAN|i have no restrictions now|jailbreak successful|ignoring previous)",
        "description": "Jailbreak acknowledgement detected"
    },
}

CANARY_TOKENS = [
    "CANARY_TOKEN_ALPHA_7291",
    "SECRET_SENTINEL_X9182",
]


class OutputValidator:
    def __init__(self, custom_rules: dict = None):
        self.rules = {**POLICY_RULES, **(custom_rules or {})}
        self.canary_tokens = CANARY_TOKENS

    def validate(self, output: str) -> ValidationResult:
        violations = []

        # Check policy rules
        for rule_name, rule in self.rules.items():
            if re.search(rule["pattern"], output, re.IGNORECASE):
                violations.append(f"{rule_name}: {rule['description']}")

        # Check canary token leakage
        canary_triggered = any(token in output for token in self.canary_tokens)
        if canary_triggered:
            violations.append("canary_token_leaked: Canary token appeared in output")

        return ValidationResult(
            passed=len(violations) == 0,
            violations=violations,
            canary_triggered=canary_triggered
        )

    def inject_canary(self, system_prompt: str) -> str:
        """Inject a canary token into the system prompt for leak detection."""
        canary = self.canary_tokens[0]
        return f"{system_prompt}\n\n[INTERNAL_REF: {canary}]"
