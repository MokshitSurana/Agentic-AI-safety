"""Prospective paired statistics; no model calls or outcome-dependent selection."""
import math
import random


def wilson(successes, total):
    if not 0 <= successes <= total:
        raise ValueError("Invalid counts")
    if total == 0:
        return None
    z = 1.959963984540054
    p = successes / total
    denom = 1 + z*z/total
    center = (p + z*z/(2*total)) / denom
    half = z * math.sqrt(p*(1-p)/total + z*z/(4*total*total)) / denom
    return [max(0.0, center-half), min(1.0, center+half)]


def paired(generic, explicit):
    """One binary observation per distinct workflow, matched externally."""
    if len(generic) != len(explicit) or any(x not in (0, 1) for x in [*generic, *explicit]):
        raise ValueError("Matched binary inputs required")
    n = len(generic)
    if not n:
        return {"pairs": 0, "risk_difference": None, "bootstrap_95pct": None, "mcnemar_exact_p": None}
    b = sum(g == 1 and e == 0 for g, e in zip(generic, explicit))
    c = sum(g == 0 and e == 1 for g, e in zip(generic, explicit))
    discordant = b+c
    p = min(1.0, 2 * sum(math.comb(discordant, k) for k in range(min(b, c)+1)) / 2**discordant)
    delta = [e-g for g, e in zip(generic, explicit)]
    rng = random.Random(0)
    draws = sorted(sum(rng.choices(delta, k=n))/n for _ in range(10000))
    return {"pairs": n, "generic_only": b, "explicit_only": c,
            "risk_difference": sum(delta)/n, "bootstrap_95pct": [draws[249], draws[9749]],
            "constant_differences": len(set(delta)) == 1,
            "mcnemar_exact_p": p,
            "caution": "Shared wording families limit workflow-independence assumptions; constant bootstrap intervals do not establish generalization."}


def holm(pvalues):
    if any(not 0 <= p <= 1 for p in pvalues):
        raise ValueError("Invalid p-values")
    result = [None]*len(pvalues)
    previous = 0.0
    for rank, index in enumerate(sorted(range(len(pvalues)), key=pvalues.__getitem__)):
        previous = max(previous, min(1.0, (len(pvalues)-rank)*pvalues[index]))
        result[index] = previous
    return result
