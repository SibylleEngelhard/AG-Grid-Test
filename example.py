import streamlit as st
import pandas as pd
import numpy as np

from st_aggrid import AgGrid, GridOptionsBuilder

df = pd.DataFrame(
    np.random.randint(0, 100, 50).reshape(-1, 5),
    index=range(10),
    columns=list("abcde"),
)

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection('multiple', pre_selected_rows=[3,5])

response = AgGrid(
    df,
    editable=True,
    gridOptions=gb.build(),
    data_return_mode="filtered_and_sorted",
    update_mode="no_update",
    fit_columns_on_grid_load=True,
)