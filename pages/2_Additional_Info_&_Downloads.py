import streamlit as st

st.set_page_config(layout="wide")
st.title("Additional Information")

ext_interfaces, vdw_definitions, data_download = st.tabs(["Extracting Interfaces", "VDW Definitions", "Download Data"])

with ext_interfaces:
    st.write("Interface definitions")

with vdw_definitions:
    st.write("VDW parameters used")

with data_download:
    st.write("Download all pdb information")
    st.write("Download all interface information")