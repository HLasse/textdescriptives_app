
from typing import List, Dict, Set

from spacy.cli.download import get_compatibility


def metrics_options() -> List[str]:
    return [
        "descriptive_stats",
        "readability",
        "dependency_distance",
        "pos_proportions",
        "coherence",
        "quality"
    ]


def language_options() -> Dict[str, str]:
    return {
        "English": "en",
        "Danish": "da",
        "Croatian": "hr"
    }


#################
# Model options #
#################


def all_model_size_options_pretty_to_short() -> Dict[str, str]:
    return {
        "Small": "sm",
        "Medium": "md",
        "Large": "lg",
        #"Transformer": "trf"  # Disabled for now
    }


def all_model_size_options_short_to_pretty() -> Dict[str, str]:
    return {
        short: pretty
        for pretty, short in all_model_size_options_pretty_to_short().items()
    }


def available_model_size_options(lang) -> List[str]:
    short_to_pretty = all_model_size_options_short_to_pretty()
    if lang == "all":
        return sorted(list(short_to_pretty.values()))
    return sorted([
        short_to_pretty[short]
        for short in ModelAvailabilityChecker.available_model_sizes_for_language(lang)
    ])


class ModelAvailabilityChecker():

    @staticmethod
    def available_models() -> List[str]:
        return list(get_compatibility().keys())

    @staticmethod
    def extract_language_and_size() -> List[List[str]]:
        # [["ca", "sm"], ["en", "lg"], ...]
        return list([
            list(map(m.split("_").__getitem__, [0, -1]))
            for m in ModelAvailabilityChecker.available_models()
        ])

    @staticmethod
    def model_is_available(lang: str, size: str) -> bool:
        lang_and_size = set([
            "_".join(lang_size)
            for lang_size in ModelAvailabilityChecker.extract_language_and_size()
        ])
        return f"{lang}_{size}" in lang_and_size

    @staticmethod
    def available_model_sizes_for_language(lang: str) -> Set[str]:
        return set([
            size
            for (lang_, size) in ModelAvailabilityChecker.extract_language_and_size()
            if lang_ == lang and size in all_model_size_options_pretty_to_short().values()
        ])
