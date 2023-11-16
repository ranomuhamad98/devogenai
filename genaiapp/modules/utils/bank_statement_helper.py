import os
import re
import time
import json
import pickle

import numpy as np
import pandas as pd
import requests as req

from google.cloud import vision
from pdf2image import convert_from_path

import google.auth
import google.auth.transport.requests

with open('cred.pickle', 'rb') as token:
    credentials = pickle.load(token)

credentials.refresh(google.auth.transport.requests.Request())
gcp_token = credentials._id_token

headers = {
    'Authorization': 'Bearer ' + gcp_token,
    'Content-Type': 'application/json'
}

#GLOBAL SECTION
monthData = ["Januari","Februari","Maret","April","Mei","Juni",
            "Juli","Agustus","September","Oktober","November","Desember"]

PREFIX = """
            You are working with a pandas dataframe in Python. The name of the dataframe is `df`.
            Rules:
                1. Do not give formula as an output, only give formula result / final result
                2. Format the final result as json
                3. The result must fill this JSON Value
                '
                        "Sum_Transaction":"",
                        "Count_Transaction":"",
        
                        "Cash_Witdrawal_Count":"",
                        "Cash_Witdrawal_Sum":"",
                        
                        "Pajak_Sum":"",
                        "Pajak_Count":"",
                        
                        "Biaya_Admin_Sum":"",
                        "Biaya_Admin_Count":"",
                        
                        "Sales_Sum":"",
                        "Sales_Count":"",
                        
                        "Deposit_Sum":"",
                        "Deposit_Count":"",
                        
                        "Debit_Sum":"",
                        "Debit_Count":"",
                        
                        "Credit_Sum":"",
                        "Credit_Count":""
                '
            You should use the tools below to answer the question posed of you:
"""

def prompt_template(date):
    return """
        1. TOTAL AMMOUNT WHERE BULAN_TAHUN = "{date}" as "Sum_Transaction"\n
        2. COUNT row WHERE BULAN_TAHUN = "{date}" as "Count_Transaction"\n
        3. TOTAL AMMOUNT WHERE BULAN_TAHUN = "{date}" and KETERANGAN contain "TARIKAN ATM" as "Cash_Witdrawal_Sum"\n
        4. COUNT row WHERE BULAN_TAHUN = "{date}" and KETERANGAN contain "TARIKAN ATM" as "Cash_Witdrawal_Count"
        5. TOTAL AMMOUNT WHERE BULAN_TAHUN = "{date}" and KETERANGAN contain "PAJAK BUNGA" as "Pajak_Sum"
        6. COUNT row WHERE BULAN_TAHUN = "{date}" and KETERANGAN contain "PAJAK BUNGA" as "Pajak_Count"
        7. TOTAL AMMOUNT WHERE BULAN_TAHUN = "{date}" and KETERANGAN contain "BIAYA ADM" as "Biaya_Admin_Sum"
        8. COUNT row WHERE BULAN_TAHUN = "{date}" and KETERANGAN contain "BIAYA ADM" as "Biaya_Admin_Count"
        9. TOTAL AMMOUNT WHERE BULAN_TAHUN = "{date}" and KETERANGAN contain "INV" as "Sales_Sum"
        10. COUNT row WHERE BULAN_TAHUN = "{date}" and KETERANGAN contain "INV" as "Sales_Count"
        11. TOTAL AMMOUNT WHERE BULAN_TAHUN = "{date}" and KETERANGAN contain "SETORAN TUNAI" as "Deposit_Sum"
        12. COUNT row WHERE BULAN_TAHUN = "{date}" and KETERANGAN contain "SETORAN TUNAI" as "Deposit_Count"
        13. TOTAL AMMOUNT WHERE BULAN_TAHUN = "{date}" AND STATUS = "DEBIT" as "Debit_Sum"
        14. COUNT row WHERE BULAN_TAHUN = "{date}" AND STATUS = "DEBIT" as "Debit_Count"
        15. TOTAL AMMOUNT WHERE BULAN_TAHUN = "{date}" AND STATUS = "CREDIT" as "Credit_Sum"
        16. COUNT row WHERE BULAN_TAHUN = "{date}" AND STATUS = "CREDIT" as "Credit_Count"
    """.format(date = date)

