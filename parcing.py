# -*- coding: utf-8 -*-

import requests                  #запросы
import re                        #Regular expression operations (регулярные выражения)
from bs4 import BeautifulSoup    #супчик
import pandas as pd              #работа с таблицами
import time                      #время
import math                      #для Пифагора

def html_stripper(text):
    return re.sub('<[^<]+?>', '', str(text))
    
#сначала пользовательские функции

#сколько комнат?
def getRoom(flat_page):
    rooms = flat_page.find('div', attrs={'class':'object_descr_title'})
    rooms = html_stripper(rooms)
    room_number = ''
    for i in re.split('-|\n', rooms):
        if 'комн' in i:
            break
        else:
            room_number += i
    room_number = "".join(room_number.split())
    return room_number

#извлечь цену
def getPrice(flat_page):
    price = flat_page.find('div', attrs={'class':'object_descr_price'})
    price = re.split('<div>|руб|\W', str(price))
    price = "".join([i for i in price if i.isdigit()][-3:])
    return int(price)


def getTotsp(flat_page):
    p = flat_page.find('div', attrs={'class':'clearfix'})
    p = re.split('Общая площадь|комнат', str(p))[1]
    p = re.split('</i>|\xa0м<sup>', str(p))[1]
    Totsp = p.replace(',', '.')
    return Totsp

def getLivsp(flat_page):
    p = flat_page.find('div', attrs={'class':'clearfix'})
    p = re.split('Жилая|кухни', str(p))[1]
    p = re.split('</i>|\xa0м<sup>', str(p))[1]
    Livesp = p.replace(',', '.')
    return Livesp
    
def getKitsp(flat_page):
    p = flat_page.find('div', attrs={'class':'clearfix'})
    p = re.split('кухни|сан', str(p))[1]
    p = re.split('</i>|\xa0м<sup>', str(p))[1]
    Kitsp = p.replace(',', '.')
    return Kitsp

    
#расстояние от центра
def getDist(flat_page):
    coords = flat_page.find('div', attrs={'class':'map_info_button_extend'}).contents[1]
    coords = re.split('&amp|center=|%2C', str(coords))
    coords_list = []
    for item in coords:
        if item[0].isdigit():
            coords_list.append(item)
    lat = float(coords_list[0])
    lon = float(coords_list[1])
    #нулевой киломтер Москвы
    Center_lat = 55.755817 
    Center_lon = 37.617633
    Dist = math.sqrt((lat - Center_lat)**2 + (lon- Center_lon)**2)
    return Dist
 
def getMetrDist(flat_page):
    p = flat_page.find('div', attrs={'class':'object_descr_metro'})
    p = re.split('comment', str(p))
    try:
        p = p[1]
        Metrdist = [i for i in p.split() if i.isdigit()]
    except: 
        Metrdist = 'N'
    return Metrdist
 
def getWalk(flat_page):
    p = flat_page.find('div', attrs={'class':'object_descr_metro'})
    p = re.split('comment', str(p))
    try:
        p = p[1]
        if re.search('пеш', p) is not None:
            Walk = 1
        else:
            Walk = 0
    except: 
        Walk = 0
    return Walk
    

def getBrick(flat_page):
    p = flat_page.find('div', attrs={'class':'clearfix'})
    p = re.split('дома|Высота', str(p))
    try:
        p = p[1]
        if re.search('кирп|монолит|жб', str(p)) is not None:
            Brick = 1
        else:
            Brick = 0
    except:
        Brick = 'N'
    return Brick
    
def getTel(flat_page):
    p = flat_page.find('div', attrs={'class':'clearfix'})
    p = re.split('Телефон:|Вид из окна', str(p))[1]
    if re.search('да|есть', str(p)) is not None:
            Tel = 1
    else:
            Tel = 0
    return Tel
 
def getBal(flat_page):
    p = flat_page.find('div', attrs={'class':'clearfix'})
    p = re.split('Балкон|Лифт', str(p))[1]
    if re.search('балк|лодж', str(p)) is not None:
            Bal = 1
    else:
            Bal = 0
    return Bal
    
