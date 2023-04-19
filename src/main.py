"""
Dashboard for showcasing extraction of text metrics with textdescriptives.

"""

from io import StringIO
import streamlit as st
import textdescriptives as td
import numpy as np

from data_viewer import DataViewer


################
# Introduction #
################


col1, col2 = st.columns([9, 2])
with col1:
    st.title("Extract Text Statistics")
with col2:
    st.image(
        "https://github.com/HLasse/TextDescriptives/raw/main/docs/_static/icon.png"
    )

st.write(
    "Calculate a large variety of statistics from text via the "
    "[**TextDescriptives**](https://github.com/HLasse/TextDescriptives) python package "
    f"(v/{td.__version__}). "
    "Includes descriptive statistics and metrics related to readability and dependency distance."
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
    label="Input",
    options=["Enter text", "Upload file"],
    index=0,
    horizontal=True
)

with st.form(key='settings_form'):

    split_by_line = st.checkbox(label="Split by newline", value=True)

    string_data = None

    if input_choice == "Upload file":

        uploaded_file = st.file_uploader(
            label="Choose a .txt file",
            type=["txt"],
            accept_multiple_files=False
        )

        if uploaded_file is not None:
            # To convert to a string based IO:
            string_data = StringIO(
                uploaded_file.getvalue().decode("utf-8")
            ).read()

    else:

        default_text = """Little interest or pleasure in doing things?
Feeling down, depressed, or hopeless?
Trouble falling or staying asleep, or sleeping too much?
Feeling tired or having little energy?
Poor appetite or overeating?
Feeling bad about yourself - or that you are a failure or have let yourself or your family down?"""

        string_data = st.text_area(
            label="Enter text",
            value=default_text,
            height=170,
            max_chars=None
        )

    # Selection of model to use
    model_name = st.selectbox(
        label="Model",
        options=["en_core_web_sm", "en_core_web_lg"],
        index=0
    )

    apply_settings_button = st.form_submit_button(label='Apply')


#############
# Apply NLP #
#############


if apply_settings_button and string_data is not None and string_data:

    # Clean and (optionally) split the text
    string_data = string_data.strip()
    if split_by_line:
        string_data = string_data.split("\n")
    else:
        string_data = [string_data]

    # Remove empty strings
    # E.g. due to consecutive newlines
    string_data = [s for s in string_data if s]

    # Will automatically download the relevant model (´en_core_web_lg´) and extract all metrics
    # TODO: Download beforehand to speed up inference
    df = td.extract_metrics(
        text=string_data,
        spacy_model=model_name,
        metrics=None
    )

    ###################
    # Present Results #
    ###################

    # Create 2 columns with 1) the output header
    # and 2) a download button
    DataViewer()._header_and_download(
        header="The calculated metrics",
        data=df,
        file_name="text_metrics.csv"
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
model_name = "..."
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
    spacy_model=model_name
)

""",
        language="python",
        line_numbers=True
    )