def jaccard_similarity(x,y):
    """ returns the jaccard similarity between two lists """
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    return intersection_cardinality/float(union_cardinality)

def detect_text(path):
    """Detects text in the file."""

    client = vision.ImageAnnotatorClient()
    
    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    texts = response.text_annotations

    confidence = []
    for p in response.full_text_annotation.pages:
        for b in p.blocks:
            for par in b.paragraphs:
                for w in par.words:
                    confidence.append(w.confidence)
    
    df_text = {
      "text":[],
      "y_pos":[],
      "x_pos":[]
    }
    x_pos = 1
    for i in range(1,len(texts)):
      # df_text['text'].append(texts[i].description+'_'+str("{:.5f}".format(confidence[i-1])))
      df_text['text'].append(texts[i].description)
      df_text['y_pos'].append([texts[i].bounding_poly.vertices[x].y for x in range(4)])
      df_text['x_pos'].append([texts[i].bounding_poly.vertices[x].x for x in range(4)])
    df_text = pd.DataFrame.from_dict(df_text)
    
    return df_text

def funcPosition(df,pos):
    start_i = 0
    end_i   = 1

    datacur = 0
    newdata = []

    for i in range(1,len(df)):
        data_before  = np.array(df.iloc[[i-1]][pos].values.tolist())
        data_current = np.array(df.iloc[[i]][pos].values.tolist())
        # print(np.array([np.abs(x.sum()) for x in data_current-data_before]))
        if np.array([np.abs(x.sum()) for x in data_current-data_before]) > 20:
            newdata.append(df.iloc[start_i:end_i])
            start_i = end_i
            end_i   = i
        if end_i != start_i:
            try:
                newdata[-1] = df.iloc[start_i:end_i]
            except:
                newdata.append(df.iloc[start_i:end_i])

    newdata.append(df.iloc[end_i:])
    return newdata

def bank_extraction(path_file,filter_trash,sufix_filter,extract_table,extract_detail):
    start = time.time()
    images = convert_from_path(path_file)
    
    prefix = ''
    sufix  = ''
    result_text = []
    
    for index,img in enumerate(images):
      img.save('image_save.png','PNG')
      df = detect_text('image_save.png')
      df = df.sort_values(by=['y_pos']).reset_index(drop=True)

      df_x_result = funcPosition(df,'y_pos')
      data_regex = ''
      for df_x in df_x_result:
        df_x = df_x.sort_values(by=['x_pos']).reset_index(drop=True)
        data_regex += ' '.join(df_x.text.values.tolist()).replace(' , ',',').replace(' . ','.').replace(' / ','/')+'\n'
        
      data_regex = re.sub(r"(\d\d)\.(\d\.\d\d)", r"\1.00 \2", data_regex)
      
      if prefix != '':
          data_regex = data_regex.replace(prefix,'')
    
      data_regex   = re.sub(filter_trash,'', data_regex)
      
      try:
          sufix_start  = re.findall(sufix_filter,data_regex)[0]
          sufix        = data_regex[data_regex.index(sufix_start):]
          data_regex   = data_regex.replace(sufix,'')
      except:
        pass
      
      r1           = re.findall(extract_table,data_regex)
      r1_position  = []
      for r in r1:
        r=r.replace('\\','\\\\')
        r=r.replace('+','\\+')
        try:
            dataIndexer = [indexer.start() for indexer in re.finditer(r, data_regex)]
            r1_position += dataIndexer
        except:
            pass
      
      r1_position = list(dict.fromkeys(r1_position))
      r1_position.sort()

      for i in range(len(r1_position)):
        try:
          result_text.append(data_regex[r1_position[i]:r1_position[i+1]])
        except:
          result_text.append(data_regex[r1_position[i]:])

        try:
            # print("data",result_text[-1])
            save_data = re.findall(extract_detail,result_text[-1])[0][0]

            result_text[-1] = [result_text[-1].replace(save_data,''),save_data]
            result_text[-1] = [rt.replace('\n',' ') for rt in result_text[-1]]
        except:
            pass
        
      if prefix == '':
        prefix       = data_regex[:r1_position[0]]
        
    end = time.time()
    print("Done",(end-start), "s")
    
    return prefix,result_text,sufix