def getFloor(flat_page):
    floor = flat_page.find('div', attrs={'class':'clearfix'})
    floor = re.split('Этаж|Тип', str(floor))
    floor = floor[1].split()
    floor = [i for i in floor if i.isdigit()]
    try :
        Floor = int(floor[0])
    except:
        Floor = 'N'
    return Floor
    
def getNfloors(flat_page):
    floor = flat_page.find('div', attrs={'class':'clearfix'})
    floor = re.split('Этаж|Тип', str(floor))
    floor = floor[1].split()
    floor = [i for i in floor if i.isdigit()]
    try:
        Nfloors = int(floor[1])
    except:
        Nfloors = 'N'
    return Nfloors
    
def getNew(flat_page):
    p = flat_page.find('div', attrs={'class':'clearfix'})
    p = re.split('дома|Высота', str(p))
    try:
        p = p[1]
        if re.search('втор', str(p)) is None:
            New = 1
        else:
            New = 0
    except:
        New = 'N'
    return New
    


def pars(flat_url):
    flat_page = requests.get(flat_url)
    flat_page = flat_page.content
    flat_page = BeautifulSoup(flat_page, 'lxml')	
    flatStats = {'District':0}
    flatStats['Totsq'] = getTotsq(flat_page)
    flatStats['Livesq'] = getLivesq(flat_page)
    flatStats['Kitsq'] = getKitsq(flat_page)
    flatStats['Price'] = getPrice(flat_page)
    flatStats['Rooms'] = getRoom(flat_page)
    flatStats['Bal'] = getBal(flat_page)
    flatStats['Floor'] = getFloor(flat_page)
    flatStats['NFloors'] = getNfloors(flat_page)
    flatStats['Metrdist'] = getMetrDist(flat_page)
    flatStats['Walk'] = getWalk(flat_page)
    flatStats['Brick'] = getBrick(flat_page)
    flatStats['Tel'] = getTel(flat_page)
    flatStats['New'] = getNew(flat_page)
    flatStats['Dist'] = getDist(flat_page)
    return flatStats['Rooms'], flatStats['Price'], flatStats['Totsp'], flatStats['Livesp'], flatStats['Kitsp'], flatStats['Dist'], flatStats['Metrdist'], flatStats['Walk']	, flatStats['Brick'], flatStats['Tel'], flatStats['Bal'], flatStats['Floor'], flatStats['Nfloors'], flatStats['New'], flatStats['url']
 

#12 округов, чтобы более-менее равномерно охватить Москву
districts=['','','','','','','','','','','','']

