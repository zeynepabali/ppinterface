import streamlit as st
import pandas as pd
import numpy as np
from stmol import showmol, render_pdb
import py3Dmol
import gzip
import os.path
from io import StringIO
from datetime import datetime
import random
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from utils.visualization import visualize_interfaces
from utils.tables import get_pdb_data, get_int_data, render_pdb_builder, render_interface_builder
import zipfile


st.set_page_config(layout="wide")
column3_2 = st.columns([3, 2])

with column3_2[0]:
    st.title("Interface Dataset")

pdb_df = get_pdb_data()
int_df = get_int_data()

with column3_2[1]:
    #current_random = random.choice(int_df.interface_id)
    current_random = "12e8_H_L"
    st.write(f"Random interface: {current_random}")
    #view = visualize_interfaces([current_random])
    #view.spin("y")
    #st.write(view.selectedAtoms({'chain': 'A'}))
    #showmol(view, height=300, width=500)

search_pdbid, search_keyword = st.tabs(["Search by PDB ID", "Search by Keyword"])

with search_pdbid:

    search_txt = ""
    upload_txt = ""

    pdb_id_txt = st.text_area(
        "Enter PDB IDs seperated by comma, white space or newline, such as 4d2i, 4cs4, 4ciw, 4q4w.", key='pdbtext')

    if pdb_id_txt != "":
        pdb_id_list = [i.strip() for i in pdb_id_txt.replace(" ", "").replace(" ", ",").replace("\n", ",").split(",") if i.strip() != ""]

    upload_pdbid_list = st.file_uploader("Upload a file with PDB IDs")

    if upload_pdbid_list is not None:
        upload_txt = upload_pdbid_list.getvalue().decode('utf-8')

    search_txt = pdb_id_txt + "\n" + upload_txt
    pdb_id_list = [i.strip() for i in search_txt.replace(" ", "").replace(" ", ",").replace("\n", ",").split(",") if i.strip() != ""]

    pdb_submit_button = st.button("Search", key='pdbsearch')

with search_keyword:

    keyword_txt = st.text_area(
        "Enter PDB IDs seperated by comma, white space or newline, such as 4d2i, 4cs4, 4ciw, 4q4w. Press Ctrl+Enter to apply", key='keytext')
    keyword_list = [i.strip() for i in pdb_id_txt.replace(" ", "").replace(" ", ",").replace("\n", ",").split(",") if i.strip() != ""]

    key_submit_button = st.button("Search", key='keysearch')

st.markdown("---")

if pdb_submit_button or pdb_id_txt:
    pdb_df = pdb_df[pdb_df.pdb_id.isin(pdb_id_list)]
    int_df = int_df[int_df.pdb_id.isin(pdb_df.pdb_id)]

    # Divide the page to 8 columns for using smaller components
    column_7_1 = st.columns([7, 1])

    with column_7_1[0]:
        st.subheader("PDB Entries with Interfaces")
        # Table information
        # Homomer - heteromer
        # organism
        # Status to last column


        st.download_button(label="Download current view as CSV",
                           data=pdb_df.to_csv().encode('utf-8'),
                           file_name=f"structures_table_{datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')}.csv",
                           mime='text/csv')

    with column_7_1[1]:
        pdb_select_pagination = st.selectbox("Number of rows per page: ", (10, 20, 50, 100), index=0, key='pdb')

    # PDB Table
    # TODO 4: Enable multi-selection and filter the interface table accordingly
    pdb_builder = render_pdb_builder(pdb_df, pdb_select_pagination).build()

    with st.spinner('Loading data...'):
        pdb_return = AgGrid(pdb_df,
                            width='100%',
                            theme='material',
                            enable_enterprise_modules=False,
                            gridOptions=pdb_builder,
                            custom_css={".ag-header-cell-label": {"justify-content": "center;"}})

    pdb_selected_df = pd.DataFrame(pdb_return['selected_rows'])

    if not pdb_selected_df.empty:
        int_df = int_df[int_df.pdb_id.isin(pdb_selected_df.pdb_id)]

    st.markdown("---")

    # Divide the page to 8 columns for using smaller components
    column_7_1 = st.columns([7, 1])

    with column_7_1[0]:
        st.subheader("Interface(s)")
        # Table information
        # Homomer - heteromer

        st.download_button(label="Download current view as CSV",
                           data=int_df.to_csv().encode('utf-8'),
                           file_name=f"interfaces_table_{datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')}.csv",
                           mime='text/csv')

    with column_7_1[1]:
        int_select_pagination = st.selectbox("Number of rows per page: ", (10, 20, 50, 100), index=0, key='interface')

    # Interface Table
    int_builder = render_interface_builder(int_df, int_select_pagination).build()

    with st.spinner('Loading data...'):
        int_return = AgGrid(int_df,
                            width='100%',
                            theme='material',
                            enable_enterprise_modules=False,
                            gridOptions=int_builder,
                            fit_columns_on_grid_load=True,
                            custom_css={".ag-header-cell-label": {"justify-content": "center;"}})

    int_selected_df = pd.DataFrame(int_return['selected_rows'])

    # TODO 10: Visualization (Show selected interface, and its dimer)

    st.markdown("---")
    st.subheader("Visualization")

    fullwidth_column_4_6 = st.columns([4, 6])

    if not int_selected_df.empty:

        with fullwidth_column_4_6[1]:
            if not int_selected_df.empty:
                interface_list = list(int_df[int_df.pdb_id.isin(int_selected_df.pdb_id)].interface_id)
                select_int_list = st.multiselect("Choose interfaces", interface_list,
                                                 int_selected_df.interface_id[0])
                if len(select_int_list) > 0:
                    email = st.text_input("Email (Optional)", help="Send me an email with download information. Created data will be available for 7 days.")

                if len(select_int_list) == 1:
                    with open(f'/datasets/pdb/interfaces/mmCIF/{select_int_list[0][1:3]}/{select_int_list[0]}.cif', 'r') as f:
                        st.download_button(label='Download interface structure',
                                           data=f,
                                           file_name=f"{select_int_list[0]}.cif")

                if len(select_int_list) > 1:
                    zip_name = f"{datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')}_interface_structure.zip"
                    with zipfile.ZipFile(zip_name, 'w') as zip_object:
                        for int_id in select_int_list:
                            zip_object.write(f'/datasets/pdb/interfaces/mmCIF/{int_id[1:3]}/{int_id}.cif', f"{int_id}.cif")

                    st.download_button(label='Download interface structures as zip',
                                       data = open(zip_name, 'rb'),
                                       file_name=zip_name,
                                       mime='application/zip',
                                       key='zip_downlaod')


        with fullwidth_column_4_6[0]:



            if len(select_int_list) > 1:
                show_surf = st.checkbox("Show/hide surface", value=True)

            else:
                show_surf = st.checkbox("Show/hide surface", value=False)

            show_label = st.checkbox("Show/hide labels", value=True)
            view = visualize_interfaces(select_int_list, show_surf, show_label)

            if view:
                with st.spinner('Loading...'):
                    showmol(view, )
            else:
                st.write("Select at least one interface to visualize.")

    else:
        st.write("Choose an interface from interfaces table to visualize.")

# TODO 13: Add statistics (Number of PDBs per year, number of interfaces per year, residue number per interface distr.)
# TODO 14: Add VDW values as parameter files to about
# TODO 15: Add an explanation page on how interfaces are extracted

# TODO: add search by keywords (pfam)
# TODO: visualization - show contacting & nearby seperately

# TODO: naming - ppinterface - ppint - PrIntDB (interface dataset) + PPConf (seq cluster) + PIface v2.0 (struc clutser) +