"""
Dashboard for showcasing extraction of text metrics with textdescriptives.

"""

from io import StringIO

import pandas as pd
import streamlit as st
import textdescriptives as td

from data_viewer import DataViewer
from process_text import text_to_metrics
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
        width=125,
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
    "calculating a large variety of metrics from text. [Journal of Open Source Software, 8(84), "
    "5153, https://doi.org/10.21105/joss.05153](https://doi.org/10.21105/joss.05153)"
)


############
# Settings #
############


input_choice = st.radio(
    label="Input", options=["Enter text", "Upload file(s)"], index=0, horizontal=True
)

with st.form(key="settings_form"):
    split_by_line = st.checkbox(label="Split by newline", value=True)

    file_name_to_text_string = {}

    if input_choice == "Upload file(s)":
        uploaded_files = st.file_uploader(
            label="Choose a .txt file", type=["txt"], accept_multiple_files=True
        )

        if uploaded_files is not None and len(uploaded_files) > 0:
            # To convert to a string based IO:
            file_name_to_text_string = {
                file.name: StringIO(file.getvalue().decode("utf-8")).read()
                for file in uploaded_files
            }

    else:
        default_text = """Hello, morning dew. The grass whispers low.
I'm here to dance. The gentle breeze does show.
Good morning, world. The birds sing in delight.
Let's spread our wings. The butterflies take flight.
Nature's chorus sings, a symphony of light."""

        file_name_to_text_string = {
            "input": st.text_area(
                label="Enter text", value=default_text, height=145, max_chars=None
            )
        }

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


if apply_settings_button and len(file_name_to_text_string) > 0:
    if model_size_pretty not in available_model_size_options(lang=language_short):
        st.write(
            "**Sorry!** The chosen *model size* is not available in this language. Please try another."
        )
    else:
        # Extract metrics for each text
        output_df = pd.concat(
            [
                text_to_metrics(
                    string=string,
                    language_short=language_short,
                    model_size_short=model_size_short,
                    metrics=metrics,
                    split_by_line=split_by_line,
                    filename=filename if "Upload" in input_choice else None,
                )
                for filename, string in file_name_to_text_string.items()
            ],
            ignore_index=True,
        )

        ###################
        # Present Results #
        ###################

        # Create 2 columns with 1) the output header
        # and 2) a download button
        DataViewer()._header_and_download(
            header="The calculated metrics",
            data=output_df,
            file_name="text_metrics.csv",
        )

        st.write("**Note**: This data frame has been transposed for readability.")
        output_df = output_df.transpose().reset_index()
        output_df.columns = ["Metric"] + [str(c) for c in list(output_df.columns)[1:]]
        st.dataframe(data=output_df, use_container_width=True)


############################
# Code For Reproducibility #
############################


with st.expander("See python code"):
    st.code(
        """
# Note: This is the code for a single text file
# The actual code is slightly more complex
# to allow processing multiple files at once

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
