import streamlit as st
import pandas as pd
import numpy as np
from stmol import showmol, render_pdb
import py3Dmol
import gzip
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

# TODO: error files: 6h4b - 5zng - 4dst

color_list = ['#7b68ee', '#f08080', '#8fbc8f', '#deb887', '#ff7f50', '#808080', '#6b8e23',
              '#646464', '#34e77b', '#371370', '#ffff96', '#ca3e5e', '#cd913f', '#b776e7',
              '#6efbc9', '#af9b32', '#69cd30', '#254619', '#792187', '#538cd0', '#009a25',
              '#b2dccd', '#ff98d5', '#c85aae', '#afc84a', '#3f190c', '#575757', '#81d7ea',
              '#66f27e', '#1d6914', '#814a19', '#8126c0', '#a0a0a0', '#81c57a', '#9dafff', '#29d0d0']


def cif_to_dict(file_path):
    if file_path[-2:] == 'gz':
        f_handle = gzip.open(file_path, 'rt')
        return MMCIF2Dict(f_handle)

    else:
        return MMCIF2Dict(file_path)


def visualize_interfaces(int_list, show_surf, show_label):
    if len(int_list) > 0:
        view = py3Dmol.view()

        int_id = int_list[0]
        pdb_id = int_id.split("_")[0]
        struct_dict = cif_to_dict(
            f"/datasets/pdb/structures/divided/mmCIF/{pdb_id[1:3]}/{pdb_id}.cif.gz")
        chain_list = sorted(list(set(struct_dict['_atom_site.auth_asym_id'])))
        color_dict = {chain_list[k]: color_list[k % len(color_list)] for k in range(len(chain_list))}

        view.addModel(gzip.open(f"/datasets/pdb/structures/divided/mmCIF/{pdb_id[1:3]}/{pdb_id}.cif.gz",
                                'rt').read(), 'cif')
        view.setStyle()
        chains = set([s for k in [i.split("_")[1:] for i in int_list] for s in k])

        for i in int_list:
            view.addModel(
                open(f"/datasets/pdb/interfaces/mmCIF/{pdb_id[1:3]}/{i}.cif", 'r').read(),
                'cif')

        for c in chains:
            view.setStyle({'chain': c}, {'cartoon': {'color': color_dict[c]}})
            view.setStyle({'chain': c, 'model': 0}, {'cartoon': {'color': color_dict[c], 'opacity': 0.6}})

            if show_label:
                label_lst = [f"Chain {c}",
                             {
                                 "backgroundColor": color_dict[c],
                                 "fontColor": "black",
                                 "backgroundOpacity": 0.8,
                             },
                             {"chain": c}]

                view.addLabel(label_lst[0], label_lst[1], label_lst[2])

        if show_surf:
            for c in chains:
                structure_surf = [
                    {"opacity": 0.7, "color": color_dict[c]},
                    {"chain": c, 'model':0}
                ]

                interface_surf = [
                    {"color": color_dict[c]},
                    {"chain": c, 'model': list(range(1, len(int_list)+1))}
                ]

                view.addSurface(py3Dmol.VDW, interface_surf[0], interface_surf[1])
                view.addSurface(py3Dmol.VDW, structure_surf[0], structure_surf[1])

        view.zoomTo({'chain': list(chains)})

        return view

    else:
        return False
