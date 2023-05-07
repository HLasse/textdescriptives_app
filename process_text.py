"""
The text processing functionality.
"""

from typing import List, Optional
import streamlit as st
import pandas as pd
import textdescriptives as td


@st.cache_data
def text_to_metrics(
    string: str,
    language_short: str,
    model_size_short: str,
    metrics: List[str],
    split_by_line: bool,
    filename: Optional[str],
) -> pd.DataFrame:
    # Clean and (optionally) split the text
    string = string.strip()
    if split_by_line:
        strings = string.split("\n")
    else:
        strings = [string]

    # Remove empty strings
    # E.g. due to consecutive newlines
    strings = [s for s in strings if s]

    # Will automatically download the relevant model and extract all metrics
    # TODO: Download beforehand to speed up inference
    df = td.extract_metrics(
        text=strings,
        lang=language_short,
        spacy_model_size=model_size_short,
        metrics=metrics,
    )

    # Add filename
    if filename is not None:
        df["File"] = filename
        move_column_inplace(df=df, col="File", pos=0)

    return df


def move_column_inplace(df: pd.DataFrame, col: str, pos: int) -> None:
    """
    Move a column to a given column-index position.

    Taken from the `utipy` package.

    Parameters
    ----------
    df : `pandas.DataFrame`.
    col : str
        Name of column to move.
    pos : int
        Column index to move `col` to.
    """
    assert (
        0 <= pos < len(df.columns)
    ), f"`pos` must be between 0 (incl.) and the number of columns -1. Was {pos}."
    col = df.pop(col)
    df.insert(pos, col.name, col)
