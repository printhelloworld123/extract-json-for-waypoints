import time
import base64
import json
import numpy as np
import pandas as pd
import streamlit as st

import folium
from streamlit_folium import folium_static

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
    
# Function to obtain missing columns
def get_cols_missing_in_prod_file(prod_file):
    required_cols = ['external_id','name','street','lat','lon','stop_type']
    existing_cols = list(prod_file.columns)
    return list(filter(lambda x: x not in existing_cols, required_cols))

# Function to obtain missing data in production file
def get_missing_data(prepared_file, prod_file, ID_col):
    return list(ID for ID in set(prepared_file[ID_col]) if ID not in set(prod_file['id']))

class ExtractStopSubset:

    def __init__(self, df, prod, ID_col_name):
        self.df = df
        self.prod = prod
        self.ID_col_name = ID_col_name
        self.df_selected = pd.DataFrame(columns=self.prod.columns)
        self.d = {}
    
    # Prepare a file with all the required field details based on Production ID provided in the masterlist file
    def prepare_stop_subset_file(self):
        selected_ID = list(set(map(lambda x: int(x), list(self.df[self.ID_col_name]))))
        self.d = {self.prod.loc[i,'id'] : (self.prod.loc[i,'external_id'],
                                           self.prod.loc[i,'name'],
                                           self.prod.loc[i,'street'],
                                           self.prod.loc[i,'lat'],
                                           self.prod.loc[i,'lon'] ,
                                           self.prod.loc[i,'stop_type']) for i in range(len(self.prod))}

        self.df_selected['id'] = selected_ID
        self.df_selected['external_id'] = list(map(lambda x: self.d[x][0] if x in self.d else 'NIL', selected_ID))
        self.df_selected['name'] = list(map(lambda x: self.d[x][1] if x in self.d else 'NIL', selected_ID))
        self.df_selected['street'] = list(map(lambda x: self.d[x][2] if x in self.d else 'NIL', selected_ID))
        self.df_selected['lat'] = list(map(lambda x: self.d[x][3] if x in self.d else 'NIL', selected_ID))
        self.df_selected['lon'] = list(map(lambda x: self.d[x][4] if x in self.d else 'NIL', selected_ID))
        self.df_selected['stop_type'] = list(map(lambda x: self.d[x][5] if x in self.d else 'NIL', selected_ID))

        
class CSVtoJSON:

    def __init__(self, df):
        self.df = df
        self.lst_stop_details = []
    
    def get_num_waypoints(self):
        return len(self.lst_stop_details)
    
    # Convert CSV file to the desired JSON file format
    def prepare_JSON_file(self):
        self.df = pd.DataFrame.reset_index(self.df)
        self.df = self.df.drop(columns=['index'])
        
        self.df['stop_type'] = list(map(lambda x: x.split('StopType.')[1].lower() 
                                        if x != 'StopType.VIRTUAL' else 'virtual_stop', 
                                        list(self.df['stop_type'])))
        
        self.df.rename(columns={"street": "address", 
                                "lat": "latitude", 
                                "lon": "longitude", 
                                "id": "place_id", 
                                "stop_type": "type"}, inplace=True)
        
        stop_details = list(map(lambda x: {"address": self.df.loc[x,"address"],
                                           "latitude": round(float(self.df.loc[x, "latitude"]),7),
                                           "longitude": round(float(self.df.loc[x, "longitude"]),7), 
                                           "name": self.df.loc[x, "name"], 
                                           "place_id": str(self.df.loc[x, "external_id"]), 
                                           "roadClosed": False, 
                                           "source": "mass_transit", 
                                           "type": str(self.df.loc[x, "type"])}, list(range(len(self.df)))))


        self.lst_stop_details += stop_details
    
    # Display the map visualization of the waypoints
    def display_map(self):
        map_1 = folium.Map(location=[self.df.loc[0,'latitude'], self.df.loc[0,'longitude']], zoom_start=10)
        coords_lst = list(map(lambda lat, lon: (lat,lon), list(self.df['latitude']), list(self.df['longitude'])))
        for coord in list(coords_lst):
            folium.Marker(coord).add_to(map_1)
        folium_static(map_1)
        return map_1
    
