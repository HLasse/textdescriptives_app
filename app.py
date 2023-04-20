"""
Dashboard for showcasing extraction of text metrics with textdescriptives.

"""

from io import StringIO

import numpy as np
import streamlit as st
import textdescriptives as td

from data_viewer import DataViewer
from options import (
    all_model_size_options_pretty_to_short,
    available_model_size_options,
    language_options,
    metrics_options,
)

################
# Introduction #
################


col1, col2 = st.columns([9, 2])
with col1:
    st.title("Extract Text Statistics")
with col2:
    st.image(
        "https://github.com/HLasse/TextDescriptives/raw/main/docs/_static/icon.png",
        width=125
    )

st.write(
    "Calculate a large variety of statistics from text via the "
    "[**TextDescriptives**](https://github.com/HLasse/TextDescriptives) python package "
    f"(v/{td.__version__}) and download the results as a .csv file. "
    "Includes descriptive statistics and metrics related to readability, "
    "information theory, text coherence and text quality."
)

st.write(
    "The source code for this application can be found on [**GitHub**](https://github.com/HLasse/TextDescriptives_app). "
    "If you have feedback, please open an [issue](https://github.com/HLasse/textdescriptives_app/issues)."
)

st.caption(
    "Hansen, L., Olsen, L. R., & Enevoldsen, K. (2023). TextDescriptives: A Python package for "
    "calculating a large variety of statistics from text. "
    "[arXiv preprint arXiv:2301.02057](https://arxiv.org/abs/2301.02057)"
)


############
# Settings #
############


input_choice = st.radio(
    label="Input", options=["Enter text", "Upload file"], index=0, horizontal=True
)

with st.form(key="settings_form"):
    split_by_line = st.checkbox(label="Split by newline", value=True)

    string_data = None

    if input_choice == "Upload file":
        uploaded_file = st.file_uploader(
            label="Choose a .txt file", type=["txt"], accept_multiple_files=False
        )

        if uploaded_file is not None:
            # To convert to a string based IO:
            string_data = StringIO(uploaded_file.getvalue().decode("utf-8")).read()

    else:
        default_text = """Hello, morning dew. The grass whispers low.
I'm here to dance. The gentle breeze does show.
Good morning, world. The birds sing in delight.
Let's spread our wings. The butterflies take flight.
Nature's chorus sings, a symphony of light."""

        string_data = st.text_area(
            label="Enter text", value=default_text, height=145, max_chars=None
        )

    # Row of selectors
    col1, col2 = st.columns([1, 1])

    with col1:
        # Selection of language
        language_pretty = st.selectbox(
            label="Language",
            options=list(language_options().keys()),
            index=5,
            key="language_selector",
        )

        language_short = language_options()[language_pretty]

    with col2:
        # Selection of model size
        model_size_pretty = st.selectbox(
            label="Model Size",
            options=available_model_size_options(lang="all"),
            index=0,
            key="size_selector",
        )

        model_size_short = all_model_size_options_pretty_to_short()[model_size_pretty]

    # Multiselection of metrics
    metrics = st.multiselect(
        label="Metrics", options=metrics_options(), default=metrics_options()
    )

    st.write(
        "See the [**documentation**](https://hlasse.github.io/TextDescriptives/) for "
        "information on the available metrics."
    )

    # This shouldn't happen but better safe than sorry
    if isinstance(metrics, list) and not metrics:
        metrics = None

    apply_settings_button = st.form_submit_button(label="Apply")


#############
# Apply NLP #
#############


if apply_settings_button and string_data is not None and string_data:
    if model_size_pretty not in available_model_size_options(lang=language_short):
        st.write(
            "**Sorry!** The chosen *model size* is not available in this language. Please try another."
        )
    else:
        # Clean and (optionally) split the text
        string_data = string_data.strip()
        if split_by_line:
            string_data = string_data.split("\n")
        else:
            string_data = [string_data]

        # Remove empty strings
        # E.g. due to consecutive newlines
        string_data = [s for s in string_data if s]

        # Will automatically download the relevant model and extract all metrics
        # TODO: Download beforehand to speed up inference
        df = td.extract_metrics(
            text=string_data,
            lang=language_short,
            spacy_model_size=model_size_short,
            metrics=metrics,
        )

        ###################
        # Present Results #
        ###################

        # Create 2 columns with 1) the output header
        # and 2) a download button
        DataViewer()._header_and_download(
            header="The calculated metrics", data=df, file_name="text_metrics.csv"
        )

        st.write("**Note**: This data frame has been transposed for readability.")
        df = df.transpose().reset_index()
        df.columns = ["Metric"] + [str(c) for c in list(df.columns)[1:]]
        st.dataframe(data=df, use_container_width=True)


############################
# Code For Reproducibility #
############################


with st.expander("See python code"):
    st.code(
        """
import textdescriptives as td

# Given a string of text and the settings
text = "..."
language = "..."
model_size = "..."
metrics = [...]
split_by_newline = True

# Remove whitespace from both ends of the string
text = text.strip()

# When asked, split by newlines
if split_by_newline:
    lines = text.split("\\n")
else:
    lines = [text]

# Remove empty lines
# E.g. due to consecutive newlines
lines = [l for l in lines if l]

# Extract metrics for each line
extracted_metrics = td.extract_metrics(
    text=lines,
    lang=language,
    spacy_model_size=model_size,
    metrics=metrics
)

""",
        language="python",
    )
