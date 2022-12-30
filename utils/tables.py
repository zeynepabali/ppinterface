import streamlit as st
import pandas as pd
import numpy as np
from stmol import showmol, render_pdb
import py3Dmol
import gzip
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from Bio.PDB.MMCIF2Dict import MMCIF2Dict


# TODO 1: Add entry date (from json files)
# TODO 2: Add chains with interfaces
# TODO: Include monomer entries as well with a warning

@st.cache(allow_output_mutation=True)
def get_pdb_data():
    df = pd.read_csv('pdb_combined_data.csv', header=0, index_col=0)
    df["accession_date"] = pd.to_datetime(df["accession_date"]).dt.date
    return df


@st.cache(allow_output_mutation=True)
def get_int_data():
    df = pd.read_csv('interface_data.csv', header=0, index_col=0)
    return df


def render_pdb_builder(df, page_count):
    pdb_builder = GridOptionsBuilder.from_dataframe(df[["pdb_id", "num_interface", "accession_date", "resolution", "experiment_type", "status"]])
    pdb_builder.configure_default_column(editable=False, filterable=True, cellStyle={'text-align': 'center'})
    pdb_builder.configure_column("pdb_id", header_name="PDB ID")
    pdb_builder.configure_column("num_interface", header_name="# Interface")
    pdb_builder.configure_column("accession_date", header_name="Accession Date", type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='yyyy-MM-dd')
    pdb_builder.configure_column("resolution", header_name="Resolution")
    pdb_builder.configure_column("experiment_type", header_name="Experimental Method")
    pdb_builder.configure_column("status", header_name="Status")
    pdb_builder.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=page_count)
    pdb_builder.configure_selection('multiple', use_checkbox=True)

    return pdb_builder


def render_interface_builder(df, page_count):
    int_builder = GridOptionsBuilder.from_dataframe(
        df[['interface_id', 'chain_1', 'chain_2', 'num_chain_1', 'num_chain_2', 'total']])
    int_builder.configure_default_column(editable=False, filterable=True, cellStyle={'text-align': 'center'})
    int_builder.configure_column("interface_id", header_name="Interface ID")
    int_builder.configure_column("chain_1", header_name="Chain 1")
    int_builder.configure_column("chain_2", header_name="Chain 2")
    int_builder.configure_column('num_chain_1', header_name="Number of Residues Chain 1")
    int_builder.configure_column("num_chain_2", header_name="Number of Residues Chain 2")
    int_builder.configure_column("total", header_name="# Interface Residues")
    int_builder.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=page_count)
    int_builder.configure_selection('single', use_checkbox=True)

    return int_builder