def DataFrameExtraction(df,promt,prefix):
    url     = 'https://llm-processor-swgjfxtwwq-et.a.run.app/modelDataframe'
    # url     = 'http://127.0.0.1:5000/modelDataframe'

    data_trans = {
        "dataframe"       : df.copy().to_json(orient='records', lines=True),
        "question"        : promt,
        "prefix"          : prefix,
        "gcp_token"      : gcp_token
    }

    response = req.post(url, headers=headers, data=json.dumps(data_trans))
    response = json.loads(response.text)

    return response['result']

def Bank_Data_Ekstract(df):
    print(df)
    tanggal = df[['BULAN_TAHUN']].copy()
    tanggal['Year'] = tanggal['BULAN_TAHUN'].apply(lambda x:x.split(' ')[1])
    tanggal['Month'] = tanggal['BULAN_TAHUN'].apply(lambda x:monthData.index(x.split(' ')[0]))
    tanggal = tanggal.sort_values(by=['Year', 'Month'])
    tanggal = tanggal.drop(columns=['Year', 'Month'])

    BankAnalysis = []
    
    for my in tanggal.BULAN_TAHUN.unique():
        data = DataFrameExtraction(df,prompt_template(my),PREFIX)
        try:
            data = json.loads(data.replace("'",'"'))
            data['Mounth_Year'] = my
            BankAnalysis.append(data)
        except:
            pass

    df_data = pd.DataFrame(BankAnalysis)
    return df_data

#BCA SECTION
def BCA_Second_Check(text):
    new_text = []
    for i in text:
        if i in "1234567890.,DB ":
            new_text.append(i)
    return ''.join(new_text)

