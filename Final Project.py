#!/usr/bin/env python
# coding: utf-8

# In[13]:


from tkinter import *
#get method used
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.select import Select
#mask method used
import pandas as pd
from tkinter import ttk
#infection method used
from urllib.request import urlopen
import json
from urllib.parse import quote
from bs4 import BeautifulSoup

class Webpage():
    def __init__(self):
        pass
    def openbrowser(self):
        driverpath = 'C:/Users/User/Downloads/chromedriver_win32/chromedriver.exe'
        options = webdriver.ChromeOptions()
        options.add_argument('-headless')
        browser = webdriver.Chrome(executable_path = driverpath,options = options)
        return browser
    def getelements(self,url,element):
        browser = self.openbrowser()
        browser.get(url)
        html = browser.page_source
        bsObj = BeautifulSoup(html,'html.parser')
        places = bsObj.find_all(element)
        return places
class Window():
    def __init__(self, title, width, height):
        self.title = title
        self.width = width
        self.height = height
    def createpop(self, data):
        t1 = Toplevel()
        t1.title(self.title)
        screenwidth = t1.winfo_screenwidth()
        screenheight = t1.winfo_screenheight()
        t1.geometry("{}x{}+{}+{}".format(self.width, self.height, (screenwidth-self.width)//2, (screenheight-self.height)//2))
        canvas = Canvas(t1)
        yscroll = Scrollbar(t1, orient="vertical", command=canvas.yview)
        xscroll = Scrollbar(t1, orient="horizontal", command=canvas.xview)
        yscroll.pack(fill='y', side='right')
        xscroll.pack(fill='x', side='bottom')
        frame = Frame(canvas)
        for key,i in zip(data.keys(),range(len(data.keys()))):
            Label(frame, text = key).grid(row = 0, column = i, padx = 10, pady = 10)
            for element,j in zip(data[key],range(len(data[key]))):
                Label(frame, text = element).grid(row = j+1, column = i, padx = 10, pady = 10)
        canvas.create_window(0, 0, anchor='nw', window=frame)
        # make sure everything is displayed before configuring the scrollregion
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox('all'), yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)       
        canvas.pack(fill='both', expand=True, side='left')

#obtain all the city name in Taiwan from post office
def getcityandarea():
    browser = Webpage().openbrowser()
    url = 'https://www.post.gov.tw/post/internet/Postal/index.jsp?ID=208'
    browser.get(url)
    #select the city 
    cities = Select(browser.find_element_by_id('city_zip6'))
    allinfo = {}
    #for every city
    for option in cities.options:
        #choose the city
        cities.select_by_visible_text(option.text)
        #find the area
        areas =Select(browser.find_element_by_id('cityarea_zip6'))
        #exclude the default option
        if option.text != "???????????????":
            allinfo[option.text] = list()
            for area in areas.options:
                allinfo[option.text].append(area.text)
    return allinfo
#if city has been selected, get the area values
def bind(event):
    city = event.widget.get()
    data = getcityandarea()
    areas = []
    for i in data[city]:
        areas.append(i)
    areaselect['values'] = areas
#if ???????????? is pressed
def mask():
    #retrive the information about mask from government
    data = pd.read_csv('https://data.nhi.gov.tw/Datasets/Download.ashx?rid=A21030000I-D50001-001&l=https://data.nhi.gov.tw/resource/mask/maskdata.csv')
    df = pd.DataFrame(data)
    #rename the column names in case error occurs
    df.columns = ["??????????????????","??????????????????","??????????????????","??????????????????","?????????????????????","?????????????????????","??????????????????"]
    #drop redundant columns
    del df["??????????????????"]
    del df["??????????????????"]
    city = cityselect.get()
    area = areaselect.get()
    info = city+area          
    data = {}
    for columnname in df.columns.values.tolist():
        data[columnname] = list()
    alllist = df.values.tolist()
    ##get the corresponding data
    for i in range(len(df)):
        if info in df["??????????????????"][i]:
            for j, key in zip(alllist[i], data.keys()):
                data[key].append(j)
    t1 = Window("????????????",700,500)
    t1.createpop(data)

#????????????
def testplace():
    data = pd.read_excel('https://www.cdc.gov.tw//File/Get?q=alK1SUhIV6SOP0j4uU3aIxnRgFGtDZW-bebFr2ltQo7y9odQGJ4MJNGHQjWpoTMd8dXSEVXrmgaNbexFiD1i_GKq7oBFIy5sIXmxMwYGh2HbTnXXtOur3NRA42WlYVjAT5h3d8b27xE7H6UhaA1HhA', engine="odf")
    df = pd.DataFrame(data)
    del df["????????????"]
    city = cityselect.get()
    data = {}
    for columnname in df.columns.values.tolist():
        data[columnname] = list()
    alllist = df.values.tolist()
    ##get the corresponding data
    for i in range(len(df)):
        if city in df["??????"][i]:
            for j, key in zip(alllist[i], data.keys()):
                data[key].append(j)
    t1 = Window("????????????",300,600)
    t1.createpop(data)
    
#??????????????????
def vaccineplace():
    vaccine = Webpage()
    alldata = vaccine.getelements('https://tools.heho.com.tw/covid-19-vaccine/','td')
    info = cityselect.get()+areaselect.get()
    data = {}
    headers = ["????????????","????????????","????????????","??????"]
    for header in headers:
        data[header] = list()
    text = list()
    for td in alldata:
        text.append(td.text.strip().replace('??????',''))
    for i in range(len(text)):
        if info in text[i]:
            data["????????????"].append(text[i-3])
            data["????????????"].append(text[i-2])
            data["????????????"].append(text[i-1])
            data["??????"].append(text[i])
    t1 = Window("??????????????????",800,400)
    t1.createpop(data)

    
#covid-19 ????????????
#https://covid-19.nchc.org.tw/dt_005-covidTable_taiwan.php?downloadall=yes&language=en?downloadall=yes 
def infection():
    infection = {}
    headers = ["??????","??????????????????","??????????????????","??????????????????????????????"]
    for header in headers:
        infection[header] = list()
    city = cityselect.get()
    city = str(quote(city))
    url = 'https://covid-19.nchc.org.tw/api/covid19?CK=covid-19@nchc.org.tw&querydata=5003&limited='
    url += city
    html = urlopen(url).read()
    jsonObj = json.loads(html)
    for i in jsonObj:
        if i["a02"] == cityselect.get():
            if i["a03"] == areaselect.get():
                keys = ["a01","a04","a05","a06"]
                for key,j in zip(infection.keys(),keys):
                    infection[key].append(i[j])
    t1 = Window("????????????",450,400)
    t1.createpop(infection)

if __name__ == '__main__':          
    root = Tk()
    root.title("Covid-19 ???????????????")
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    width = 380
    height = 150
    root.geometry("{}x{}+{}+{}".format(width, height, (screenwidth-width)//2, (screenheight-height)//2))
    city_value = StringVar(value = "Select city")
    cities = []
    for i in getcityandarea().keys():
        cities.append(i)
    cityselect = ttk.Combobox(root,textvariable=city_value, width = 11)
    cityselect['values'] = cities
    #cityselect.current(0)
    cityselect.place(x = 80, y = 10)
    cityselect.bind("<<ComboboxSelected>>", bind)
    area_value = StringVar(value = "Select area")
    areaselect = ttk.Combobox(root,textvariable=area_value, width = 11)
    areaselect.place(x = 200, y = 10)
    texts = ["????????????????????????","??????????????????","????????????????????????","??????????????????"]
    commands = [mask,testplace,vaccineplace,infection]
    for text,func,i in zip(texts,commands,range(len(texts))):
        Button(root, text = text, height = 2, width = 13, relief = "raised", command = func).place(x = 80+ i%2 *120, y = 50+i//2*50)
    root.mainloop()


# In[ ]:




