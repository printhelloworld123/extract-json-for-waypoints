import time
import base64
import json
import numpy as np
import pandas as pd
import streamlit as st

import folium
from streamlit_folium import folium_static

import functions
from functions import *

timestr = time.strftime("%d%m%y")
 
def main():
    sidebar = ["Extract JSON (Basic)",
               "Extract JSON (Requires Matching)"]
    choice = st.sidebar.selectbox("Select task", sidebar)

    if choice == "Extract JSON (Basic)":
        try:
            st.title("Extract JSON (Basic)")

            st.subheader("1.Upload CSV File")
            section_1_uploaded_file = st.file_uploader("",type=["csv"])
            section_1_prepared_file = pd.read_csv(section_1_uploaded_file)
            
            st.subheader("2.Check that the JSON File is prepared correctly")
            section_1_prepared_file = CSVtoJSON(section_1_prepared_file)
            check_missing_columns = get_cols_missing_in_prod_file(section_1_prepared_file.df)
            check_missing_columns = (', ').join(check_missing_columns)
            if len(check_missing_columns) != 0:
                st.markdown('####')
                st.write('Your csv file is missing these columns: ' + str(check_missing_columns))
            else:
                st.markdown('####')
                section_1_prepared_file.prepare_JSON_file()
                st.markdown('####')
                st.write("There are **{}** waypoints in the JSON file".format(str(section_1_prepared_file.get_num_waypoints())))
                section_1_prepared_file.df
                section_1_prepared_file.display_map()

                st.subheader("3.Download JSON file")
                text_downloader(section_1_prepared_file.lst_stop_details, section_1_uploaded_file.name.split('.csv')[0])
        except:
            pass
    
    elif choice == 'Extract JSON (Requires Matching)':
        try:
            st.title('Extract JSON (Requires Matching)')
            
            st.subheader("1.Upload the waypoints CSV file")
            st.markdown('####')
            section_2_uploaded_df = st.file_uploader("Upload the master list of waypoints",type=["csv"])
            section_2_prepared_df = pd.read_csv(section_2_uploaded_df)
            st.markdown('####')
            section_2_uploaded_prod = st.file_uploader("Upload the waypoints from production",type=["csv"])
            section_2_prepared_prod = pd.read_csv(section_2_uploaded_prod)
            check_missing_columns = (', ').join(get_cols_missing_in_prod_file(section_2_prepared_prod))
            
            st.subheader("2.Configure the parameters")
            st.markdown('####')
            if len(check_missing_columns) != 0:
                st.write('Your csv file from production is missing these columns: ' + str(check_missing_columns))
            else:
                ID_col_names = tuple(section_2_prepared_df.columns)
                ID_col = st.selectbox('In the masterlist of stops, What is the name of the column for the masstransit ID?',ID_col_names)
                missing_data = get_missing_data(section_2_prepared_df,section_2_prepared_prod,ID_col)
                if len(missing_data) != 0:
                    st.write('Your production csv file is missing data for these waypoints (Masstransit ID provided) : ' + str(missing_data))
                else:
                    section_2_prepared_file = ExtractStopSubset(section_2_prepared_df,section_2_prepared_prod,ID_col) 
                    section_2_prepared_file.prepare_stop_subset_file()
                    section_2_prepared_file = section_2_prepared_file.df_selected
                    section_2_prepared_file = CSVtoJSON(section_2_prepared_file)
                    section_2_prepared_file.prepare_JSON_file()

                    st.subheader("3.Check that the JSON File is prepared correctly")
                    st.markdown('####')
                    st.write("There are **{}** waypoints in the JSON file".format(str(section_2_prepared_file.get_num_waypoints())))
                    section_2_prepared_file.df
                    section_2_prepared_file.display_map()

                    st.subheader("4.Download JSON file")
                    st.markdown('####')
                    text_downloader(section_2_prepared_file.lst_stop_details, 'subset_of_stops')
    
        except:
            pass  
        

if __name__ == "__main__":
    main()
    