def BCA_table_spliting(df):
    #retrieving first row to get the year
    first_row = df[0].upper()
    year = ""
    for str in first_row.splitlines():
        if "PERIODE" in str:
            year = str.replace("PERIODE : ", "").split()[1]
       
    df = df[1]
    dtlist = {
        "INDEX":[],
        "BULAN_TAHUN":[],
        "TANGGAL":[],
        "KETERANGAN":[],
        "MUTASI":[],
        "SALDO":[],
        "CBG":[]
    }
    
    indexing = 0
    for er in df:
        try:
            stringnumdata = re.findall(r"(\d\d\/\d\d)\s+(.*)",er[0])[0]
            dtlist['INDEX'].append(indexing)
            indexing+=1
        except:
            continue
        
        data = BCA_Second_Check(er[1]).strip().split(' ')
        if '' in data:
            data.remove('')
        if 'DB' in data:
            index_db = data.index('DB')
            data[index_db-1]+=' '+data[index_db]
            data.remove('DB')
        if len(dtlist['SALDO'])==0:
            dtlist["CBG"].append("")
            dtlist["MUTASI"].append("")
            dtlist["SALDO"].append(data[0])
            dtlist['BULAN_TAHUN'].append("{0} {1}".format(monthData[int(stringnumdata[0].split('/')[1])-1], year))
            dtlist['KETERANGAN'].append(stringnumdata[1])
            dtlist['TANGGAL'].append(stringnumdata[0]+'/'+year)
            continue
        if len(data)==3:
            dtlist["CBG"].append(data[0])
            dtlist["MUTASI"].append(data[1])
            dtlist["SALDO"].append(data[2])
            dtlist['BULAN_TAHUN'].append("{0} {1}".format(monthData[int(stringnumdata[0].split('/')[1])-1], year))
            dtlist['KETERANGAN'].append(stringnumdata[1])
            dtlist['TANGGAL'].append(stringnumdata[0]+'/'+year)
        elif len(data)==2:
            if len(data[0])==4:
                dtlist["CBG"].append(data[0])
                dtlist["MUTASI"].append(data[1])
                dtlist["SALDO"].append("")
            else:
                dtlist["CBG"].append("")
                dtlist["MUTASI"].append(data[0])
                dtlist["SALDO"].append(data[1])
            dtlist['BULAN_TAHUN'].append("{0} {1}".format(monthData[int(stringnumdata[0].split('/')[1])-1], year))
            dtlist['KETERANGAN'].append(stringnumdata[1])
            dtlist['TANGGAL'].append(stringnumdata[0]+'/'+year)
        elif len(data)==1:
            dtlist["CBG"].append("")
            dtlist["MUTASI"].append(data[0])
            dtlist["SALDO"].append("")
            dtlist['BULAN_TAHUN'].append("{0} {1}".format(monthData[int(stringnumdata[0].split('/')[1])-1], year))
            dtlist['KETERANGAN'].append(stringnumdata[1])
            dtlist['TANGGAL'].append(stringnumdata[0]+'/'+year)

    # Table Cleanup
    # print(dtlist)
    df = pd.DataFrame.from_dict(dtlist)
    # df = df.drop(df[df['MUTASI'].str.contains('\d') == False].index[0])
    df['STATUS'] = ['DEBIT' if 'DB' in x else 'CREDIT' for x in df['MUTASI']]
    df['AMMOUNT'] = df['MUTASI'].str.replace('DB', '').str.replace('.00', '').str.replace('D', '').str.replace(',', '').str.replace(' ', '').str.replace('.', '').replace('', np.nan).astype(float)
    df['AMMOUNT'] = df['AMMOUNT'].apply(lambda x:x)
    df['SALDO'] = df['SALDO'].apply(lambda x: x.strip()).str.replace('D', '').replace('', np.nan)
    df['SALDO'] = df['SALDO'].str.replace('.00', '').str.replace(',', '').str.replace('.', '').str.replace(' ', '').astype(float)
    df['SALDO'] = df['SALDO'].apply(lambda x:x/100)
    
    return df[["INDEX","TANGGAL","BULAN_TAHUN", "KETERANGAN", "STATUS", "AMMOUNT", "SALDO"]]

