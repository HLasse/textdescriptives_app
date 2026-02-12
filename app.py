"""
Dashboard for showcasing extraction of text metrics with textdescriptives.
"""

import tempfile

import gradio as gr
import pandas as pd
import textdescriptives as td

from options import (
    all_model_size_options_pretty_to_short,
    available_model_size_options,
    language_options,
    metrics_options,
)
from process_text import text_to_metrics

DEFAULT_TEXT = """Hello, morning dew. The grass whispers low.
I'm here to dance. The gentle breeze does show.
Good morning, world. The birds sing in delight.
Let's spread our wings. The butterflies take flight.
Nature's chorus sings, a symphony of light."""

LANG_OPTIONS = language_options()
LANG_NAMES = list(LANG_OPTIONS.keys())
DEFAULT_LANG_INDEX = LANG_NAMES.index("English")

CODE_SNIPPET = """\
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
"""

CSS = """
.citation {
    font-size: 0.85em;
    color: #666;
}
"""


def toggle_input(choice):
    if choice == "Upload file(s)":
        return gr.update(visible=False), gr.update(visible=True)
    return gr.update(visible=True), gr.update(visible=False)


def process_and_display(
    input_choice,
    text_input,
    files,
    split_by_line,
    language_pretty,
    model_size_pretty,
    metrics,
):
    if not metrics:
        return (
            gr.update(value="**Please select at least one metric.**", visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            None,
        )

    language_short = LANG_OPTIONS[language_pretty]
    model_size_short = all_model_size_options_pretty_to_short()[model_size_pretty]

    if model_size_pretty not in available_model_size_options(lang=language_short):
        return (
            gr.update(
                value="**Sorry!** The chosen *model size* is not available in this language. Please try another.",
                visible=True,
            ),
            gr.update(visible=False),
            gr.update(visible=False),
            None,
        )

    # Build mapping of filename -> text
    file_name_to_text = {}
    if input_choice == "Upload file(s)":
        if not files:
            return (
                gr.update(value="**Please upload at least one file.**", visible=True),
                gr.update(visible=False),
                gr.update(visible=False),
                None,
            )
        for f in files:
            with open(f, "r", encoding="utf-8") as fh:
                file_name_to_text[f.rsplit("/", 1)[-1]] = fh.read()
    else:
        if not text_input or not text_input.strip():
            return (
                gr.update(value="**Please enter some text.**", visible=True),
                gr.update(visible=False),
                gr.update(visible=False),
                None,
            )
        file_name_to_text["input"] = text_input

    # Extract metrics for each text
    output_df = pd.concat(
        [
            text_to_metrics(
                string=string,
                language_short=language_short,
                model_size_short=model_size_short,
                metrics=metrics,
                split_by_line=split_by_line,
                filename=filename if input_choice == "Upload file(s)" else None,
            )
            for filename, string in file_name_to_text.items()
        ],
        ignore_index=True,
    )

    # Transpose for readability
    transposed = output_df.transpose().reset_index()
    transposed.columns = ["Metric"] + [str(c) for c in list(transposed.columns)[1:]]

    # Write CSV to a temp file for download
    csv_path = tempfile.NamedTemporaryFile(
        suffix=".csv", delete=False, prefix="text_metrics_"
    ).name
    output_df.to_csv(csv_path, index=False)

    return (
        gr.update(
            value="**Note**: This data frame has been transposed for readability.",
            visible=True,
        ),
        gr.update(value=transposed, visible=True),
        gr.update(value=csv_path, visible=True),
        csv_path,
    )


with gr.Blocks(title="TextDescriptives", css=CSS) as demo:
    ################
    # Introduction #
    ################

    gr.HTML(
        '<div style="display:flex;align-items:center;gap:12px;">'
        '<img src="https://github.com/HLasse/TextDescriptives/raw/main/docs/_static/icon.png" '
        'style="height:56px;width:auto;border-radius:8px;" />'
        '<h1 style="margin:0;font-size:2em;">Extract Text Statistics</h1>'
        '</div>'
    )

    gr.Markdown(
        f"Calculate a large variety of statistics from text via the "
        f"[**TextDescriptives**](https://github.com/HLasse/TextDescriptives) python package "
        f"(v/{td.__version__}) and download the results as a .csv file. "
        f"Includes descriptive statistics and metrics related to readability, "
        f"information theory, text coherence and text quality. "
        f"Source on [**GitHub**](https://github.com/HLasse/TextDescriptives_app) "
        f"— [open an issue](https://github.com/HLasse/textdescriptives_app/issues) for feedback."
    )

    gr.Markdown(
        "Hansen, L., Olsen, L. R., & Enevoldsen, K. (2023). *TextDescriptives: A Python package for "
        "calculating a large variety of metrics from text.* "
        "[JOSS, 8(84), 5153](https://doi.org/10.21105/joss.05153)",
        elem_classes="citation",
    )

    ############
    # Settings #
    ############

    with gr.Group():
        input_choice = gr.Radio(
            choices=["Enter text", "Upload file(s)"],
            value="Enter text",
            label="Input",
        )

        text_input = gr.Textbox(
            label="Enter text",
            value=DEFAULT_TEXT,
            lines=7,
            visible=True,
        )

        file_upload = gr.File(
            label="Choose .txt file(s)",
            file_types=[".txt"],
            file_count="multiple",
            visible=False,
        )

        split_by_line = gr.Checkbox(label="Split by newline", value=True)

        input_choice.change(
            fn=toggle_input,
            inputs=input_choice,
            outputs=[text_input, file_upload],
        )

    with gr.Row():
        language_dropdown = gr.Dropdown(
            label="Language",
            choices=LANG_NAMES,
            value=LANG_NAMES[DEFAULT_LANG_INDEX],
        )
        model_size_dropdown = gr.Dropdown(
            label="Model Size",
            choices=available_model_size_options(lang="all"),
            value=available_model_size_options(lang="all")[0],
        )

    metrics_select = gr.CheckboxGroup(
        label="Metrics",
        choices=metrics_options(),
        value=metrics_options(),
    )

    gr.Markdown(
        "See the [**documentation**](https://hlasse.github.io/TextDescriptives/) "
        "for information on the available metrics."
    )

    apply_btn = gr.Button("Apply", variant="primary")

    #############
    # Results   #
    #############

    status_msg = gr.Markdown(visible=False)
    results_table = gr.DataFrame(visible=False, label="Results")
    csv_state = gr.State(value=None)
    download_btn = gr.DownloadButton("Download CSV", visible=False, variant="primary")

    apply_btn.click(
        fn=process_and_display,
        inputs=[
            input_choice,
            text_input,
            file_upload,
            split_by_line,
            language_dropdown,
            model_size_dropdown,
            metrics_select,
        ],
        outputs=[status_msg, results_table, download_btn, csv_state],
    )

    ############################
    # Code For Reproducibility #
    ############################

    with gr.Accordion("See python code", open=False):
        gr.Code(value=CODE_SNIPPET, language="python", interactive=False)

    #######
    # FAQ #
    #######

    gr.Markdown("## FAQ")

    with gr.Accordion("What does the 'Split by newline' option do?", open=False):
        gr.Markdown(
            "When the `Split by newline` option is `enabled`, the metrics calculation is "
            "performed separately for each paragraph. I.e. whenever there's a line break, "
            "we split the text.\n\n"
            "When this option is `disabled`, the entire text is processed at once."
        )

    with gr.Accordion(
        "Why do I get a warning/error message for certain languages or model sizes?",
        open=False,
    ):
        gr.Markdown(
            "Some combinations of languages, model sizes, and metrics are not currently supported in the app. "
            "While we *are* working on this, you may currently see an error message after clicking `Apply`.\n\n"
            "If you need this language and/or model size to work for your project, "
            "please open an [issue](https://github.com/HLasse/textdescriptives_app/issues). "
            "This may cause us to prioritize supporting your use case."
        )

if __name__ == "__main__":
    demo.launch()
