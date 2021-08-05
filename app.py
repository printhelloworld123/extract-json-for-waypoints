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

# Function to allow download of prepared csv file as txt file #
def text_downloader(file, name):
    with open("test.json", "w", encoding="utf-8") as f:
        json.dump(file, f, ensure_ascii=False, indent=2)
    with open("test.json", "r", encoding="utf-8") as f:
        string = f.read()
    b64 = base64.b64encode(string.encode()).decode()
    new_filename = name + "_{}.json".format(timestr)
    href = f'<a href="data:file/txt;base64,{b64}" download="{new_filename}">Click this link to download the JSON file</a>'
    st.markdown(href,unsafe_allow_html=True)
    

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
            section_1_prepared_file.prepare_JSON_file()
            st.markdown('####')
            st.write("There are **{}** waypoints in the JSON file".format(str(section_1_prepared_file.get_num_waypoints())))
            section_1_prepared_file.df
            section_1_prepared_file.display_map()

            st.subheader("3.Download JSON file")
            st.markdown('####')
            text_downloader(section_1_prepared_file.lst_stop_details, section_1_uploaded_file.name.split('.csv')[0])
        except:
            pass     
    
    elif choice == 'Extract JSON (Requires Matching)':
        try:
            st.title('Extract JSON (Requires Matching)')
            
            st.subheader("1.Upload the waypoints CSV file")
            st.markdown('####')
            section_2_df = st.file_uploader("Upload the master list of waypoints",type=["csv"])
            section_2_df_file = pd.read_csv(section_2_df)
            st.markdown('####')
            section_2_prod = st.file_uploader("Upload the waypoints from production",type=["csv"])
            section_2_prod_file = pd.read_csv(section_2_prod)

            st.subheader("2.Configure the parameters")
            st.markdown('####')
            ID_col_names = tuple(section_2_df_file.columns)
            ID_col = st.selectbox('In the masterlist of stops, What is the name of the column for the masstransit ID?',ID_col_names)
            section_2_selected_stops_file = ExtractStopSubset(section_2_df_file,section_2_prod_file,ID_col)
            section_2_selected_stops_file.prepare_stop_subset_file()
            final_file = CSVtoJSON(section_2_selected_stops_file.df_selected)
            final_file.prepare_JSON_file()

            st.subheader("3.Check that the JSON File is prepared correctly")
            st.markdown('####')
            st.write("There are **{}** waypoints in the JSON file".format(str(final_file.get_num_waypoints())))
            final_file.df
            final_file.display_map()

            st.subheader("4.Download JSON file")
            st.markdown('####')
            text_downloader(final_file.lst_stop_details, 'subset_of_stops')
        
        except:
            pass  
        

if __name__ == "__main__":
    main()