def BCA_table_spliting_Demo(df):
    #retrieving first row to get the year
    first_row = df[0].upper()
    year = ""
    for str in first_row.splitlines():
        if "PERIODE" in str:
            year = str.replace("PERIODE : ", "").split()[1]
       
    df = df[1]
    dtlist = {
        "TANGGAL":[],
        "BULAN_TAHUN":[],
        "KETERANGAN":[],
        "CBG":[],
        "MUTASI":[],
        "SALDO":[]
    }
    for er in df:
        try:
            stringnumdata = re.findall(r"(\d\d\/\d\d)\s+(.*)",er[0])[0]
        except:
            continue
        
        data = BCA_Second_Check(er[1]).strip().split(' ')
        if '' in data:
            data.remove('')
        if 'DB' in data:
            index_db = data.index('DB')
            data[index_db-1]+=' '+data[index_db]
            data.remove('DB')
        if len(dtlist['SALDO'])==0:
            dtlist["CBG"].append("")
            dtlist["MUTASI"].append("")
            dtlist["SALDO"].append(data[0])
            dtlist['BULAN_TAHUN'].append("{0} {1}".format(monthData[int(stringnumdata[0].split('/')[1])-1], year))
            dtlist['KETERANGAN'].append(stringnumdata[1])
            dtlist['TANGGAL'].append(stringnumdata[0]+'/'+year)
            continue
        if len(data)==3:
            dtlist["CBG"].append(data[0])
            dtlist["MUTASI"].append(data[1])
            dtlist["SALDO"].append(data[2])
            dtlist['BULAN_TAHUN'].append("{0} {1}".format(monthData[int(stringnumdata[0].split('/')[1])-1], year))
            dtlist['KETERANGAN'].append(stringnumdata[1])
            dtlist['TANGGAL'].append(stringnumdata[0]+'/'+year)
        elif len(data)==2:
            if len(data[0])==4:
                dtlist["CBG"].append(data[0])
                dtlist["MUTASI"].append(data[1])
                dtlist["SALDO"].append("")
            else:
                dtlist["CBG"].append("")
                dtlist["MUTASI"].append(data[0])
                dtlist["SALDO"].append(data[1])
            dtlist['BULAN_TAHUN'].append("{0} {1}".format(monthData[int(stringnumdata[0].split('/')[1])-1], year))
            dtlist['KETERANGAN'].append(stringnumdata[1])
            dtlist['TANGGAL'].append(stringnumdata[0]+'/'+year)
        elif len(data)==1:
            dtlist["CBG"].append("")
            dtlist["MUTASI"].append(data[0])
            dtlist["SALDO"].append("")
            dtlist['BULAN_TAHUN'].append("{0} {1}".format(monthData[int(stringnumdata[0].split('/')[1])-1], year))
            dtlist['KETERANGAN'].append(stringnumdata[1])
            dtlist['TANGGAL'].append(stringnumdata[0]+'/'+year)

    # Table Cleanup
    # print(dtlist)
    df = pd.DataFrame.from_dict(dtlist)
    # df = df.drop(df[df['MUTASI'].str.contains('\d') == False].index[0])
    df['STATUS'] = ['DEBIT' if 'DB' in x else 'CREDIT' for x in df['MUTASI']]
    df['AMMOUNT'] = df['MUTASI'].str.replace('DB', '').str.replace('D', '').str.replace(',', '').str.replace(' ', '').str.replace('.', '').replace('', np.nan).astype(float)
    df['AMMOUNT'] = df['AMMOUNT'].apply(lambda x:x/100)
    df['SALDO'] = df['SALDO'].apply(lambda x: x.strip()).str.replace('D', '').replace('', np.nan)
    df['SALDO'] = df['SALDO'].str.replace(',', '').str.replace('.', '').str.replace(' ', '').astype(float)
    df['SALDO'] = df['SALDO'].apply(lambda x:x/100)
    
    return df[["TANGGAL","BULAN_TAHUN", "KETERANGAN", "STATUS", "AMMOUNT", "SALDO"]]

def BCA_extraction(folderBCA):
    data_extract = {
        "prefix":[],
        "transaction":[],
        "transaction2":[],
        "sufix":[]
    }
    for data_file in os.listdir(folderBCA):
        if 'pdf' in data_file:
            extraction_result = bank_extraction(folderBCA+'/'+data_file,filter_trash = 'Bersambung ke Halaman berikut',sufix_filter = '\\nSALDO\s+AWAL',extract_table = "\n\d\d\/\d\d.*",extract_detail = "(((\s\d\d\d\d\s)*(([\d\.,]{4,}\.\d\d).{0,4}))([\d\.,]{4,}\.\d\d)*)")
            data_extract["prefix"].append(extraction_result[0])
            data_extract["sufix"].append(extraction_result[2])
            data_extract["transaction"].append(BCA_table_spliting(extraction_result))
            data_extract["transaction2"].append(BCA_table_spliting_Demo(extraction_result))
    
    data_extract = pd.DataFrame.from_dict(data_extract) #Next Will Use For Multiple Bank Account

    prefix = extraction_result[0].replace('\n',' ')
    sufix = extraction_result[2].replace('\n',' ')
    Transaction_data = pd.concat(data_extract["transaction"].values.tolist()).reset_index(drop=True).sort_values(by=['TANGGAL'])
    Transaction_data2 = pd.concat(data_extract["transaction2"].values.tolist()).reset_index(drop=True)

    url     = 'https://llm-processor-swgjfxtwwq-et.a.run.app/modelBertIndo'

    data = {
        "context"       : extraction_result[0].replace('\n',' ')
    }

    PrefixExtract = []
    for query in ["Nama Bank adalah","Account Number adalah","Nama Account Holder adalah"]:
        data['query'] = query
        print(data)
        response = req.post(url, headers=headers, data=json.dumps(data))
        print(response)
        response = json.loads(response.text)
        PrefixExtract.append(response['result'])

    print(Transaction_data)

    outputResult={
        "Bank_Name":PrefixExtract[0],
        "Account_Number":PrefixExtract[1],
        "Account_Holder":PrefixExtract[2],
        "Transaction_Analysis":Bank_Data_Ekstract(Transaction_data.copy())
    }
        
    return outputResult,prefix,Transaction_data,Transaction_data2,sufix

