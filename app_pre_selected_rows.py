import numpy as np
import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode
from streamlit_autorefresh import st_autorefresh
import time

@st.cache_data
def load_data():
    # Create Example DataFrame
    data = {
        "Name": ["Luna", "Waldi", "Milo", "Pixie", "Nelly"],
        "Grade": [14.5, 13.1, 14.2, 11.7, 12.2],
    }
    df = pd.DataFrame(data)
    df.insert(loc=1, column="Selected", value=True)
    mean = df.loc[df["Selected"], "Grade"].mean()
    df["Difference"] = df["Grade"] - mean
    return df


def update_dataframe(input_df):
    for i in range(5):  # index length of df
        if i not in st.session_state.selected_rows:
            st.session_state.example_df.at[i, "Selected"] = False
        else:
            st.session_state.example_df.at[i, "Selected"] = True
    # Function updates column "Selected" and calculates column "Difference" depending on column "Selected"
    mean = input_df.loc[input_df["Selected"], "Grade"].mean()
    input_df["Difference"] = np.where(input_df["Selected"].array, input_df["Grade"] - mean, np.nan)


# -----Page Configuration
st.set_page_config(page_title="Test AG-Grid", initial_sidebar_state="collapsed")

#  ------------------------------------------------------------------------------------------
# 1. Example with pre-selected rows

if "example_df" not in st.session_state:
    st.session_state.example_df = load_data()
if "selected_rows" not in st.session_state:
    st.session_state.selected_rows = [0, 1, 2, 3, 4]


st.header("1.  AG-Grid with pre-selected rows")

st.write("AG-Grid with pre-selected rows:")
gb = GridOptionsBuilder.from_dataframe(st.session_state.example_df)
gb.configure_selection("multiple", use_checkbox=True, pre_selected_rows=st.session_state.selected_rows)
gridOptions = gb.build()

ag_grid = AgGrid(
    st.session_state.example_df,
    gridOptions=gridOptions,
    data_return_mode="as_input",
    update_mode="selection_changed",
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True,
    enable_enterprise_modules=False,
    reload_data=False,
)
placeholder_sessstate=st.empty()
placeholder_sessstate.write("Session State of selected rows: &nbsp;" + str(st.session_state.selected_rows))

temp1 = []
ag_selected_rows_list = ag_grid["selected_rows"]
for selected_row_dict in ag_selected_rows_list:
    temp1.append(selected_row_dict["_selectedRowNodeInfo"]["nodeRowIndex"])
time.sleep(2)
if st.session_state.selected_rows != temp1:
    st.session_state.selected_rows = temp1
    placeholder_sessstate.write("Session State of selected rows: &nbsp;" + str(st.session_state.selected_rows))
   
    # Function that updates the dataframe according to selected rows in session state
    update_dataframe(st.session_state.example_df)
   
    st.experimental_rerun()
    #st_autorefresh(interval=((500)), key="dataframerefresh")