#ЦАО    
districts[0] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=13&district%5B1%5D=14&district%5B2%5D=15&district%5B3%5D=16&district%5B4%5D=17&district%5B5%5D=18&district%5B6%5D=19&district%5B7%5D=20&district%5B8%5D=21&district%5B9%5D=22&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'    
#САО
districts[1] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=23&district%5B10%5D=33&district%5B11%5D=34&district%5B12%5D=35&district%5B13%5D=36&district%5B14%5D=37&district%5B15%5D=38&district%5B1%5D=24&district%5B2%5D=25&district%5B3%5D=26&district%5B4%5D=27&district%5B5%5D=28&district%5B6%5D=29&district%5B7%5D=30&district%5B8%5D=31&district%5B9%5D=32&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#СВАО
districts[2] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=39&district%5B10%5D=49&district%5B11%5D=50&district%5B12%5D=51&district%5B13%5D=52&district%5B14%5D=53&district%5B15%5D=54&district%5B16%5D=55&district%5B1%5D=40&district%5B2%5D=41&district%5B3%5D=42&district%5B4%5D=43&district%5B5%5D=44&district%5B6%5D=45&district%5B7%5D=46&district%5B8%5D=47&district%5B9%5D=48&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#ВАО
districts[3] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=56&district%5B10%5D=66&district%5B11%5D=67&district%5B12%5D=68&district%5B13%5D=69&district%5B14%5D=70&district%5B15%5D=71&district%5B1%5D=57&district%5B2%5D=58&district%5B3%5D=59&district%5B4%5D=60&district%5B5%5D=61&district%5B6%5D=62&district%5B7%5D=63&district%5B8%5D=64&district%5B9%5D=65&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#ЮВАО
districts[4] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=72&district%5B10%5D=82&district%5B11%5D=83&district%5B1%5D=73&district%5B2%5D=74&district%5B3%5D=75&district%5B4%5D=76&district%5B5%5D=77&district%5B6%5D=78&district%5B7%5D=79&district%5B8%5D=80&district%5B9%5D=81&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#ЮАО
districts[5] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=84&district%5B10%5D=94&district%5B11%5D=95&district%5B12%5D=96&district%5B13%5D=97&district%5B14%5D=98&district%5B15%5D=99&district%5B1%5D=85&district%5B2%5D=86&district%5B3%5D=87&district%5B4%5D=88&district%5B5%5D=89&district%5B6%5D=90&district%5B7%5D=91&district%5B8%5D=92&district%5B9%5D=93&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#ЮЗАО
districts[6] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=100&district%5B10%5D=110&district%5B11%5D=111&district%5B1%5D=101&district%5B2%5D=102&district%5B3%5D=103&district%5B4%5D=104&district%5B5%5D=105&district%5B6%5D=106&district%5B7%5D=107&district%5B8%5D=108&district%5B9%5D=109&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#ЗАО
districts[7] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=112&district%5B10%5D=122&district%5B11%5D=123&district%5B12%5D=124&district%5B13%5D=348&district%5B14%5D=349&district%5B15%5D=350&district%5B1%5D=113&district%5B2%5D=114&district%5B3%5D=115&district%5B4%5D=116&district%5B5%5D=117&district%5B6%5D=118&district%5B7%5D=119&district%5B8%5D=120&district%5B9%5D=121&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#СЗАО
districts[8] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=125&district%5B1%5D=126&district%5B2%5D=127&district%5B3%5D=128&district%5B4%5D=129&district%5B5%5D=130&district%5B6%5D=131&district%5B7%5D=132&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#ЗЕЛАО
districts[9] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=152&district%5B1%5D=153&district%5B2%5D=154&district%5B3%5D=355&district%5B4%5D=356&district%5B5%5D=357&district%5B6%5D=358&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#НАО
districts[10] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=327&district%5B10%5D=337&district%5B1%5D=328&district%5B2%5D=329&district%5B3%5D=330&district%5B4%5D=331&district%5B5%5D=332&district%5B6%5D=333&district%5B7%5D=334&district%5B8%5D=335&district%5B9%5D=336&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
#ТАО
districts[11] = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=338&district%5B1%5D=339&district%5B2%5D=340&district%5B3%5D=341&district%5B4%5D=342&district%5B5%5D=343&district%5B6%5D=344&district%5B7%5D=345&district%5B8%5D=346&district%5B9%5D=347&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'

links = [] #массив ссылок на квартиры

#по 500 из каждого из 12
data_table = pd.DataFrame(np.random.randn(500*12, 15), columns=['Rooms','Price','Totsp','Livesp','Kitsp','Dist','MetrDist','Walk','Brick','Tel','Bal','Floor','Nfloors','New','URL'])



for i in range(0,12): #по округам
    for page in range(1, 30): #по страничкам
        page_url =  districts[i].format(page)
        search_page = requests.get(page_url)
        search_page = search_page.content
        search_page = BeautifulSoup(search_page, 'lxml')
        flat_urls = search_page.findAll('div', attrs = {'ng-class':"{'serp-item_removed': offer.remove.state, 'serp-item_popup-opened': isPopupOpen}"})
        flat_urls = re.split('http://www.cian.ru/sale/flat/|/" ng-class="', str(flat_urls))
        for link in flat_urls:
            if link.isdigit():
                links.append(link)
    
    for j in range(0,500):
        flat_url = 'http://www.cian.ru/sale/flat/' + str(links[j]) + '/'
        data_table.loc[j+i*500] = pars(flat_url)
    
data_table.to_csv("data.csv")