#BRI SECTION
def BRI_table_spliting(df):
    valBefore = float(re.findall(r"\d[\d\.,]+\d\d",df[2])[0].replace(",",""))

    df = df[1]
    print(df[-1])
    dtlist = {
        "TANGGAL":[],
        "KETERANGAN":[],
        "STATUS":[],
        "AMMOUNT":[],
        "SALDO":[]
    }
    for er in df:
        print(er)
        data = re.findall(r"(\d\d\/\d\d\/\d\d)\s+(\d\d:\d\d:\d\d)\s+(.*)",er[0])[0]
        bulan,tahun = data[0].split('/')[1:]
        bulan       = monthData[int(bulan)-1]
        
        dtlist['TANGGAL'].append(bulan+' 20'+tahun)
        dtlist['KETERANGAN'].append(data[2])
    
        data = er[1].strip().split(' ')
        
        current = 0 
        if float(data[0].replace(',','')) == 0:
            dtlist['STATUS'].append('CREDIT')
            current = float(data[1].replace(',',''))
            valBefore += current
        else:
            dtlist['STATUS'].append('DEBIT')
            current = float(data[0].replace(',',''))
            valBefore -= current
        
        dtlist['AMMOUNT'].append(current)
        dtlist['SALDO'].append(valBefore)
    
    df = pd.DataFrame.from_dict(dtlist)
    df['AMMOUNT'] = df['AMMOUNT'].astype(float)
    
    return df

def BRI_extraction(folderBRI):
    data_extract = {
        "prefix":[],
        "transaction":[],
        "sufix":[]
    }
    for data_file in os.listdir(folderBRI):
        if 'pdf' in data_file:
            extraction_result = bank_extraction(folderBRI+'/'+data_file,filter_trash = '\d+\s+dari\s+\d+',sufix_filter = 'OPENING.*',extract_table = "\d\d\/\d\d\/\d\d\s.*?.+",extract_detail = "(([\d\.,]+\.\d+)\s+([\d\.,]+\.\d+)\s+(.*))")
            data_extract["prefix"].append(extraction_result[0])
            data_extract["sufix"].append(extraction_result[2])
            data_extract["transaction"].append(BRI_table_spliting(extraction_result))
    
    data_extract = pd.DataFrame.from_dict(data_extract) #Next Will Use For Multiple Bank Account

    prefix = extraction_result[0].replace('\n',' ')
    sufix = extraction_result[2].replace('\n',' ')
    Transaction_data = pd.concat(data_extract["transaction"].values.tolist()).reset_index(drop=True).sort_values(by=['TANGGAL'])



    url     = 'https://llm-processor-swgjfxtwwq-et.a.run.app/modelBertIndo'

    data = {
        "context"       : extraction_result[0].replace('\n',' ')
    }

    PrefixExtract = []
    for query in ["Nama Bank adalah","Account No adalah","Account Holder adalah"]:
        data['query'] = query
        print(data)
        response = req.post(url, headers=headers, data=json.dumps(data))
        print(response)
        response = json.loads(response.text)
        PrefixExtract.append(response['result'])

    outputResult={
        "Bank_Name":PrefixExtract[0],
        "Account_Number":PrefixExtract[1],
        "Account_Holder":PrefixExtract[2],
        "Transaction_Analysis":Bank_Data_Ekstract(Transaction_data.copy())
    }
        
    return outputResult,prefix,Transaction_data,sufix

