import numpy as np
import pandas as pd
import streamlit as st

from streamlit_autorefresh import st_autorefresh
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode

if 'selected_rows_array' not in st.session_state:
    st.session_state.selected_rows_array=[False,False,False]

df = pd.DataFrame(columns=['ID', 'STATUS'])
df['ID'] = [1, 2, 3]
df['STATUS'] = np.random.randint(0,100,size=(3))
# Dataframe gets additional column 'Selected' which is updated with every refresh according to the session state of selected rows
df.insert(loc=0, column='Selected', value=st.session_state.selected_rows_array)

# Show dataframe without column 'Selected'
st.write(df[['ID','STATUS']])

# add a placeholder to show the session state of the selected_rows_array
# the placeholder gets updated at the bottom as soon as the grid changed
placeholder = st.empty()
placeholder.write("Session State selected_rows_array:  "+str(list(st.session_state.selected_rows_array)))

# checkbox renderer for checkbox
checkbox_renderer = JsCode("""
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
    """)
# rowStyle renderer for different background for selected rows
rowStyle_renderer = JsCode("""
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
    """)

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True, wrapText=True, autoHeight=True)
# gb.configure_column('ID', minWidth=80, maxWidth=80, type=["numericColumn","numberColumnFilter"], sortable=True, sort='desc', checkboxSelection=True, headerCheckboxSelection=True)
gb.configure_column('ID', minWidth=80, maxWidth=80, type=["numericColumn","numberColumnFilter"], sortable=True, sort='desc', checkboxSelection=False, headerCheckboxSelection=False)
gb.configure_column( 'Selected',headerName=' ', minWidth=80, maxWidth=80, editable=True, cellRenderer=checkbox_renderer)
gb.configure_column('STATUS', minWidth=100, maxWidth=100)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=3)
gb.configure_side_bar()
# gb.configure_selection('multiple', pre_selected_rows=pre_selected_rows, use_checkbox=True)
gb.configure_selection('multiple', use_checkbox=False)

gb_grid_options = gb.build()
# rowStyle added
gb_grid_options['getRowStyle'] = rowStyle_renderer


# render the grid and get the selected rows
grid_return = AgGrid(
        df,
        gridOptions = gb_grid_options,
        key = 'ID',
        reload_data = True,
        data_return_mode = DataReturnMode.AS_INPUT,
        update_mode = GridUpdateMode.MODEL_CHANGED, # GridUpdateMode.SELECTION_CHANGED or GridUpdateMode.VALUE_CHANGED or
        allow_unsafe_jscode = True,
        fit_columns_on_grid_load = False,
        enable_enterprise_modules = False,
        height = 320,
        width = '100%',
        theme = "streamlit"
    )

# save the array of column 'Selected' in the session state and update display of placeholder
if not np.array_equal(st.session_state.selected_rows_array,grid_return['data']['Selected']):
    st.session_state.selected_rows_array=grid_return['data']['Selected']
    placeholder.empty()
    placeholder.write("Session State selected_rows_array:  "+str(list(st.session_state.selected_rows_array)))

st_autorefresh(interval=((1*2*1000)), key="dataframerefresh")
