import numpy as np
import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode
# from streamlit_autorefresh import st_autorefresh


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
    # Function updates column "Selected" and calculates column "Difference" depending on column "Selected"
    mean = input_df.loc[input_df["Selected"], "Grade"].mean()
    input_df["Difference"] = np.where(input_df["Selected"].array, input_df["Grade"] - mean, np.nan)


# -----Page Configuration
st.set_page_config(page_title="Test AG-Grid", initial_sidebar_state="collapsed")

#  ----defining session states 
if "example_df" not in st.session_state:
    st.session_state.example_df = load_data()
if "grid_key" not in st.session_state:
    st.session_state.grid_key = 0
if "selected_rows_array" not in st.session_state:
    st.session_state.selected_rows_array = st.session_state.example_df["Selected"].array

st.header("AG-Grid with checkbox for boolean column")



col1, col2 = st.columns(2)
with col1:
    st.write("Dataframe:")
    st.dataframe(st.session_state.example_df)
with col2:
    st.write("AG-Grid:")
    checkbox_renderer = JsCode(
        """
	    class CheckboxRenderer{
	    init(params) {
	        this.params = params;
	        this.eGui = document.createElement('input');
	        this.eGui.type = 'checkbox';
	        this.eGui.checked = params.value;
	        this.checkedHandler = this.checkedHandler.bind(this);
	        this.eGui.addEventListener('click', this.checkedHandler);
	    }
	    checkedHandler(e) {
	        let checked = e.target.checked;
	        let colId = this.params.column.colId;
	        this.params.node.setDataValue(colId, checked);
	    }
	    getGui(params) {
	        return this.eGui;
	    }
	    destroy(params) {
	    this.eGui.removeEventListener('click', this.checkedHandler);
	    }
	    }//end class
    """
    )
    rowStyle_renderer = JsCode(
        """
        function(params) {
            if (params.data.Selected) {
                return {
                    'color': 'black',
                    'backgroundColor': 'pink'
                }
            }
            else {
                return {
                    'color': 'black',
                    'backgroundColor': 'white'
                }
            }
        }; 
    """
    )

    gb = GridOptionsBuilder.from_dataframe(st.session_state.example_df[["Selected", "Name", "Grade", "Difference"]])
    gb.configure_column("Selected", minWidth=90, maxWidth=90, editable=True, cellRenderer=checkbox_renderer)
    gb.configure_column("Name", minWidth=80, maxWidth=80)
    gb.configure_column("Grade", minWidth=75, maxWidth=75)
    gb.configure_selection("multiple", use_checkbox=False)
    gridOptions = gb.build()
    gridOptions["getRowStyle"] = rowStyle_renderer
    ag_grid = AgGrid(
        st.session_state.example_df,
        key=st.session_state.grid_key,
        gridOptions=gridOptions,
        data_return_mode="as_input",
        update_mode="grid_changed",
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
        reload_data=False,
    )

placeholder_sess_state = st.empty()
placeholder_sess_state.write("Session State of selected rows: " + str(list(st.session_state.selected_rows_array)))
placeholder_sess_state2 = st.empty()
placeholder_sess_state2.write("Session State of grid_key: " + str(st.session_state.grid_key))

st.session_state.example_df = ag_grid["data"]
if not np.array_equal(st.session_state.selected_rows_array, st.session_state.example_df["Selected"].array):
    update_dataframe(st.session_state.example_df)
    st.session_state.selected_rows_array = st.session_state.example_df["Selected"].array
    placeholder_sess_state.write("Session State of selected rows: " + str(list(st.session_state.selected_rows_array)))
    placeholder_sess_state2.write("Session State of grid_key: " + str(st.session_state.grid_key))

    st.session_state.grid_key += 1
    st.experimental_rerun()
    # st_autorefresh(interval=((500)), key="dataframerefresh")
