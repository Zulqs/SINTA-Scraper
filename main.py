import pandas as pd
import numpy as np
import gspread, os, time, traceback
from datetime import datetime as dt
import storageSinta as st
from fungsiScrape import *
from dataclasses import dataclass, field
from typing import List
os.system('cls')
#Koneksi & Up Gsheet
gc = gspread.oauth()
sh = gc.open("SINTA Sheet")
worksheet = sh.worksheet('DosenSV')
worksheet2 = sh.worksheet('IndikatorKerja')
worksheet3 = sh.worksheet('Lampiran_IndikatorKerja')

sintaRange = st.sintaRange()

@dataclass
class dcProfile:
    name : str
    prodi : str
    ID : str

@dataclass
class dcScore:
    sintaAll : str
    sinta3yr : str
    affilAll : str
    affil3yr : str

#Index iterate for sheet
def iterIndex():
    shIndex = []
    scopus = []
    scholar = []
    wos = []
    for i in range(len(metaIndexs)):
        scopus.append(metaIndexs[i][1])
        scholar.append(metaIndexs[i][2])
        wos.append(metaIndexs[i][3])
    for i in scopus:
        shIndex.append(i)
    for i in scholar:
        shIndex.append(i)
    for i in wos:
        shIndex.append(i)
    return shIndex

tahun = datetime.datetime.today().year
datTahun = list(range(tahun, tahun -5, -1))