#CIMB SECTION
def CIMB_table_spliting(df):
    df = df[1]
    dtlist = {
        "TANGGAL":[],
        "KETERANGAN":[],
        "STATUS":[],
        "AMMOUNT":[],
        "SALDO":[]
    }
    for er in df:
        data = re.findall(r"(\d\d\d\d\-\d\d\-\d\d)\s+(.*)",er[0])[0]
        tahun,bulan = data[0].split('-')[:2]
        bulan = monthData[int(bulan)-1]
        
        dtlist['TANGGAL'].append(bulan+' '+tahun)
        dtlist['KETERANGAN'].append(data[1])

        data = er[1].strip().split(' ')
        if len(data[0])>1:
            if '-' in data[0]:
                data = ['-']+[data[0].replace('-','')]+[data[1]]
            else:
                data = ['+']+[data[0].replace('+','')]+[data[1]]
        
        if data[0]=='-':
            dtlist['STATUS'].append('DEBIT')
            dtlist['AMMOUNT'].append(data[1].replace(',','').strip())
        else:
            dtlist['STATUS'].append('CREDIT')
            dtlist['AMMOUNT'].append(data[1].replace(',','').strip())
        dtlist['SALDO'].append(data[2].replace(',','').strip())
        
    df = pd.DataFrame.from_dict(dtlist)
    df['AMMOUNT'] = df['AMMOUNT'].astype(float)
    df['SALDO']   = df['SALDO'].astype(float)
    
    return df

def CIMB_extraction(folderCIMB):
    data_extract = {
        "prefix":[],
        "transaction":[],
        "sufix":[]
    }
    for data_file in os.listdir(folderCIMB):
        if 'pdf' in data_file:
            extraction_result = bank_extraction(folderCIMB+'/'+data_file,filter_trash = 'PT Bank CIMB Niaga Tbk is registered and under supervision of Financial Services Authority ( OJK ).OCTO Clicks Copyright © 2020. All rights reserved .',sufix_filter = 'Begining\s+Balance',extract_table = "\d\d\d\d-\d\d-\d\d.*?.+\\n",extract_detail = "((-|\+)[\s,\d]+\.\d\d[\s,\d]+\.\d\d)")
            data_extract["prefix"].append(extraction_result[0])
            data_extract["sufix"].append(extraction_result[2])
            data_extract["transaction"].append(CIMB_table_spliting(extraction_result))
    
    data_extract = pd.DataFrame.from_dict(data_extract) #Next Will Use For Multiple Bank Account

    prefix = extraction_result[0].replace('\n',' ')
    sufix = extraction_result[2].replace('\n',' ')
    Transaction_data = pd.concat(data_extract["transaction"].values.tolist()).reset_index(drop=True).sort_values(by=['TANGGAL'])

    url     = 'https://llm-processor-swgjfxtwwq-et.a.run.app/modelBertIndo'

    data = {
        "context"       : extraction_result[0].replace('\n',' ')
    }

    PrefixExtract = []
    for query in ["Nama Bank adalah","Account No adalah","Account Holder adalah"]:
        data['query'] = query
        print(data)
        response = req.post(url, headers=headers, data=json.dumps(data))
        print(response)
        response = json.loads(response.text)
        PrefixExtract.append(response['result'])

    outputResult={
        "Bank_Name":PrefixExtract[0],
        "Account_Number":PrefixExtract[1],
        "Account_Holder":PrefixExtract[2],
        "Transaction_Analysis":Bank_Data_Ekstract(Transaction_data.copy())
    }
        
    return outputResult,prefix,Transaction_data,sufix