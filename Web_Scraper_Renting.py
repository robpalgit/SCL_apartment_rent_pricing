from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from datetime import date


# Define web scraping function
def web_scraper(url):
        
    soup_list = []
    sauce = requests.get(url).text
    soup = BeautifulSoup(sauce)
    soup_list.append(soup)
    
    arrow_buttons = soup.find_all('span', class_="andes-pagination__arrow-title")
    i=1
    while arrow_buttons[0].text=='Siguiente' or len(arrow_buttons) > 1:
        for button in arrow_buttons:
            if button.text=='Siguiente':
                url = button.parent.get('href')
                sauce = requests.get(url).text
                soup = BeautifulSoup(sauce)
                soup_list.append(soup)
                arrow_buttons = soup.find_all('span', class_="andes-pagination__arrow-title")
        i+=1 
                
    return soup_list


# Define function to extract the data from each soup
def extract_data_from_soup(soup):

    area = []
    rooms = []
    bathrooms = []
    price_clp = []
    address = []

    for item in soup.find_all('div', class_="item__info-container"):
        
        item_attrs = item.find('div', class_="item__attrs").string
        attrs_list = [int(s) for s in item_attrs.split() if s.isdigit()]
        
        if len(attrs_list)==3:
            item_area = attrs_list[0]
            item_area = int(item_area)
            area.append(item_area)
    
            item_rooms = attrs_list[1]
            rooms.append(item_rooms)
    
            item_bathrooms = attrs_list[2]
            bathrooms.append(item_bathrooms)
    
        if len(attrs_list)==2:
            item_area = None
            area.append(item_area)
            
            item_rooms = attrs_list[0]
            rooms.append(item_rooms)
    
            item_bathrooms = attrs_list[1]
            bathrooms.append(item_bathrooms)
        
        if len(attrs_list)<=1 or len(attrs_list)>3:
            item_area = None
            area.append(item_area)
            
            item_rooms = None
            rooms.append(item_rooms)
            
            item_bathrooms = None
            bathrooms.append(item_bathrooms)
       
    
        symbol = item.find('span', class_="price__symbol").string        
        price = item.find('span', class_="price__fraction") 
        uf = item.find('span', class_="price__clf-full")
    
        if symbol=='$':
            price_str = price.string
            price_str_split = price_str.split('.')
            if len(price_str_split)==1:
                price = (int(price_str_split[0]))
                price_clp.append(price)
            if len(price_str_split)==2:
                price = (int(price_str_split[0])*1000 + int(price_str_split[1]))
                price_clp.append(price)
            if len(price_str_split)==3:
                price = (int(price_str_split[0])*1000000 + int(price_str_split[1])*1000 + int(price_str_split[2]))
                price_clp.append(price)
        
        if symbol=='U$S':
            price_str = price.string
            price_str_split = price_str.split('.')
            if len(price_str_split)==1:
                price = (int(price_str_split[0]))*clp_usd_today
                price_clp.append(price)
            if len(price_str_split)==2:
                price = (int(price_str_split[0])*1000 + int(price_str_split[1]))*clp_usd_today
                price_clp.append(price)
        
        if symbol=='UF':
            if price is not None:
                price_str = price.string
                price_str_split = price_str.split('.')
                if len(price_str_split)==2:
                    price = (int(price_str_split[0])*1000 + int(price_str_split[1]))*uf_today
                    price_clp.append(price)
                if len(price_str_split)==1:
                    price = int(price_str)*uf_today
                    price_clp.append(price)
            else:
                uf_str = uf.string
                uf_str_split = uf_str.split(',')
                price = (int(uf_str_split[0]) + int(uf_str_split[1]) / 100)*uf_today
                price_clp.append(price)
   

        item_address = item.find('span', class_="main-title").string
        address.append(item_address)
    
    df = pd.DataFrame(np.column_stack([price_clp, area, rooms, bathrooms, address]), 
                  columns=['price_clp', 'area', 'rooms', 'bathrooms', 'address'])

    if df['area'].isnull().any():
        df.dropna(inplace=True)
        df.reset_index(inplace=True, drop=True)
        
    df['area'] = df['area'].astype(int)
    df['rooms'] = df['rooms'].astype(int)
    df['bathrooms'] = df['bathrooms'].astype(int)
    df['price_clp'] = round(df['price_clp'].astype(float), 0)   
    return df


# Define function to create a dataframe containig all the extracted data
def create_main_df(soup_list):
    
    df_list = []
    for soup in soup_list:
        df = extract_data_from_soup(soup)
        df_list.append(df)  
        
    main_df = pd.concat(df_list, ignore_index=True)    
    return main_df
