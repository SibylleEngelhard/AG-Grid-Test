import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode
from streamlit_autorefresh import st_autorefresh

@st.cache_data   
def load_data():
    # Create Example DataFrame 
    data = {'Name': ['Luna', 'Waldi', 'Milo', 'Pixie', 'Nelly'], 'Grade': [14.5, 13.1, 14.2, 11.7, 12.2]}  
    df = pd.DataFrame(data)
    df.insert(loc=1, column='Selected', value=True)
    mean = df.loc[df["Selected"], "Grade"].mean()
    df["Difference"]=df["Grade"]-mean
    return df

def UpdateDataframe(input_df):    
    #Function updates column "Selected" and calculates column "Difference" depending on column "Selected"
    mean=input_df.loc[input_df["Selected"], "Grade"].mean()
    input_df["Difference"]=np.where(input_df["Selected"].array,input_df["Grade"]-mean,np.nan)


# -----Page Configuration
st.set_page_config(page_title="Test AG-Grid", initial_sidebar_state='collapsed')

# defining session states for part 1
if "example_df" not in st.session_state:
    st.session_state.example_df = load_data()
if 'selected_rows' not in st.session_state:   
    st.session_state.selected_rows=[0,1,2,3,4] 
if 'grid_key' not in st.session_state:
    st.session_state.grid_key=0


st.header("1.  AG-Grid with pre selected rows")

col1,col2=st.columns(2)
with col1:
    st.write("Dataframe:")
    placeholder_df=st.empty()
    placeholder_df.dataframe(st.session_state.example_df)
with col2:
    st.write("AG-Grid with pre-selected rows:")
    gb = GridOptionsBuilder.from_dataframe(st.session_state.example_df)
    gb.configure_selection('multiple', use_checkbox=True,pre_selected_rows=st.session_state.selected_rows)
    gridOptions = gb.build()

    ag_grid=AgGrid(st.session_state.example_df,
        key=st.session_state.grid_key, 
        gridOptions = gridOptions, 
        data_return_mode = 'as_input',
        update_mode='selection_changed',
        fit_columns_on_grid_load = True,
        allow_unsafe_jscode = True, 
        reload_data = False, 
    )             

cola,colb,colc=st.columns([2,3,4],gap="small")
with colb:
    button = st.button("Update Dataframe")
    if button:
        temp1=[]
        ag_selected_rows_list = ag_grid['selected_rows']
        for selected_row_dict in ag_selected_rows_list:
            temp1.append(selected_row_dict['_selectedRowNodeInfo']['nodeRowIndex'])
        
        if st.session_state.selected_rows!=temp1:
            st.session_state.selected_rows=temp1
            for i in range(5): #index length of df
                if i not in st.session_state.selected_rows:
                    st.session_state.example_df.at[i,"Selected"] = False
                else:
                    st.session_state.example_df.at[i,"Selected"] = True
            UpdateDataframe(st.session_state.example_df)
           
            # View of dataframe in col1 gets updated
            placeholder_df.empty()
            placeholder_df.write(st.session_state.example_df)
            st.session_state.grid_key+=1
            st_autorefresh(interval=((1*1*1000)), key="dataframerefresh")
        
    
colc.write("Session State of selected rows: "+str(st.session_state.selected_rows))
st.write("- On button click dataframe and 'selected_rows' get updated. AG-Grid gets refreshed but with wrongly selected rows")


if "example_df2" not in st.session_state:
    st.session_state.example_df2 = load_data()
if 'grid_key2' not in st.session_state:
    st.session_state.grid_key2="a0"
if 'selected_rows_array' not in st.session_state:   
    st.session_state.selected_rows_array=st.session_state.example_df["Selected"].array

st.header("2. AG-Grid with selection column")

col3,col4=st.columns(2)
with col3:
    st.write("Dataframe:")
    st.dataframe(st.session_state.example_df2)
with col4:
    st.write("AG-Grid:")
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

    gb3 = GridOptionsBuilder.from_dataframe(st.session_state.example_df2[["Selected","Name","Grade","Difference"]])
    gb3.configure_column( "Selected",editable=True, cellRenderer=checkbox_renderer)
    gb3.configure_selection('multiple', use_checkbox=False)
    gridOptions3 = gb3.build()
    gridOptions3['getRowStyle'] = rowStyle_renderer
    ag_grid2=AgGrid(st.session_state.example_df2,
        key=st.session_state.grid_key2, 
        gridOptions = gridOptions3, 
        data_return_mode = 'as_input',
        update_mode='grid_changed',
        fit_columns_on_grid_load = True,
        allow_unsafe_jscode = True, 
        reload_data = False, 
    )             

    st.session_state.example_df2=ag_grid2['data']
    if  not np.array_equal(st.session_state.selected_rows_array,st.session_state.example_df2["Selected"].array):
    
        UpdateDataframe(st.session_state.example_df2)
        st.session_state.selected_rows_array=st.session_state.example_df2["Selected"].array
        st.session_state.grid_key2+="1"   
        st_autorefresh(interval=((1*1*1000)), key="dataframerefresh")

