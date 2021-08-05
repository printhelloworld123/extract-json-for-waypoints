import time
import base64
import json
import numpy as np
import pandas as pd
import streamlit as st

import folium
from streamlit_folium import folium_static

class ExtractStopSubset:

    def __init__(self, df, prod, ID_col_name):
        self.df = df
        self.prod = prod
        self.ID_col_name = ID_col_name
        self.df_selected = pd.DataFrame(columns=self.prod.columns)
    
    def prepare_stop_subset_file(self):
        selected_ID = list(map(lambda x: int(x), list(self.df[self.ID_col_name])))
        
        for i in range(len(self.prod)):
            ID = self.prod.loc[i,'id']
            if ID in selected_ID:
                if ID not in list(self.df_selected['id']):
                    self.df_selected = self.df_selected.append(self.prod.iloc[i])
        

class CSVtoJSON:

    def __init__(self, df):
        self.df = df
        self.lst_stop_details = []
    
    def get_num_waypoints(self):
        return len(self.lst_stop_details)
    
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
                                           "latitude": round(self.df.loc[x, "latitude"],7),
                                           "longitude": round(self.df.loc[x, "longitude"],7), 
                                           "name": self.df.loc[x, "name"], 
                                           "place_id": str(self.df.loc[x, "external_id"]), 
                                           "roadClosed": False, 
                                           "source": "mass_transit", 
                                           "type": str(self.df.loc[x, "type"])}, list(range(len(self.df)))))


        self.lst_stop_details += stop_details
    
    def display_map(self):
        map_1 = folium.Map(location=[self.df.loc[0,'latitude'], self.df.loc[0,'longitude']], zoom_start=10)
        coords_lst = list(map(lambda lat, lon: (lat,lon), list(self.df['latitude']), list(self.df['longitude'])))
        for coord in list(coords_lst):
            folium.Marker(coord).add_to(map_1)
        folium_static(map_1)
        return map_1
    