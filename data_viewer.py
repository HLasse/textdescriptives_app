"""
Class for showing header and download button in the same row.
"""

import streamlit as st


class DataViewer:
    def _convert_df_to_csv(self, data, **kwargs):
        return data.to_csv(**kwargs).encode("utf-8")

    def _header_and_download(
        self, header, data, file_name, key=None, label="Download", help="Download data"
    ):
        col1, col2 = st.columns([9, 2])
        with col1:
            st.subheader(header)
        with col2:
            st.write("")
            st.download_button(
                label=label,
                data=self._convert_df_to_csv(data, index=False),
                file_name=file_name,
                key=key,
                help=help,
            )
