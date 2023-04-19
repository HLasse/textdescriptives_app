
from typing import List, Dict


def language_options() -> Dict[str, str]:
    return {
        "English": "en",
        "Danish": "da",
    }


def model_size_options() -> Dict[str, str]:
    return {
        "Small": "sm",
        "Medium": "md",
        "Large": "lg",
        "Transformer": "trf"
    }


def metrics_options() -> List[str]:
    return [
        "descriptive_stats",
        "readability",
        "dependency_distance",
        "pos_stats",
        "coherence",
        "quality"
    ]
