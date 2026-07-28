def score_security(has_ssl: bool, https_enforced: bool) -> int:
    """
    Scores Section 1 (Technical Security).
    Each check is binary (Pass/Fail) and worth 50 points (Max 100).
    """
    score = 0
    if has_ssl:
        score += 50
    if https_enforced:
        score += 50

    return score