bigDataset = []
loadingNum = 1
loadUntil = len(sintaRange)
errorCount = 0
errorLog = []
#Sheet DosenSV
nomorIndikatorKerja = 0
bigDatasetIndikatorKerja = []
bigDatasetLampiran = []
for sintaID in sintaRange:
    startTime = time.time()
    sintaID = str(sintaID)
    nomorIndikatorKerja += 1
    metaProfiles = metaProfile(sintaID)
    profile = dcProfile(name=metaProfiles[0],prodi=metaProfiles[1],ID=metaProfiles[2])
    print('Ekstrak [{}/{}]. Nama Dosen: {}'.format(loadingNum,loadUntil,profile.name))
    try:
        metaScores = metaScore(sintaID)
        metaIndexs = metaIndex(sintaID)
        metaScopuss = metaScopus(sintaID)
        metaScholars = metaScholar(sintaID)
        metaResearchs =  metaResearch(sintaID)
        metaServicess = metaServices(sintaID)
        metaIprss = metaIprs(sintaID)
        metaBookss = metaBooks(sintaID)
    except:
        print('|_________________> Error pada proses Dosen: {}'.format(profile.name))
        print('                  \______> Sinta Id: {}'.format(profile.ID))
        errorCount += 1
        errorLog.append([loadingNum,profile.ID])
        traceback.print_exc()

    score = dcScore(sintaAll=metaScores[0][1],sinta3yr=metaScores[1][1],affilAll=metaScores[2][1],affil3yr=metaScores[3][1])

    def checklenList(values,indexKe):
        try:
            values[indexKe]
            return True
        except IndexError:
            return False
    skipCell = ['',] * 25
    skipLite = ['',]
    listDataset = []
    def datasetItera():
        lenMax = [len(metaScopuss[0]),len(metaScholars[0]),len(metaResearchs),len(metaServicess),len(metaIprss),len(metaBookss)]
        lenMax = max(lenMax)
        nomor = 1
        for i in range(lenMax):
            tempDataset = []
            numbering = [str(nomor)]
            if nomor != 1: 
                tempDataset.extend(skipCell)
            if checklenList(metaScopuss[0],i): 
                setScopus = metaScopuss[0][i]
                numScopus = numbering
            else: 
                setScopus = skipLite*4
                numScopus = ['',]

            if checklenList(metaScholars[0],i): 
                setScholar = metaScholars[0][i]
                numScholar = numbering
            else: 
                setScholar = skipLite*4
                numScholar = ['',]

            if checklenList(metaResearchs,i): 
                setResearch = metaResearchs[i]
                numResearch = numbering
            else: 
                setResearch = skipLite*7
                numResearch = ['',]

            if checklenList(metaServicess,i): 
                setServices = metaServicess[i]
                numServices = numbering
            else: 
                setServices = skipLite*6
                numServices = ['',]

            if checklenList(metaIprss,i): 
                setIprs = metaIprss[i]
                numIprs = numbering
            else: 
                setIprs = skipLite*6
                numIprs = ['',]

            if checklenList(metaBookss,i): 
                setBooks = metaBookss[i]
                numBooks = numbering
            else: 
                setBooks = skipLite*7
                numBooks = ['',]

            tempDataset.extend(numScopus+setScopus+numScholar+setScholar+numResearch+setResearch+numServices+setServices+numIprs+setIprs+numBooks+setBooks)
            nomor += 1
            listDataset.append(tempDataset)
    datasetItera()

    shIndex = iterIndex()
    shProfile = [profile.prodi,profile.name,profile.ID,]
    shProfile1 = ['',profile.name,profile.prodi]
    shScore = [score.sintaAll,score.sinta3yr,score.affilAll,score.affil3yr]
    shHeader = [['Profile','','',
                'Scopus Index','','','','','',
                'Scholar Index','','','','','',
                'WOS Index','','','','','',
                'Score','','','',

                'Article Scopus',      '','','','', #4 Skip
                'Article Scholar',     '','','','',
                'Research',            '','','','','','','', #7 Skip
                'Community Services',  '','','','','','', #6 Skip
                'IPRs',                '','','','','','',
                'Books',               '','','','','','','',
                ],
                
                ['Program Studi','Nama Dosen','Sinta ID',
                'Article','Citation','Cited Document','H-Index','i10-Index','G-Index', # Scopus Index
                'Article','Citation','Cited Document','H-Index','i10-Index','G-Index', # Scholar Index
                'Article','Citation','Cited Document','H-Index','i10-Index','G-Index', # WOS Index
                'SINTA Score Overall','SINTA Score 3Yr','Affil Score','Affil Score 3Yr', #Score

                'No.','Tahun','Judul','Publikasi','Quartil', #Article Scopus
                'No.','Tahun','Judul','Publikasi','Quartil', #Article Scholar
                'No.','Tahun','Judul','Leader','Personils','Publikasi','Dana','Sumber', #Research
                'No.','Tahun','Judul','Leader','Personils','Publikasi','Dana', # Community Service
                'No.','Tahun','Judul','Inventor','Publikasi','Nomor Permohonan','Tipe', #IPRs
                'No.','Tahun','Judul','Kategori','Penerbit','Publikasi','Kota','Tipe', #Books
                ]]
    shHeaderIndikatorKerja = [['No',
                               'Nama Dosen',
                               'Prodi',
                               'Jumlah Publikasi Akreditasi Scopus',        '','','','',
                               'Jumlah Publikasi Non-Scopus',               '','','','',
                               'Jumlah Publikasi Scholar Sinta (S1-S4)',    '','','','',
                               ],
                               ['','','',
                               str(datTahun[0]),str(datTahun[1]),str(datTahun[2]),str(datTahun[3]),str(datTahun[4]),
                               str(datTahun[0]),str(datTahun[1]),str(datTahun[2]),str(datTahun[3]),str(datTahun[4]),
                               str(datTahun[0]),str(datTahun[1]),str(datTahun[2]),str(datTahun[3]),str(datTahun[4]),
                               ]]
    shHeaderLampiranIndikatorKerja = [['No',
                                        'Nama Dosen',
                                        'Prodi',
                                        'Tahun',
                                        'Judul',
                                        'Publikasi',
                                        'Quartil',
                                        ]]
    
    shIndikatorKerja = metaScopuss[1]+metaScholars[1]
    for i in metaScopuss[2]:
        tempLampiran = [shProfile1+i]
        bigDatasetLampiran.extend(tempLampiran)
    for i in metaScholars[2]:
        tempLampiran = [shProfile1+i]
        bigDatasetLampiran.extend(tempLampiran)
    try:
        dataFix = [shProfile+shIndex+shScore+listDataset[0]]+listDataset[1:]
    except IndexError:
        dataFix = [shProfile+shIndex+shScore+listDataset]

    bigDataset.extend(dataFix)
    datasetFixIndikatorKerja = [shProfile1+shIndikatorKerja]
    bigDatasetIndikatorKerja.extend(datasetFixIndikatorKerja)
    elapsed = time.time() - startTime
    formatTime = dt.strftime(dt.utcfromtimestamp(elapsed),'%H:%M:%S')
    print(f'|_________________> Selesai dalam {formatTime}! ')
    loadingNum += 1

subbigDataset = [sublist for sublist in bigDataset]
worksheet.clear()
worksheet2.clear()
worksheet3.clear()

#Worksheet DosenSV
worksheet.update('A1',shHeader)
worksheet.update('A1',shHeader)
worksheet.update('A3',subbigDataset)

#Worksheet IndikatorKerja
worksheet2.update('A1',shHeaderIndikatorKerja)
worksheet2.update('A3',bigDatasetIndikatorKerja)

#Worksheet Lampiran_IndikatorKerja
worksheet3.update('A1',shHeaderLampiranIndikatorKerja)
worksheet3.update('A2',bigDatasetLampiran)
if errorCount == 0:
    print('Selesai! Tidak ada error.')
else:
    print('Selesai! Total Error: {}'.format(errorCount))
    print('Error Log: {}'.format(errorLog))