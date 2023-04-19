# TextDescriptives Demo

A streamlit dashboard for extracting text metrics with TextDescriptives.


## TODO

[ ] Add license

[ ] Host on huggingface / streamlit cloud

[ ] Change default text in text box to something lighter :-)

[ ] Ensure environment.yaml works - currently just added stuff manually. When it works, perhaps update installation notes below.

[ ] Ensure models are pre-downloaded to speed up inference

[ ] When supporting the transformer models, we should pre-install the dependencies to avoid it happening at runtime.


## Installation

```shell
conda create --name textdesc python==3.11
pip install textdescriptives streamlit watchdog
streamlit main.py
```