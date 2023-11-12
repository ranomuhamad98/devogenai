import os
import time
import shutil
import PIL

import pandas as pd
import numpy as np

from google.cloud import vision

from pdf2image import convert_from_path
from PIL import Image

from genaiapp.modules.utils.ocr_confidence import spredConf

import cv2
from scipy.ndimage import interpolation as inter
from scipy.ndimage import rotate

import requests as req
import json

def correct_skew(image, delta=1, limit=5):
    def determine_score(arr, angle):
        data = inter.rotate(arr, angle, reshape=False, order=0)
        histogram = np.sum(data, axis=1, dtype=float)
        score = np.sum((histogram[1:] - histogram[:-1]) ** 2, dtype=float)
        return histogram, score

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1] 

    scores = []
    angles = np.arange(-limit, limit + delta, delta)
    for angle in angles:
        histogram, score = determine_score(thresh, angle)
        scores.append(score)

    best_angle = angles[scores.index(max(scores))]

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, best_angle, 1.0)
    corrected = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, \
            borderMode=cv2.BORDER_REPLICATE)

    return best_angle, corrected

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
      df_text['text'].append(texts[i].description+'_'+str("{:.5f}".format(confidence[i-1])))
      df_text['y_pos'].append([texts[i].bounding_poly.vertices[x].y for x in range(4)])
      df_text['x_pos'].append([texts[i].bounding_poly.vertices[x].x for x in range(4)])
    df_text = pd.DataFrame.from_dict(df_text)

    A = np.array(df_text.y_pos.values.tolist())
    text_data = df_text.text.values.tolist()
    x_pos = df_text.x_pos.values.tolist()
    text_result = []
    for B in df_text.y_pos:
      cosine = np.array([np.abs(x.sum()) for x in A-B])
      text_next = (cosine).argsort()[np.sort(cosine)<35]
      posmax = []
      posmin = []
      for i in range(len(text_next)):
        posmax.append(max(x_pos[text_next[i]]))
        posmin.append(min(x_pos[text_next[i]]))
      posmax_in = np.array(posmax).argsort()
      posx = posmax+posmin
      posx = np.sort(np.array(posx)).tolist()

      text_new  = [text_data[text_next[x]] for x in range(len(text_next))]
      text_new2 = [text_new[posmax_in[x]] for x in range(len(posmax_in))]
      
      text_result.append((" ".join(text_new2),B))
    
    rsemen = pd.DataFrame(text_result).sort_values(by=[1]).drop_duplicates(subset=[0])[0].values.tolist()

    gabung = [rsemen[0]]
    lastb = rsemen[0]
    for i in range(1,len(rsemen)):
        if jaccard_similarity(lastb,rsemen[i]) > 0.5:
            before_add = []
            for r in rsemen[i].split(' '):
                if r not in lastb.split(' '):
                    before_add.append(r)
            if len(before_add) != 0:
                gabung.append(' '.join(before_add))

        else:
            gabung.append(' '+rsemen[i])

        lastb = rsemen[i]

    gabung2 = [gabung[0]]
    lastb = gabung[0]
    for i in range(1,len(gabung)):
        before_add = []
        for r in gabung[i].split(' '):
            if r not in lastb.split(' '):
                before_add.append(r)
        if len(before_add) != 0:
            gabung2.append(' '.join(before_add))

        lastb = gabung[i]

    return " ".join(gabung2)

def DocumentUpload(foldername_rand,df_path):
    dataDocument = {
        'documents':[],
        'path_data':[],
        'time_process':[]
    }

    print('Process Start')
    df = pd.read_csv(df_path)
    for fileName in os.listdir('DataForAccess'+foldername_rand):
        start = time.time()
        path_document = 'DataForAccess'+foldername_rand+'/'+fileName

        if fileName in df['path_data']:
            continue

        images = convert_from_path(path_document)
        folderName = 'TrainTable'+foldername_rand
        os.mkdir(folderName)
        os.mkdir('ImagePage'+foldername_rand)

        fullDocText = ""
        for i in range(len(images)):
            try:
                data_img = np.asarray(images[i])
                angle, corrected = correct_skew(data_img)
                img = PIL.Image.fromarray(corrected)
                img.save('ImagePage'+foldername_rand+'/page'+ str(i) +'.jpg', 'JPEG')
                response = detect_text('ImagePage'+foldername_rand+'/page'+ str(i) +'.jpg')
                # print("\n\n\npage",str(i),"\n",response)
                fullDocText += " " + response
            except:
                pass

        print(fileName, end=" ")
        dataDocument['documents'].append(fullDocText)
        dataDocument['path_data'].append(fileName)
        end = time.time()
        print("Done",(end-start), "s")
        dataDocument['time_process'].append(end-start)
        os.remove(path_document)
        shutil.rmtree('TrainTable'+foldername_rand)
        shutil.rmtree('ImagePage'+foldername_rand)
    
    shutil.rmtree('DataForAccess'+foldername_rand)
    
    df = pd.concat([pd.read_csv(df_path),pd.DataFrame.from_dict(dataDocument)])
    df = df.drop_duplicates(subset=['path_data'])
    df.to_csv(df_path,index=False)

