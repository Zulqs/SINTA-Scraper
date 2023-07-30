import pandas as pd
import numpy as np
import df2gspread as d2g
import os, requests, gspread, datetime, traceback, re, unicodedata, time
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from dataclasses import dataclass

load_dotenv()
##################Login########################
login_url= 'https://sinta.kemdikbud.go.id/logins/do_login'
username = os.getenv('USER')
password = os.getenv('PASSWORD')
payload = {
    'username': username,
    'password': password
}
session = requests.session()
response = session.post(login_url, data=payload)
#################Login#######################
requestItera = 0
if response.status_code == 200:
    def remover(public):
        cleaned_string = unicodedata.normalize('NFKD', public)
        cleaned_string = re.sub("\(.*?\)","()", cleaned_string)
        cleaned_string = re.sub(r'[0-9!@#$%^*(),.?":{}|<>-]', '', cleaned_string)
        cleaned_string = cleaned_string.replace('Vol', '').strip()
        cleaned_string = re.sub(r'\\.*', '', cleaned_string)
        return cleaned_string
    
    def webURL(addUrl=""):
        # global requestItera
        web = "https://sinta.kemdikbud.go.id/"+addUrl
        response = session.get(web)
        response_text = response.text
        soup = BeautifulSoup(response_text, 'html.parser')
        # requestItera += 1
        # print(requestItera)
        return soup

    #List meta profile
    def metaProfile(sintaID):
        list_dosen = []
        soup = webURL('authors/profile/'+sintaID)
        name = soup.find('h3').find('a').text
        profile =  soup.find('div',{'class':'meta-profile'})
        profile = profile.text.split('\n')
        list_dosen.append(name)
        for data in profile:
            if data[0:3] == " D4" or data[0:3] == " D3" or data[0:3] == " S1" or data[0:3] == " S2" or data[0:3] == " S3":
                list_dosen.append(data[1:])
            elif data[0:6] == " SINTA":
                splitID = data.split()
                list_dosen.append(splitID[3])
            elif data == 'Unknown' or data == ' Unknown':
                list_dosen.append('Tidak Diketahui')
        return list_dosen

    #List meta SINTA score
    def metaScore(sintaID):
        list_score = []
        soup = webURL('authors/profile/'+sintaID)
        for data in soup.find_all('div',{'class':'col-4'}):
            pr_num = data.find('div', {'class': 'pr-num'}).text
            pr_txt = data.find('div', {'class': 'pr-txt'}).text
            list_score.append((pr_txt, pr_num))
        return list_score

    #List meta Index
    def metaIndex(sintaID):
        list_sum = []
        itera = 0
        soup = webURL('authors/profile/'+sintaID)
        for data in soup.find_all('tr'): #Parsing data tbody
            list_temp = []
            if itera != 0:
                for i in data:
                    if i == '\n': pass
                    else: list_temp.append(i.text)
                list_sum.append(list_temp)
            else: itera = 1
        return list_sum
    
    #Data meta artikel scopus
    def metaScopus(sintaID):
        list_artikel5 = []
        list_judulIndikatorSCPS = []
        sumTahun1 = 0
        sumTahun2 = 0
        sumTahun3 = 0
        sumTahun4 = 0
        sumTahun5 = 0
        sumTahunn1 = 0
        sumTahunn2 = 0
        sumTahunn3 = 0
        sumTahunn4 = 0
        sumTahunn5 = 0
        soup = webURL('authors/profile/'+sintaID)
        tahun = datetime.datetime.today().year
        tahun5 = list(range(tahun, tahun -5, -1))
        try:
            pageMax = soup.find('div',{'class':'pagination-text'}).text.split()[3]
            for page in range(1,int(pageMax)+1):
                website_url = 'authors/profile/'+sintaID+'?page='+str(page)+'&view=scopus'
                soupPage = webURL(website_url)
                for data in soupPage.find_all('div',{'class':'ar-list-item'}):
                    dataTahun = data.find('a',{'class':'ar-year'}).text
                    judulArti = data.find('div',{'class':'ar-title'}).find('a').text
                    dataQuart = data.find('a',{'class':'ar-quartile'}).text
                    dataPub = data.find('a',{'class':'ar-pub'}).text
                    if int(dataTahun) in tahun5: #Cek apakah artikel ada dalam range 5 tahun terakhir
                        list_artikel5.append([dataTahun,judulArti,dataPub,dataQuart])
                        list_judulIndikatorSCPS.append([dataTahun,judulArti,dataPub,dataQuart])
                    if dataQuart[1:3] != 'no':
                        if dataTahun == ' 2023':
                            #print('test1')
                            sumTahun1 += 1
                        elif dataTahun == ' 2022':
                            #print('test1')
                            sumTahun2 += 1
                        elif dataTahun == ' 2021':
                            #print('test2')
                            sumTahun3 += 1
                        elif dataTahun == ' 2020':
                            #print('test3')
                            sumTahun4 += 1
                        elif dataTahun == ' 2019':
                            #print('test4')
                            sumTahun5 += 1
                    else:
                        if dataTahun == ' 2023':
                            #print('test1')
                            sumTahunn1 += 1
                        elif dataTahun == ' 2022':
                            #print('test1')
                            sumTahunn2 += 1
                        elif dataTahun == ' 2021':
                            #print('test2')
                            sumTahunn3 += 1
                        elif dataTahun == ' 2020':
                            #print('test3')
                            sumTahunn4 += 1
                        elif dataTahun == ' 2019':
                            #print('test4')
                            sumTahunn5 += 1
        except AttributeError:
            pass
        listJumlah = [sumTahun1,sumTahun2,sumTahun3,sumTahun4,sumTahun5,sumTahunn1,sumTahunn2,sumTahunn3,sumTahunn4,sumTahunn5]
        return list_artikel5,listJumlah,list_judulIndikatorSCPS
    
    #Data meta artikel scholar
    def metaScholar(sintaID):
        soup = webURL('authors/profile/'+sintaID+'/?view=googlescholar')
        list_artikel5 = []
        list_judulIndikator = []
        sumTahun1 = 0
        sumTahun2 = 0
        sumTahun3 = 0
        sumTahun4 = 0
        sumTahun5 = 0
        tahun = datetime.datetime.today().year
        tahun5 = list(range(tahun, tahun -5, -1))
        try:
            pageMax = soup.find('div',{'class':'pagination-text'}).text.split()[3]
            for page in range(1,int(pageMax)+1):
                    website_url = 'authors/profile/'+sintaID+'?page='+str(page)+'&view=googlescholar'
                    soupPage = webURL(website_url)
                    dataPage = soupPage.find_all('div',{'class':'ar-list-item'})
                    for indexing,data in enumerate(dataPage):
                        dataTahun = data.find('a',{'class':'ar-year'}).text
                        judulArti = data.find('div',{'class':'ar-title'}).find('a').text
                        dataPubli = data.find('a',{'class':'ar-pub'}).text
                        if dataPubli == '':
                            dataQuart = 'Tidak ada data publikasi pada SINTA'
                        else:
                            dataQuart = remover(dataPubli)
                            dataQuart = cekAkreditasi(dataQuart)

                        if int(dataTahun) in tahun5: #Cek apakah artikel ada dalam range 5 tahun terakhir
                            list_artikel5.append([dataTahun,judulArti,dataPubli,dataQuart])
                            #print(cacheJudul)
                            # print('Info 1: ',remover(dataPubli),dataQuart,dataTahun)
                            if dataQuart[0:3] == ' S1' or dataQuart[0:3] == ' S2' or dataQuart[0:3] == ' S3' or dataQuart[0:3] == ' S4':
                                list_judulIndikator.append([dataTahun,judulArti,dataPubli,dataQuart])
                                # print(dataQuart)
                                # print(dataTahun)
                                if dataTahun == ' 2023':
                                    #print('test1')
                                    sumTahun1 += 1
                                elif dataTahun == ' 2022':
                                    #print('test1')
                                    sumTahun2 += 1
                                elif dataTahun == ' 2021':
                                    #print('test2')
                                    sumTahun3 += 1
                                elif dataTahun == ' 2020':
                                    #print('test3')
                                    sumTahun4 += 1
                                elif dataTahun == ' 2019':
                                    #print('test4')
                                    sumTahun5 += 1
        except AttributeError:
            print("Some Error at metaScholar")
        listJumlah = [sumTahun1,sumTahun2,sumTahun3,sumTahun4,sumTahun5]
        return list_artikel5,listJumlah,list_judulIndikator


    #Data meta research
    def metaResearch(sintaID):
        soup = webURL('authors/profile/'+sintaID+'/?view=researches')
        list_researches = []
        tahun = datetime.datetime.today().year
        tahun5 = list(range(tahun, tahun -5, -1))
        try:
            pageMax =  soup.find('div',{'class':'pagination-text'}).text.split()[3]
            for page in range(1,int(pageMax)+1):
                website_url = 'authors/profile/'+sintaID+'/?page='+str(page)+'&view=researches'
                soupPage = webURL(website_url)
                for data in soupPage.find_all('div',{'class':'ar-list-item'}):
                    dataTahun = data.find('a',{'class':'ar-year'}).text
                    if int(dataTahun) in tahun5:
                        judulArti = data.find('div',{'class':'ar-title'}).find('a').text
                        dataPubli = data.find('a',{'class':'ar-pub'}).text
                        dataLead = data.find('div',{'class':'ar-meta'}).find('a').text
                        dataPers = data.find('div',{'class':'ar-meta'}).findNext('div',{'class':'ar-meta'})
                        dataDana = data.find('a',{'class':'ar-quartile'}).text
                        iterate = 0
                        list_pers = []
                        for i in dataPers.find_all('a'):
                            if iterate == 0:
                                iterate += 1
                            else: list_pers.append(i.text)
                        try:
                            dataSource = data.find('a',{'class':'ar-quartile text-info'}).text
                        except AttributeError:
                            dataSource = "Tidak ada sumber"
                        joined_list_pers = ', '.join(list_pers)
                        list_researches.append([dataTahun,judulArti,dataLead[9:],joined_list_pers,dataPubli,dataDana,dataSource])
        except AttributeError:
            pass
        return list_researches
    
    #Data meta services
    def metaServices(sintaID):
        soup = webURL('authors/profile/'+sintaID+'/?view=services')
        list_services = []
        tahun = datetime.datetime.today().year
        tahun5 = list(range(tahun, tahun -5, -1))
        try:
            pageMax =  soup.find('div',{'class':'pagination-text'}).text.split()[3]
            for page in range(1,int(pageMax)+1):
                website_url = 'authors/profile/'+sintaID+'/?page='+str(page)+'&view=services'
                soupPage = webURL(website_url)
                for data in soupPage.find_all('div',{'class':'ar-list-item'}):
                    dataTahun = data.find('a',{'class':'ar-year'}).text
                    if int(dataTahun) in tahun5:
                        judulArti = data.find('div',{'class':'ar-title'}).find('a').text
                        dataPubli = data.find('a',{'class':'ar-pub'}).text
                        dataLead = data.find('div',{'class':'ar-meta'}).find('a').text
                        dataPers = data.find('div',{'class':'ar-meta'}).findNext('div',{'class':'ar-meta'})
                        dataDana = data.find('a',{'class':'ar-quartile'}).text
                        iterate = 0
                        list_pers = []
                        for i in dataPers.find_all('a'):
                            if iterate == 0:
                                iterate += 1
                            else: list_pers.append(i.text)
                        joined_list_pers = ', '.join(list_pers)
                        list_services.append([dataTahun,judulArti,dataLead[9:],joined_list_pers,dataPubli,dataDana])
        except AttributeError:
            pass
        return list_services
    
    #Data meta iprs
    def metaIprs(sintaID):
        soup = webURL('authors/profile/'+sintaID+'/?view=iprs')
        list_iprs = []
        tahun = datetime.datetime.today().year
        tahun5 = list(range(tahun, tahun -5, -1))
        try:
            pageMax =  soup.find('div',{'class':'pagination-text'}).text.split()[3]
            for page in range(1,int(pageMax)+1):
                website_url = 'authors/profile/'+sintaID+'/?page='+str(page)+'&view=iprs'
                soupPage = webURL(website_url)
                for data in soupPage.find_all('div',{'class':'ar-list-item'}):
                    dataTahun = data.find('a',{'class':'ar-year'}).text
                    if int(dataTahun) in tahun5:
                        judulArti = data.find('div',{'class':'ar-title'}).find('a').text
                        dataInven = data.find('div',{'class':'ar-meta'}).find('a').text
                        dataPubli = data.find('a',{'class':'ar-pub'}).text
                        dataNomor = data.find('a',{'class':'ar-cited'}).text
                        dataTipe = data.find('a',{'class':'ar-quartile'}).text
                        list_iprs.append([dataTahun,judulArti,dataInven[11:],dataPubli,dataNomor[20:],dataTipe[1:]])
        except AttributeError:
            pass
        return list_iprs

    #Data meta books
    def metaBooks(sintaID):
        soup = webURL('authors/profile/'+sintaID+'/?view=books')
        list_books = []
        tahun = datetime.datetime.today().year
        tahun5 = list(range(tahun, tahun -5, -1))
        try:
            pageMax =  soup.find('div',{'class':'pagination-text'}).text.split()[3]
            for page in range(1,int(pageMax)+1):
                website_url = 'authors/profile/'+sintaID+'/?page='+str(page)+'&view=books'
                soupPage = webURL(website_url)
                for data in soupPage.find_all('div',{'class':'ar-list-item'}):
                    dataTahun = data.find('a',{'class':'ar-year'}).text
                    if int(dataTahun) in tahun5:
                        judulArti = data.find('div',{'class':'ar-title'}).find('a').text
                        dataKategori = data.find('div',{'class':'ar-meta'}).find('a').text
                        dataPers = data.find('div',{'class':'ar-meta'}).findNext('div').find('a').text
                        dataPubli = data.find('a',{'class':'ar-pub'}).text
                        dataKota = data.find('a',{'class':'ar-cited'}).text
                        dataTipe = data.find('a',{'class':'ar-quartile'}).text
                        list_books.append([dataTahun[1:],judulArti,dataKategori[11:],dataPers,dataPubli,dataKota[1:],dataTipe[1:]])
        except AttributeError:
            pass
        return list_books
    
    def cekAkreditasi(dataQuart):
        time.sleep(0.7)
        soup = webURL('journals/index/?q='+dataQuart)
        try:
            quartil = soup.find('span',{'class':'num-stat accredited'}).text
        except AttributeError:
            quartil = 'Tidak akreditasi SINTA'
        return quartil
        

elif response.status_code == 303:
    print("Login gagal")