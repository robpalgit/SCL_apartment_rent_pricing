from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np

def port_inmob_web_scraper(url):
    
    """

    The port_inmob_web_scraper function is designed to obtain basic information of apartments for rental published
    in a well known chilean properties website called "Portal Inmobiliario".


    Args:

        url(str): The url of the webpage from which the info will be obtained.


    Returns:

        df: A pandas dataframe containing the requested information of the apartments: rental price, area,
            number of rooms, number of bathrooms and address.
    
    """

    #Get code of the webpage to be scraped and save it as a text doc
    sauce = requests.get(url).text
    #Parse the text doc containig the webpage code
    soup = BeautifulSoup(sauce) 

    #Create empty lists to save the apartments data extracted from the webpage
    price_clp = []
    area = []
    rooms = []
    bathrooms = []
    address = []

    #Extract the price info from the "div.price__container" tag
    price_info = soup.find_all('div', class_="item__info-container")
    for item in price_info:
        
        symbol = item.find('span', class_="price__symbol").string        
        price = item.find('span', class_="price__fraction") 
        uf = item.find('span', class_="price__clf-full")

        #Prices can be expressed in chilean pesos ($), US dollars (US$) or
        #"Unidades de Fomento" (UF), which is a chilean tax unit
        #However, all prices will be converted to chilean pesos

        if symbol=='$':
            price_str = price.string
            price_str_split = price_str.split('.')
            if len(price_str_split)==2:
                price = (int(price_str_split[0])*1000 + int(price_str_split[1]))
                price_clp.append(price)
            if len(price_str_split)==3:
                price = (int(price_str_split[0])*1000000 + int(price_str_split[1])*1000 + int(price_str_split[2]))
                price_clp.append(price)
        
        if symbol=='U$S':
            price_str = price.string
            price_str_split = price_str.split('.')
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
    
        #Extract the apartment attributes like area, number of rooms and bathrooms
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
        
        if len(attrs_list)==1 or len(attrs_list)>3:
            item_area = None
            area.append(item_area)
            
            item_rooms = None
            rooms.append(item_rooms)
            
            item_bathrooms = None
            bathrooms.append(item_bathrooms)
        
        #Extract the apartment address
        item_address = item.find('span', class_="main-title").string
        address.append(item_address)
    
    #Create dataframe containing the obtained data of the apartments
    df = pd.DataFrame(np.column_stack([price_clp, area, rooms, bathrooms, address]), 
                  columns=['price_clp', 'area', 'rooms', 'bathrooms', 'address'])

    df['price_clp'] = round(df['price_clp'].astype(float), 0)
    
    if df['area'].isnull().any():
        df.dropna(inplace=True)
        df.reset_index(inplace=True, drop=True)
        
    df['area'] = df['area'].astype(int)
    df['rooms'] = df['rooms'].astype(int)
    df['bathrooms'] = df['bathrooms'].astype(int)
    
    return df