def imageUpload_single(foldername_rand,csv_file):
    dataDocument = {
        'documents':[],
        'path_data':[],
        'time_process':[]
    }

    print('Process Start')
    for fileName in os.listdir('DataForAccess'+foldername_rand):
        start = time.time()
        path_document = 'DataForAccess'+foldername_rand+'/'+fileName

        im = Image.open(path_document)
        im = im.convert('RGB')
        data_img = np.asarray(im)
        angle, corrected = correct_skew(data_img)
        img = PIL.Image.fromarray(corrected)
        img.save(foldername_rand+'.jpg', 'JPEG')
        response = detect_text(foldername_rand+'.jpg')
        # print("\n\n\npage",str(i),"\n",response)

        print(fileName, end=" ")
        dataDocument['documents'].append(response)
        dataDocument['path_data'].append(fileName)
        end = time.time()
        print("Done",(end-start), "s")
        dataDocument['time_process'].append(end-start)
        os.remove(path_document)
    
    df = pd.concat([pd.read_csv(csv_file),pd.DataFrame.from_dict(dataDocument)])
    df.to_csv(csv_file,index=False)
    shutil.rmtree('DataForAccess'+foldername_rand)
    # os.remove(foldername_rand+'.jpg')

def DocumentUpload_Translate(foldername_rand,df_path,gcp_token):

    dataDocument = {
        'documents':[],
        'path_data':[],
        'time_process':[],
        'translate':[]
    }

    print('Process Start')
    df = pd.read_csv('df.csv')
    for fileName in os.listdir('DataForAccess'+foldername_rand):
        start = time.time()
        path_document = 'DataForAccess'+foldername_rand+'/'+fileName

        if fileName in df['path_data']:
            continue

        images = convert_from_path(path_document)
        folderName = 'TrainTable'+foldername_rand
        os.mkdir(folderName)
        os.mkdir('ImagePage'+foldername_rand)

        fullDocText = ""
        TranslateDoc = ""
        for i in range(len(images)):
            try:
                data_img = np.asarray(images[i])
                angle, corrected = correct_skew(data_img)
                img = PIL.Image.fromarray(corrected)
                img.save('ImagePage'+foldername_rand+'/page'+ str(i) +'.jpg', 'JPEG')
                response = detect_text('ImagePage'+foldername_rand+'/page'+ str(i) +'.jpg')
                # print("\n\n\npage",str(i),"\n",response)
                fullDocText += " " + response

                dataPost = {
                    "data"       : spredConf(response),
                    "lang"       : "Indonesia",
                    "gcp_token"  : gcp_token
                }

                headers = {
                    'Authorization': 'Bearer ' + gcp_token,
                    'Content-Type': 'application/json'
                }

                url     = 'https://llm-processor-swgjfxtwwq-et.a.run.app/modelTranslate'

                response = req.post(url, headers=headers, data=json.dumps(dataPost))
                response = json.loads(response.text)
                result   = response['result']

                TranslateDoc += " " + result
                print("Process",i,"done")
            except:
                pass

        print(fileName, end=" ")
        dataDocument['documents'].append(fullDocText)
        dataDocument['translate'].append(TranslateDoc)
        dataDocument['path_data'].append(fileName)
        end = time.time()
        print("Done",(end-start), "s")
        dataDocument['time_process'].append(end-start)
        os.remove(path_document)
        shutil.rmtree('TrainTable'+foldername_rand)
        shutil.rmtree('ImagePage'+foldername_rand)
    
    shutil.rmtree('DataForAccess'+foldername_rand)
    
    df = pd.concat([pd.read_csv(df_path),pd.DataFrame.from_dict(dataDocument)])
    df = df.drop_duplicates(subset=['path_data'])
    df.to_csv(df_path,index=False)

def DocumentUploadInfoPage(foldername_rand,df_path):
    dataDocument = {
        'documents':[],
        'page':[],
        'path_data':[],
        'time_process':[]
    }

    print('Process Start')
    df = pd.read_csv(df_path)
    for fileName in os.listdir('DataForAccess'+foldername_rand):
        start = time.time()
        path_document = 'DataForAccess'+foldername_rand+'/'+fileName

        if fileName in df['path_data']:
            continue

        images = convert_from_path(path_document)
        folderName = 'TrainTable'+foldername_rand
        os.mkdir(folderName)
        os.mkdir('ImagePage'+foldername_rand)

        page = 0
        datasucess = len(images)
        for i in range(len(images)):
            try:
                data_img = np.asarray(images[i])
                angle, corrected = correct_skew(data_img)
                img = PIL.Image.fromarray(corrected)
                img.save('ImagePage'+foldername_rand+'/page'+ str(i) +'.jpg', 'JPEG')
                response = detect_text('ImagePage'+foldername_rand+'/page'+ str(i) +'.jpg')
                # print("\n\n\npage",str(i),"\n",response)
                
                dataDocument['documents'].append(response)
                dataDocument['path_data'].append(fileName)
                dataDocument['page'].append(page)
                page+=1
                print("page",page)
            except:
                datasucess-=1

        print(fileName, end=" ")
        end = time.time()
        print("Done",(end-start), "s")
        dataDocument['time_process']=[end-start]*datasucess
        shutil.rmtree('TrainTable'+foldername_rand)
        shutil.rmtree('ImagePage'+foldername_rand)
    
    shutil.rmtree('DataForAccess'+foldername_rand)
    df = pd.concat([pd.read_csv(df_path),pd.DataFrame.from_dict(dataDocument)])
    df = df.drop_duplicates()
    df.to_csv(df_path,index=False)
