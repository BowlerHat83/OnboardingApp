from typing import Dict, Any, Union

class BaseScorer:
    """
    Base utility class providing standardized primitive scoring functions.
    """

    @staticmethod
    def score_binary(condition: bool) -> float:
        """Returns 100.0 for True, 0.0 for False."""
        return 100.0 if condition else 0.0

    @staticmethod
    def score_ranged(value: float, best: float, worst: float) -> float:
        """
        Scales a numerical value linearly between best (100.0) and worst (0.0).
        Automatically handles cases where lower is better (e.g., latency) 
        or higher is better (e.g., word count).
        """
        if value is None:
            return 0.0

        if best < worst:  # Lower is better (e.g., LCP = 2.5s best, 4.0s worst)
            if value <= best:
                return 100.0
            if value >= worst:
                return 0.0
            return round(100.0 * (1.0 - (value - best) / (worst - best)), 2)
        else:  # Higher is better (e.g., Backlink Count)
            if value >= best:
                return 100.0
            if value <= worst:
                return 0.0
            return round(100.0 * ((value - worst) / (best - worst)), 2)

    @staticmethod
    def score_deductive(base: float, penalties: float, min_floor: float = 0.0) -> float:
        """Subtracts penalties from base score, capped at min_floor."""
        return max(min_floor, round(base - penalties, 2))

    @staticmethod
    def calculate_grade(score: float) -> str:
        """Maps a 0-100 score to a letter grade."""
        if score >= 95: return "A+"
        if score >= 90: return "A"
        if score >= 85: return "A-"
        if score >= 80: return "B+"
        if score >= 75: return "B"
        if score >= 70: return "B-"
        if score >= 65: return "C+"
        if score >= 60: return "C"
        if score >= 50: return "D"
        return "F"