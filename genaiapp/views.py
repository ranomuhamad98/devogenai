from datetime import datetime
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from .models import *
from .forms import *
from django.http import HttpResponse
import json
import random
import base64
import numpy as np
import pandas as pd

#bank statement
from genaiapp.modules.bank_statement import BankStatementProcessor
from genaiapp.modules.utils.bank_statement_helper import DataFrameExtraction

def check_user_permission(user, perm):
    x = user.user.user_permissions.all().values_list('codename', flat=True).values()
    check = len([d for d in x if d["codename"] in str(perm)])
    perms = {}
    for idx, data in enumerate(x):
        perms['%s' % str(data['codename'])] = idx+1
    
    if(check!=True): 

        halaman = str(user.get_full_path()).split('/')
        if(len(halaman) == 2):
            HttpResponseRedirect("/logout")
        else:        
            # return HttpResponseRedirect("/"+str(halaman[1]))
            return False, HttpResponseRedirect(reverse(str(halaman[1])))
            # raise HttpResponse('Unauthorized', status=401)
    
    return perms

# dashboard pages

@login_required(login_url="/login")
def indexPage(request):
    return redirect('/dashboard_default')

# .......
@login_required(login_url="/login") 
def upload_document(request):
    data_doc = {"document_name":"table cell 1","id":"1"},{"document_name":"table cell 2","id":"2"},{"document_name":"table cell 3","id":"3"}
    context={"breadcrumb":{"parent":"Dashboard","child":"Document Extraction","child2":"Upload Document"}, "data": data_doc, "perms": check_user_permission(request,'document_extraction')}
    return render(request,'theme_genai/document_extraction/index-1.html',context)
@login_required(login_url="/login")
def parser_setup(request):
        data_doc = {"document_name":"table cell 1","id":"1"},{"document_name":"table cell 2","id":"2"},{"document_name":"table cell 3","id":"3"}
        data_parser = {"parser_name":"table cell 1","id":"1"},{"parser_name":"table cell 2","id":"2"},{"parser_name":"table cell 3","id":"3"}
        context={"breadcrumb":{"parent":"Dashboard","child":"Document Extraction","child2":"Parser Set UP"}, "data_doc": data_doc, "data_parser": data_parser, "perms": check_user_permission(request,'document_extraction')}
        return render(request,'theme_genai/document_extraction/index-2.html',context)
@login_required(login_url="/login")
def extraction_process(request):
    data_extraction = {"document":"a","bank_name":"b","rekening_number": "c", "luas_lahan": "d", "telp": "e", "waktu_sewa": "f", "rekening_number": "g"},{"document":"a","bank_name":"b","rekening_number": "c", "luas_lahan": "d", "telp": "e", "waktu_sewa": "f", "rekening_number": "g"},{"document":"a","bank_name":"b","rekening_number": "c", "luas_lahan": "d", "telp": "e", "waktu_sewa": "f", "rekening_number": "g"}
    context={"breadcrumb":{"parent":"Dashboard","child":"Document Extraction","child2":"Extraction Process"}, "data_extraction": data_extraction, "perms": check_user_permission(request,'document_extraction')}
    return render(request,'theme_genai/document_extraction/index-3.html',context)

@login_required(login_url="/login")
def document_translation(request):
    data_doc = {"document_name":"table cell 1","id":"1"},{"document_name":"table cell 2","id":"2"},{"document_name":"table cell 3","id":"3"}
    context={"breadcrumb":{"parent":"Dashboard","child":"Document Translation"},"data": data_doc, "perms": check_user_permission(request,'document_translation')}
    return render(request,'theme_genai/document_translation/index.html',context)

@login_required(login_url="/login")
def bank_statement(request):
    data_prompt = {"a":"prompt table cell 1","b":"prompt table cell 1","c":"prompt table cell 1","d":"prompt table cell 1","e":"prompt table cell 1","f":"prompt table cell 1"},{"a":"prompt table cell 2","b":"prompt table cell 2","c":"prompt table cell 2","d":"prompt table cell 2","e":"prompt table cell 2","f":"prompt table cell 2"},{"a":"prompt table cell 3","b":"prompt table cell 3","c":"prompt table cell 3","d":"prompt table cell 3","e":"prompt table cell 3","f":"prompt table cell 3"}
    data_ocr = {"a":"ocr table cell 1","b":"ocr table cell 1","c":"ocr table cell 1","d":"ocr table cell 1","e":"ocr table cell 1","f":"ocr table cell 1"},{"a":"ocr table cell 2","b":"ocr table cell 2","c":"ocr table cell 2","d":"ocr table cell 2","e":"ocr table cell 2","f":"ocr table cell 2"},{"a":"ocr table cell 3","b":"ocr table cell 3","c":"ocr table cell 3","d":"ocr table cell 3","e":"ocr table cell 3","f":"ocr table cell 3"}
    data_extraction = {"a":"extraction table cell 1","b":"extraction table cell 1","c":"extraction table cell 1","d":"extraction table cell 1","e":"extraction table cell 1","f":"extraction table cell 1"},{"a":"extraction table cell 2","b":"extraction table cell 2","c":"extraction table cell 2","d":"extraction table cell 2","e":"extraction table cell 2","f":"extraction table cell 2"},{"a":"extraction table cell 3","b":"extraction table cell 3","c":"extraction table cell 3","d":"extraction table cell 3","e":"extraction table cell 3","f":"extraction table cell 3"}

    df_bank = pd.read_csv('Dataset/df_bank_statement_result.csv')[['Bank_Name','Account_Number']].drop_duplicates().astype('str').reset_index(drop=True)
    data_doc = ()
    if df_bank is not None and not df_bank.empty:
        for row in range(len(df_bank)):
            row_dict = {"document_name": df_bank['Account_Number'][row]+' - '+df_bank['Bank_Name'][row], "id":str(row+1)}
            data_doc += (row_dict,)

    context={"breadcrumb":{"parent":"Dashboard","child":"Bank Statement"}, "data_doc": data_doc, "data_prompt": data_prompt, "data_ocr": data_ocr, "data_extraction": data_extraction, "perms": check_user_permission(request,'bank_statement')}
    return render(request,'theme_genai/bank_statement/index.html',context)
    
@login_required(login_url="/login")
def ktp_extraction(request):    
    data_doc = {"document_name":"table cell 1","id":"1"},{"document_name":"table cell 2","id":"2"},{"document_name":"table cell 3","id":"3"}
    context={"breadcrumb":{"parent":"Dashboard","child":"KTP Extraction"},"data_doc": data_doc, "perms": check_user_permission(request,'ktp_extraction')}
    return render(request,'theme_genai/ktp_extraction/index.html',context)

@login_required(login_url="/login")
def image_extraction(request):
    data_doc = {"document_name":"table cell 1","id":"1"},{"document_name":"table cell 2","id":"2"},{"document_name":"table cell 3","id":"3"}
    context={"breadcrumb":{"parent":"Dashboard","child":"Image Extraction"},"data_doc": data_doc, "perms": check_user_permission(request,'image_extraction')}
    return render(request,'theme_genai/image_extraction/index.html',context)

# [START] PROCESS

# [start] document extraction - upload document
@login_required(login_url="/login")
def de_ud_action_newdoc(request):
    val,rtn = check_user_permission(request,'document_extraction')
    if val==False: return rtn

    if request.method == "POST":
        data = request.POST

        newdoc_str = data.get("new_doc")

        # start - upload file
        format, imgstr = newdoc_str.split(';base64,') 
        ext = format.split('/')[-1] 
        filename = ""+str(datetime.now().strftime("%Y%m%d%H%M%S"))+"_document-extraction."+ext
        file_content=base64.b64decode(imgstr)
        with open("genaiapp/static/assets/"+filename, 'wb') as f:
            f.write(file_content)
        # end - upload file
        
        data_response = json.dumps({"status":1, "message": "bs_action_newdoc berhasil","data":data, "processing_time":"test processing time","ocr_conf":"ocr conf","preview_ocr_result": "lorem ipsum"})

        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def de_ud_action_docname(request):
    val,rtn = check_user_permission(request,'document_extraction')
    if val==False: return rtn

    if request.method == "GET":
        idx = request.GET['post_id']
        data_response = json.dumps({"processing_time":"test processing time ("+idx+")","ocr_conf":"ocr conf ("+idx+")","preview_ocr_result": "lorem ipsum ("+idx+")"})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def de_ud_action_docdel(request):
    val,rtn = check_user_permission(request,'document_extraction')
    if val==False: return rtn
    if request.method == "GET":
        idx = request.GET['post_id']
        data_response = json.dumps({"data_delete":"id "+idx+""})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def de_ud_action_showconf(request):
    val,rtn = check_user_permission(request,'document_extraction')
    if val==False: return rtn
    if request.method == "POST":
        data = request.POST
        dt_processing_time = data.get("processing_time")
        dt_ocr_conf = data.get("ocr_conf")
        dt_preview_ocr_result = data.get("preview_ocr_result")
        result_conf = "<span><span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(251, 236, 93); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> SAPRATI</span><span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(255, 170, 170); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> ENY</span><span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(251, 236, 93); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> *</span><span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(255, 170, 170); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> #F</span><span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(251, 236, 93); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> NOTARIS</span><span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(251, 236, 93); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> KABU</span> PERJANJIAN SEWA TANAH / BANGUNAN<span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(251, 236, 93); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> KARAWANG</span> Antara PT MENARA<span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(251, 236, 93); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> SELULAR</span><span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(251, 236, 93); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> NUSANTARA</span> Dan<span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(251, 236, 93); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> [</span> Sunardi<span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(251, 236, 93); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> ]</span> NOMOR<span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(251, 236, 93); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> :</span> .075 . / PKSL /<span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(251, 236, 93); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> MSN</span><span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(251, 236, 93); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> /</span><span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(255, 170, 170); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> II</span> </span>"
        data_response = json.dumps({"result_conf":result_conf, "dt_processing_time": dt_processing_time, "dt_ocr_conf": dt_ocr_conf, "dt_preview_ocr_result": dt_preview_ocr_result})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def de_ud_action_search(request):
    val,rtn = check_user_permission(request,'document_extraction')
    if val==False: return rtn
    if request.method == "POST":
        data = request.POST
        data_response = json.dumps({"preview_prompt_result":"kvalue - ("+data.get("k_value")+") : promptinput - ("+data.get("prompt_input")+")"})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)
# [end] document extraction - upload document

# [start] document extraction - parser setup
@login_required(login_url="/login")
def de_ps_action_view(request):
    val,rtn = check_user_permission(request,'document_extraction')
    if val==False: return rtn
    if request.method == "GET":
        data = request.GET['post_id']
        data_response = json.dumps({"document_test":data})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def de_ps_action_parser(request):
    val,rtn = check_user_permission(request,'document_extraction')
    if val==False: return rtn
    if request.method == "GET":
        data = request.GET['post_id'];
        data_response = json.dumps({"model_name" : "model_name "+data+"", "prompt_used" : "prompt_used "+data+"", "first_regex_spillter" : "first_regex_spillter "+data+"", "query_used" : "query_used "+data+"", "second_regex_spillter" : "second_regex_spillter "+data+"", "last_regex_filter_used" : "last_regex_filter_used "+data+"", "third_spliter" : "third_spliter "+data+"", "insert_duplication" : ""+str(random.randint(0, 30))+"", "insert_k_value": ""+str(random.randint(0, 30))+""})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def de_ps_action_del(request):
    val,rtn = check_user_permission(request,'document_extraction')
    if val==False: return rtn
    if request.method == "GET":
        idx = request.GET['post_id']
        data_response = json.dumps({"status": 1,"data_delete":"id "+idx+""})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def de_ps_action_save(request):
    val,rtn = check_user_permission(request,'document_extraction')
    if val==False: return rtn
    if request.method == "POST":
        # status 1 = success, status 0 = failed
        data_response = json.dumps({"status": 1,"ps_action_save":"success","random":""+str(random.randint(0, 30))+""})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def de_ps_action_test(request):
    val,rtn = check_user_permission(request,'document_extraction')
    if val==False: return rtn
    if request.method == "POST":
        # status 1 = success, status 0 = failed
        data = request.POST
        data_response = json.dumps({"status": 1, "processing_time": "processing_time "+str(random.randint(0,30))+"","ocr_quality": "ocr_quality "+str(random.randint(0,30))+"","result_test": "result_test "+str(random.randint(0,30))+"","ocr_conf_score_model_test": "ocr_conf_score_model_test "+str(random.randint(0,30))+"", "data": data})
        # data_response = json.dumps({"status": 0, "data": data})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def de_ps_action_update(request):
    val,rtn = check_user_permission(request,'document_extraction')
    if val==False: return rtn
    if request.method == "POST":
        # status 1 = success, status 0 = failed
        data = request.POST
        data_response = json.dumps({"status": 1, "data": data})
        # data_response = json.dumps({"status": 0, "data": data})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def de_ps_action_showconf(request):
    val,rtn = check_user_permission(request,'document_extraction')
    if val==False: return rtn
    if request.method == "POST":
        data = request.POST
        result_conf = "<span> 4 akan dilakukan dengan transfer ke rekening bank pemilik sebagaimana diuraikan di bawah ini : nomor rekening<span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(255, 170, 170); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> :</span> 5806-01-016798-53-5 nama pemegang rekening : sunardi bank bank rakyat indonesia pemilik dengan ini menyatakan dan menjamin bahwa rekening bank diatas adalah rekening bank yang benar dan sah dari</span>"
        data_response = json.dumps({"status":1,"result_conf": result_conf, "data": data})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)
# [end] document extraction - parser setup

# [start] document extraction - extraction process
@login_required(login_url="/login")
def de_ep_action_downjson(request,id):
    val,rtn = check_user_permission(request,'document_extraction')
    if val==False: return rtn
    if request.method == "GET":
        return HttpResponse("download file json ("+id+")")
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def de_ep_action_downcsv(request,id):
    val,rtn = check_user_permission(request,'document_extraction')
    if val==False: return rtn
    if request.method == "GET":
        return HttpResponse("download file csv ("+id+")")
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def de_ep_action_alldoc(request,id):
    val,rtn = check_user_permission(request,'document_extraction')
    if val==False: return rtn
    if request.method == "GET":
        return HttpResponse("download all file ("+id+")")
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)
# [end] document extraction - extraction process

# [start] document translation
@login_required(login_url="/login")
def dt_action_newdoc(request):
    val,rtn = check_user_permission(request,'document_translation')
    if val==False: return rtn
    if request.method == "POST":
        data = request.POST

        newdoc_str = data.get("new_doc")
        # start - upload file
        format, imgstr = newdoc_str.split(';base64,') 
        ext = format.split('/')[-1] 
        filename = ""+str(datetime.now().strftime("%Y%m%d%H%M%S"))+"_document-translation."+ext
        file_content=base64.b64decode(imgstr)
        with open("genaiapp/static/assets/"+filename, 'wb') as f:
            f.write(file_content)
        # end - upload file

        data_response = json.dumps({"status":1, "message": "dt_action_newdoc berhasil","processing_time":"processing time","ocr_conf":"ocr conf","preview_ocr_result":"preview ocr result","preview_translate_result":"preview translate result"})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def dt_action_docname(request):
    val,rtn = check_user_permission(request,'document_translation')
    if val==False: return rtn
    if request.method == "GET":
        data = request.GET['post_id']
        data_response = json.dumps({"status":1, "message": "dt_action_docname berhasil","processing_time":"processing time "+str(data)+"","ocr_conf":"ocr conf "+str(data)+"","preview_ocr_result":"preview ocr result "+str(data)+"","preview_translate_result":"preview translate result "+str(data)+""})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def dt_action_docdel(request):
    val,rtn = check_user_permission(request,'document_translation')
    if val==False: return rtn
    if request.method == "GET":
        idx = request.GET['post_id']
        data_response = json.dumps({"data_delete":"id "+idx+""})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def dt_action_showconf(request):
    val,rtn = check_user_permission(request,'document_translation')
    if val==False: return rtn
    if request.method == "POST":
        data = request.POST
        result_conf = "<span> 4 akan dilakukan dengan transfer ke rekening bank pemilik sebagaimana diuraikan di bawah ini : nomor rekening<span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(255, 170, 170); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> :</span> 5806-01-016798-53-5 nama pemegang rekening : sunardi bank bank rakyat indonesia pemilik dengan ini menyatakan dan menjamin bahwa rekening bank diatas adalah rekening bank yang benar dan sah dari</span>"
        data_response = json.dumps({"status":1,"message": "dt_action_showconf berhasil","result_conf": result_conf, "data": data})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)
# [end] document translation

# [start] bank statement
@login_required(login_url="/login")
def bs_action_newdoc(request):
    val,rtn = check_user_permission(request,'bank_statement')
    if val==False: return rtn

    if request.method == "POST":
        data = request.POST
 
        newdoc_str = data.get("new_doc")
        bankname_str = data.get("bank_name")

        processor = BankStatementProcessor(bankname_str)

        # start - upload file
        format, imgstr = newdoc_str.split(';base64,') 
        ext = format.split('/')[-1] 
        filename = ""+str(datetime.now().strftime("%Y%m%d%H%M%S"))+"_bank-statement."+ext
        file_content=base64.b64decode(imgstr)
        with open("genaiapp/static/assets/"+filename, 'wb') as f:
            f.write(file_content)
        # end - upload file

        uploaded_files = processor.upload_files("genaiapp/static/assets/"+filename)
        data_result, prefix, TransactionDetail, TransactionDetail2, sufix, ocr_result, extraction_result = processor.process_files(uploaded_files)

        if bankname_str == 'BCA':
            TransactionDetail2['prefixData']     = np.array([prefix] * len(TransactionDetail2))
            TransactionDetail2['sufixData']      = np.array([sufix] * len(TransactionDetail2))
            TransactionDetail2['Bank_Name']      = [data_result['Bank_Name']] * len(TransactionDetail2)
            TransactionDetail2['Account_Holder'] = [data_result['Account_Holder']] * len(TransactionDetail2)
            TransactionDetail2['Account_Number'] = [data_result['Account_Number']] * len(TransactionDetail2)

            TransactionDetail2 = pd.concat([TransactionDetail2,pd.read_csv('Dataset/df_bank_statement_raw_BCA.csv')])
            TransactionDetail2.to_csv('Dataset/df_bank_statement_raw_BCA.csv',index=False)

        TransactionDetail['prefixData']     = np.array([prefix] * len(TransactionDetail))
        TransactionDetail['sufixData']      = np.array([sufix] * len(TransactionDetail))
        TransactionDetail['Bank_Name']      = [data_result['Bank_Name']] * len(TransactionDetail)
        TransactionDetail['Account_Holder'] = [data_result['Account_Holder']] * len(TransactionDetail)
        TransactionDetail['Account_Number'] = [data_result['Account_Number']] * len(TransactionDetail)

        TransactionDetail = pd.concat([TransactionDetail,pd.read_csv('Dataset/df_bank_statement_raw.csv')])
        TransactionDetail.to_csv('Dataset/df_bank_statement_raw.csv',index=False)

        data_result2                         = data_result['Transaction_Analysis']
        data_result2['Bank_Name']            = [data_result['Bank_Name']] * len(data_result2)
        data_result2['Account_Number']       = [data_result['Account_Number']] * len(data_result2)
        data_result2['Account_Holder']       = [data_result['Account_Holder']] * len(data_result2)

        data_result2 = pd.concat([data_result2,pd.read_csv('Dataset/df_bank_statement_result.csv')])
        data_result2.to_csv('Dataset/df_bank_statement_result.csv',index=False)
        
        free_prompt = {"table": ocr_result["table"], "prefix_ocr":ocr_result["prefix"], "prompt_dataframe": "prompt data frame"}

        data_response = json.dumps({"status":1, "message": "bs_action_newdoc berhasil","data":data, "ocr_result": ocr_result, "free_prompt": free_prompt, "extraction_result": extraction_result})

        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def bs_action_docname(request):
    val,rtn = check_user_permission(request,'bank_statement')
    if val==False: return rtn

    if request.method == "GET":
        docname = request.GET['post_id']

        #find the selected index
        df_bank = pd.read_csv('Dataset/df_bank_statement_result.csv')[['Bank_Name','Account_Number']].drop_duplicates().astype('str').reset_index(drop=True)
        for row in df_bank.index:
            if df_bank['Account_Number'][row] + ' - ' + df_bank['Bank_Name'][row] == docname:
                data=row
                break

        TransactionDetail = pd.read_csv('Dataset/df_bank_statement_raw.csv').astype('str')
        TransactionDetail = TransactionDetail.query("Account_Number == '"+df_bank['Account_Number'][data]+"' and Bank_Name == '"+ df_bank['Bank_Name'][data]+"'")

        TransactionDetail_drop = TransactionDetail.drop(columns=['prefixData','sufixData','Bank_Name','Account_Number','Account_Holder'])

        transaction_detail = ()
        if TransactionDetail_drop is not None and not TransactionDetail_drop.empty:
            for _, row in TransactionDetail_drop.iterrows():
                row_dict = {col: row[col] for col in TransactionDetail_drop.columns}
                transaction_detail += (row_dict,)

        data_result = pd.read_csv('Dataset/df_bank_statement_result.csv').astype('str')
        data_result = data_result.query("Account_Number == '"+df_bank['Account_Number'][data]+"' and Bank_Name == '"+ df_bank['Bank_Name'][data]+"'")
        data_result_drop = data_result.drop(columns=['Bank_Name','Account_Number','Account_Holder'])

        transaction_analysis = ()
        if data_result_drop is not None and not data_result_drop.empty:
            for _, row in data_result_drop.iterrows():
                row_dict = {col: row[col] for col in data_result_drop.columns}
                transaction_analysis += (row_dict,)

        if 'BCA' in df_bank['Bank_Name'][data]:
            TransactionDetail2 = pd.read_csv('Dataset/df_bank_statement_raw_BCA.csv').astype('str')
            TransactionDetail2 = TransactionDetail2.query("Account_Number == '"+df_bank['Account_Number'][data]+"' and Bank_Name == '"+ df_bank['Bank_Name'][data]+"'")
            TransactionDetail2 = TransactionDetail2.drop(columns=['prefixData','sufixData','Bank_Name','Account_Number','Account_Holder'])

        # tab ocr result
        ocr_result = {"prefix": TransactionDetail['prefixData'].values[0],"sufix":TransactionDetail['sufixData'].values[0],"table": transaction_detail}
        free_prompt = {"table": transaction_detail, "prefix_ocr":TransactionDetail['prefixData'].values[0], "prompt_dataframe": "prompt data frame"}
        extraction_result = {"bank_name": data_result['Bank_Name'].values[0], "account_number": data_result['Account_Number'].values[0], "account_holder": data_result['Account_Holder'].values[0], "table": transaction_analysis}

        data_response = json.dumps({"status":1, "message": "bs_action_newdoc berhasil","data":data, "ocr_result": ocr_result, "free_prompt": free_prompt, "extraction_result": extraction_result})

        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def bs_action_docdel(request):
    val,rtn = check_user_permission(request,'bank_statement')
    if val==False: return rtn

    if request.method == "GET":
        data = int(request.GET['post_id'])
        data =data-1
        df_bank = pd.read_csv('Dataset/df_bank_statement_result.csv')[['Bank_Name','Account_Number']].drop_duplicates().astype('str').reset_index(drop=True)
        TransactionDetail = pd.read_csv('Dataset/df_bank_statement_raw.csv').astype('str')

        indexing = TransactionDetail.query("Account_Number == '"+df_bank['Account_Number'][data]+"' and Bank_Name == '"+ df_bank['Bank_Name'][data]+"'")
        TransactionDetail = TransactionDetail.drop(indexing.index)
        TransactionDetail.to_csv('Dataset/df_bank_statement_raw.csv',index=False)

        data_result = pd.read_csv('Dataset/df_bank_statement_result.csv').astype('str')
        indexing    = data_result.query("Account_Number == '"+df_bank['Account_Number'][data]+"' and Bank_Name == '"+ df_bank['Bank_Name'][data]+"'")
        data_result = data_result.drop(indexing.index)
        data_result.to_csv('Dataset/df_bank_statement_result.csv',index=False)

        if 'BCA' in df_bank['Bank_Name'][data]:
            TransactionDetail2 = pd.read_csv('Dataset/df_bank_statement_raw_BCA.csv').astype('str')
            indexing           = TransactionDetail2.query("Account_Number == '"+df_bank['Account_Number'][data]+"' and Bank_Name == '"+ df_bank['Bank_Name'][data]+"'")
            TransactionDetail2 = TransactionDetail2.drop(indexing.index)
            print(TransactionDetail2)
            TransactionDetail2.to_csv('Dataset/df_bank_statement_raw.csv',index=False)
        data_response = json.dumps({"data_delete":"id "+str(data)+""})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def bs_action_processfp(request):
    val,rtn = check_user_permission(request,'bank_statement')
    if val==False: return rtn

    if request.method == "POST":
        data = request.POST
        TransactionDetail = pd.read_csv('Dataset/df_bank_statement_raw.csv').astype('str')
        result = DataFrameExtraction(TransactionDetail,str(data.get("prompt_dataframe")),str(data.get("prefix_ocr")))
        data_response = json.dumps({"result_dataframe_search":result})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)
# [end] bank statement

# [start] ktp extraction
@login_required(login_url="/login")
def ke_action_newdoc(request):
    val,rtn = check_user_permission(request,'ktp_extraction')
    if val==False: return rtn
    
    if request.method == "POST":
        data = request.POST

        newdoc_str = data.get("new_doc")
        # start - upload file
        format, imgstr = newdoc_str.split(';base64,') 
        ext = format.split('/')[-1] 
        filename = ""+str(datetime.now().strftime("%Y%m%d%H%M%S"))+"_ktp-extraction."+ext
        file_content=base64.b64decode(imgstr)
        with open("genaiapp/static/assets/"+filename, 'wb') as f:
            f.write(file_content)
        # end - upload file

        data_response = json.dumps({"status":1, "message": "ke_action_newdoc berhasil","processing_time":"processing time","ocr_conf":"ocr conf","preview_ocr_result":"preview ocr result"})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def ke_action_docname(request):
    val,rtn = check_user_permission(request,'ktp_extraction')
    if val==False: return rtn
    
    if request.method == "GET":
        data = request.GET['post_id']
        data_response = json.dumps({"status":1, "message": "ke_action_docname berhasil","processing_time":"processing time "+str(data)+"","ocr_conf":"ocr conf "+str(data)+"","preview_ocr_result":"preview ocr result "+str(data)+""})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def ke_action_docdel(request):
    val,rtn = check_user_permission(request,'ktp_extraction')
    if val==False: return rtn
    
    if request.method == "GET":
        idx = request.GET['post_id']
        data_response = json.dumps({"data_delete":"id "+idx+""})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def ke_action_showconf(request):
    val,rtn = check_user_permission(request,'ktp_extraction')
    if val==False: return rtn
    
    if request.method == "POST":
        data = request.POST
        result_conf = "<span> 4 akan dilakukan dengan transfer ke rekening bank pemilik sebagaimana diuraikan di bawah ini : nomor rekening<span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(255, 170, 170); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> :</span> 5806-01-016798-53-5 nama pemegang rekening : sunardi bank bank rakyat indonesia pemilik dengan ini menyatakan dan menjamin bahwa rekening bank diatas adalah rekening bank yang benar dan sah dari</span>"
        data_response = json.dumps({"status":1,"result_conf": result_conf, "data": data})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def ke_action_extract(request):
    val,rtn = check_user_permission(request,'ktp_extraction')
    if val==False: return rtn
    
    if request.method == "POST":
        data = request.POST
        data_er = {"a":"er table cell 1","b":"er table cell 1","c":"er table cell 1","d":"er table cell 1","e":"er table cell 1","f":"er table cell 1"},{"a":"er table cell 2","b":"er table cell 2","c":"er table cell 2","d":"er table cell 2","e":"er table cell 2","f":"er table cell 2"},{"a":"er table cell 3","b":"er table cell 3","c":"er table cell 3","d":"er table cell 3","e":"er table cell 3","f":"er table cell 3"}
        data_response = json.dumps({"status":1, "message": "ke_action_extract berhasil","data":data, "table": data_er})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)
# [end] ktp extraction

# [start] image extraction
@login_required(login_url="/login")
def ie_action_newdoc(request):
    val,rtn = check_user_permission(request,'image_extraction')
    if val==False: return rtn
    
    if request.method == "POST":
        data = request.POST

        newdoc_str = data.get("new_doc")
        # start - upload file
        format, imgstr = newdoc_str.split(';base64,') 
        ext = format.split('/')[-1] 
        filename = ""+str(datetime.now().strftime("%Y%m%d%H%M%S"))+"_image-extraction."+ext
        file_content=base64.b64decode(imgstr)
        with open("genaiapp/static/assets/"+filename, 'wb') as f:
            f.write(file_content)
        # end - upload file

        data_response = json.dumps({"status":1, "message": "ie_action_newdoc berhasil","processing_time":"processing time","ocr_conf":"ocr conf","preview_ocr_result":"preview ocr result"})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def ie_action_docname(request):
    val,rtn = check_user_permission(request,'image_extraction')
    if val==False: return rtn
    
    if request.method == "GET":
        data = request.GET['post_id']
        data_response = json.dumps({"status":1, "message": "ie_action_docname berhasil","processing_time":"processing time "+str(data)+"","ocr_conf":"ocr conf "+str(data)+"","preview_ocr_result":"preview ocr result "+str(data)+""})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def ie_action_docdel(request):
    val,rtn = check_user_permission(request,'image_extraction')
    if val==False: return rtn
    
    if request.method == "GET":
        idx = request.GET['post_id']
        data_response = json.dumps({"data_delete":"id "+idx+""})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def ie_action_showconf(request):
    val,rtn = check_user_permission(request,'image_extraction')
    if val==False: return rtn
    
    if request.method == "POST":
        data = request.POST
        result_conf = "<span> 4 akan dilakukan dengan transfer ke rekening bank pemilik sebagaimana diuraikan di bawah ini : nomor rekening<span style='display: inline-flex; flex-direction: row; align-items: center; background: rgb(255, 170, 170); border-radius: 0.5rem; padding: 0.25rem 0.5rem; overflow: hidden; line-height: 1;'> :</span> 5806-01-016798-53-5 nama pemegang rekening : sunardi bank bank rakyat indonesia pemilik dengan ini menyatakan dan menjamin bahwa rekening bank diatas adalah rekening bank yang benar dan sah dari</span>"
        data_response = json.dumps({"status":1,"result_conf": result_conf, "data": data})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
        return HttpResponse(data_response)

@login_required(login_url="/login")
def ie_action_search(request):
    val,rtn = check_user_permission(request,'image_extraction')
    if val==False: return rtn
    
    if request.method == "POST":
        data = request.POST
        data_response = json.dumps({"preview_prompt_result":"kvalue - ("+data.get("k_value")+") : promptinput - ("+data.get("prompt_input")+")"})
        return HttpResponse(data_response)
    else:
        data_response = json.dumps({"status":0, "message": "unauthorized"})
# [end] image extraction
# [END] - PROCESS

@login_required(login_url="/login")
def dashboard_default(request):
    check_user_permission(request,'dashboard')
    # context={"breadcrumb":{"parent":"Dashboard","child":"Document Extraction","child2":"Upload Document"}}
    # return render(request,'theme_genai/document_extraction/index-1.html',context)
    context={"breadcrumb":{"parent":"Dashboard","child":"Default"}, "perms": check_user_permission(request,'document_extraction')}
    return render(request,'general/dashboard/default/index.html',context)
# .......





@login_required(login_url="/login")
def dashboard_ecommerce(request):
    context={"breadcrumb":{"parent":"Dashboard","child":"Ecommerce"}}
    return render(request,'general/dashboard/ecommerce/dashboard-02.html',context)


@login_required(login_url="/login")
def dashboard_project(request):
    context={"breadcrumb":{"parent":"Dashboard","child":"project-Dashboard"}}
    return render(request,'general/dashboard/project/dashboard-03.html',context)

# widgets pages


@login_required(login_url="/login")
def widgets_general(request):
    context={"breadcrumb":{"parent":"Widgets","child":"General"}}
    return render(request,'widgets/general/general-widget.html',context)


@login_required(login_url="/login")
def widgets_chart(request):
    context={"breadcrumb":{"parent":"Widgets","child":"Chart"}}
    return render(request,'widgets/chart/chart-widget.html',context)

# page layout views


@login_required(login_url="/login")
def page_layout_boxed(request):
    context ={"layout":"box-layout","breadcrumb":{"parent":"Page Layout","child":"Boxed"}}
    return render(request,'page_layout/boxed/box-layout.html',context)


@login_required(login_url="/login")
def page_layout_rtl(request):
    context={"layout":"rtl","breadcrumb":{"parent":"Page Layout","child":"RTL"}}
    return render(request,'page_layout/RTL/layout-rtl.html',context)


@login_required(login_url="/login")
def page_layout_dark(request):
    context ={"layout":"dark-only","breadcrumb":{"parent":"Page Layout","child":"Layout Dark"}}
    return render(request,'page_layout/dark_layout/layout-dark.html',context)


@login_required(login_url="/login")
def page_layout_hide_nav_scroll(request):
    context={"breadcrumb":{"parent":"Page Layout","child":"Hide Menu On Scroll"}}
    return render(request,'page_layout/hide_nav_scroll/hide-on-scroll.html',context)


@login_required(login_url="/login")
def page_layout_footer_light(request):
    context={"breadcrumb":{"parent":"Page Layout","child":"Footer Light"}}
    return render(request,'page_layout/footer_light/footer-light.html',context)


@login_required(login_url="/login")
def page_layout_footer_dark(request):
    context={"footer":"footer-dark","breadcrumb":{"parent":"Page Layout","child":"Footer Dark"}}
    return render(request,'page_layout/footer_dark/footer-dark.html',context)


@login_required(login_url="/login")
def page_layout_footer_fixed(request):
    context={"footer":"footer-fix","breadcrumb":{"parent":"Page Layout","child":"Footer Fixed"}}
    return render(request,'page_layout/footer_fixed/footer-fixed.html',context)

# project views


@login_required(login_url="/login")
def project_project_list(request):
    context={"breadcrumb":{"parent":"Project","child":"Project List"}}
    return render(request,'project/project_list/projects.html',context)


@login_required(login_url="/login")
def project_create_new(request):
    context={"breadcrumb":{"parent":"Project","child":"Create New"}}
    return render(request,'project/create_new/projectcreate.html',context)

# file manager view


@login_required(login_url="/login")
def file_manager(request):
    context={"breadcrumb":{"parent":"Apps","child":"File Manager"}}
    return render(request,'file_manager/file-manager.html',context)

# kanban board view


@login_required(login_url="/login")
def kanban_board(request):
    context={"breadcrumb":{"parent":"Apps","child":"Kanban Board"}}
    return render(request,'kanban_board/kanban.html',context)

# Ecommerce views


@login_required(login_url="/login")
def ecommerce_product_default(request):
    context={"breadcrumb":{"parent":"E-Commerce","child":"Product"}}
    return render(request,'ecommerce/product/product.html',context)


@login_required(login_url="/login")
def ecommerce_product_page(request):
    context={"breadcrumb":{"parent":"E-Commerce","child":"Product Page"}}
    return render(request,'ecommerce/product_page/product-page.html',context)


@login_required(login_url="/login")
def ecommerce_product_list(request):
    context={"breadcrumb":{"parent":"E-Commerce","child":"Product List"}}
    return render(request,'ecommerce/product_list/list-products.html',context)


@login_required(login_url="/login")
def ecommerce_payment_details(request):
    context={"breadcrumb":{"parent":"E-Commerce","child":"Payment Details"}}
    return render(request,'ecommerce/payment_details/payment-details.html',context)


@login_required(login_url="/login")
def ecommerce_order_history(request):
    context={"breadcrumb":{"parent":"E-Commerce","child":"Order History"}}
    return render(request,'ecommerce/order_history/order-history.html',context)


@login_required(login_url="/login")
def ecommerce_invoice(request):
    context={"breadcrumb":{"parent":"E-Commerce","child":"Invoice"}}
    return render(request,'ecommerce/invoice/invoice-template.html',context)


@login_required(login_url="/login")
def ecommerce_cart(request):
    context={"breadcrumb":{"parent":"E-Commerce","child":"Cart"}}
    return render(request,'ecommerce/cart/cart.html',context)


@login_required(login_url="/login")
def ecommerce_wishlist(request):
    context={"breadcrumb":{"parent":"E-Commerce","child":"Wishlist"}}
    return render(request,'ecommerce/wishlist/list-wish.html',context)


@login_required(login_url="/login")
def ecommerce_checkout(request):
    context={"breadcrumb":{"parent":"E-Commerce","child":"Checkout"}}
    return render(request,'ecommerce/checkout/checkout.html',context)


@login_required(login_url="/login")
def ecommerce_pricing(request):
    context={"breadcrumb":{"parent":"E-Commerce","child":"Pricing"}}
    return render(request,'ecommerce/pricing/pricing.html',context)


# email views


@login_required(login_url="/login")
def email_email_app(request):
    context={"breadcrumb":{"parent":"Email","child":"Mail Inbox"}}
    return render(request,'email/email_app/email_inbox.html',context)


@login_required(login_url="/login")
def email_read_mail(request):
    context={"breadcrumb":{"parent":"Email","child":"Read Mail"}}
    return render(request,'email/read_mail/email_read.html',context)


@login_required(login_url="/login")
def email_email_compose(request):
    context={"breadcrumb":{"parent":"Email","child":"Email Compose"}}
    return render(request,'email/email_compose/email_compose.html',context)

# chat views 


@login_required(login_url="/login")
def chat_chat_app(request):
    context={"breadcrumb":{"parent":"Chat","child":"Chat App"}}
    return render(request,'chat/chat_app/chat.html',context)


@login_required(login_url="/login")
def chat_video_chat(request):
    context={"breadcrumb":{"parent":"Chat","child":"Video Chat"}}
    return render(request,'chat/video_chat/chat-video.html',context)

# users views


@login_required(login_url="/login")
def users_users_profile(request):
    context={"breadcrumb":{"parent":"Users","child":"User Profile"}}
    return render(request,'users/users_profile/user-profile.html',context)


@login_required(login_url="/login")
def users_users_edit(request):
    context={"breadcrumb":{"parent":"Users","child":"User Edit"}}
    return render(request,'users/users_edit/edit-profile.html',context)


@login_required(login_url="/login")
def users_users_card(request):
    context={"breadcrumb":{"parent":"Users","child":"User Cards"}}
    return render(request,'users/users_cards/user-cards.html',context)

# bookmarks views


@login_required(login_url="/login")
def bookmarks(request):
    context={"breadcrumb":{"parent":"Apps","child":"Bookmarks"}}
    return render(request,'bookmarks/bookmark.html',context)

# contacts views


@login_required(login_url="/login")
def contacts(request):
    context={"breadcrumb":{"parent":"Apps","child":"Contact"}}
    return render(request,'contacts/contacts.html',context)

# task views


@login_required(login_url="/login")
def tasks(request):
    context={"breadcrumb":{"parent":"Apps","child":"Task"}}
    return render(request,'tasks/task.html',context)

# calendar views


@login_required(login_url="/login")
def calendar(request):
    context={"breadcrumb":{"parent":"Calendar","child":"Calendar Basic"}}
    return render(request,'calendar/calendar-basic.html',context)

# social app views


@login_required(login_url="/login")
def social_app(request):
    context={"breadcrumb":{"parent":"Apps","child":"Social App"}}
    return render(request,'social_app/social-app.html',context)

# to do views


@login_required(login_url="/login")
def to_do_design(request):
    context={"breadcrumb":{"parent":"Apps","child":"To Do"}}
    return render(request,'to_do/to-do.html',context)


@login_required(login_url="/login")
def to_do_database(request):

    tasks = Task.objects.all()

    form = TaskForm()
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/to_do_database')

    completedTasks = True
    for t in tasks:
        if t.complete == False:
            completedTasks = False

    context = {'tasks': tasks, 'form': form,'completedTasks': completedTasks, "breadcrumb":{"parent":"Todo", "child":"Todo with database"}}
    context = {'tasks': tasks, 'form': form,'completedTasks': completedTasks, "breadcrumb":{"parent":"Todo", "child":"Todo with database"}}

    return render(request,'to_do_database/to-do-database.html',context)
    

@login_required(login_url="/login")
def markAllComplete(request):
    allTasks = Task.objects.all()
    for oneTask in allTasks:
        oneTask.complete = True
        oneTask.save()
    return HttpResponseRedirect("/to_do_database")



@login_required(login_url="/login")
def markAllIncomplete(request):
    allTasks = Task.objects.all()
    for oneTask in allTasks:
        oneTask.complete = False
        oneTask.save()
    return HttpResponseRedirect("/to_do_database")



@login_required(login_url="/login")
def deleteTask(request, pk):
    item = Task.objects.get(id=pk)
    
    #if request.method == "POST":
    item.delete()
    return HttpResponseRedirect("/to_do_database")



@login_required(login_url="/login")
def updateTask(request, pk):
    task = Task.objects.get(id=pk)
    if task.complete == False:
        task.complete = True
        task.save()
    else:
        task.complete = False
        task.save()

    return HttpResponseRedirect("/to_do_database")

# forms views


@login_required(login_url="/login")
def form_form_validation(request):
    context={"breadcrumb":{"parent":"Form Controls","child":"Form validation"}}
    return render(request,'forms/form_controls/form_validation/form-validation.html',context)


@login_required(login_url="/login")
def form_base_inputs(request):
    context={"breadcrumb":{"parent":"Form Controls","child":"Base Inputs"}}
    return render(request,'forms/form_controls/base_inputs/base-input.html',context)


@login_required(login_url="/login")
def checkbox_and_radio(request):
    context={"breadcrumb":{"parent":"Form Controls","child":"Checkbox & Radio"}}
    return render(request,'forms/form_controls/checkbox_and_radio/radio-checkbox-control.html',context)


@login_required(login_url="/login")
def input_groups(request):
    context={"breadcrumb":{"parent":"Form Controls","child":"Input Groups"}}
    return render(request,'forms/form_controls/input_groups/input-group.html',context)


@login_required(login_url="/login")
def mega_options(request):
    context={"breadcrumb":{"parent":"Form Controls","child":"Mega Options"}}
    return render(request,'forms/form_controls/mega_options/megaoptions.html',context)


@login_required(login_url="/login")
def datepicker(request):
    context={"breadcrumb":{"parent":"Form Widgets","child":"Datepicker"}}
    return render(request,'forms/form_widgets/datepicker/datepicker.html',context)


@login_required(login_url="/login")
def timepicker(request):
    context={"breadcrumb":{"parent":"Form Widgets","child":"Timepicker"}}
    return render(request,'forms/form_widgets/timepicker/time-picker.html',context)


@login_required(login_url="/login")
def datetimepicker(request):
    context={"breadcrumb":{"parent":"Form Widgets","child":"Date & Time"}}
    return render(request,'forms/form_widgets/dateTimePicker/datetimepicker.html',context)


@login_required(login_url="/login")
def daterangepicker(request):
    context={"breadcrumb":{"parent":"Form Widgets","child":"Date Range"}}
    return render(request,'forms/form_widgets/dateRangePicker/daterangepicker.html',context)


@login_required(login_url="/login")
def touchspin(request):
    context={"breadcrumb":{"parent":"Form Widgets","child":"Touchspin"}}
    return render(request,'forms/form_widgets/touchspin/touchspin.html',context)


@login_required(login_url="/login")
def select2(request):
    context={"breadcrumb":{"parent":"Form Widgets","child":"Select2"}} 
    return render(request,'forms/form_widgets/select2/select2.html',context)


@login_required(login_url="/login")
def switch(request):
    context={"breadcrumb":{"parent":"Form Widgets","child":"Switch"}}
    return render(request,'forms/form_widgets/switch/switch.html',context)


@login_required(login_url="/login")
def typeahead(request):
    context={"breadcrumb":{"parent":"Form Widgets","child":"Typehead"}}
    return render(request,'forms/form_widgets/typeahead/typeahead.html',context)


@login_required(login_url="/login")
def clipboard(request):
    context={"breadcrumb":{"parent":"Form Widgets","child":"Clipboard"}}
    return render(request,'forms/form_widgets/clipboard/clipboard.html',context)


@login_required(login_url="/login")
def default_form(request):
    context={"breadcrumb":{"parent":"Form Layout","child":"Default Forms"}}
    return render(request,'forms/form_layout/default_forms/default-form.html',context)


@login_required(login_url="/login")
def form_wizard_1(request):
    context={"breadcrumb":{"parent":"Form Layout","child":"Form Wizard"}}
    return render(request,'forms/form_layout/form_wizard_1/form-wizard.html',context)


@login_required(login_url="/login")
def form_wizard_2(request):
    context={"breadcrumb":{"parent":"Form Layout","child":"Form Wizard"}}
    return render(request,'forms/form_layout/form_wizard_2/form-wizard-two.html',context)


@login_required(login_url="/login")
def form_wizard_3(request):
    context={"breadcrumb":{"parent":"Form Layout","child":"Form Wizard"}}
    return render(request,'forms/form_layout/form_wizard_3/form-wizard-three.html',context)

# tables views

# bootstrap tables


@login_required(login_url="/login")
def bootstrap_basic_tables(request):
    context={"breadcrumb":{"parent":"Bootstrap Tables","child":"Basic Tables"}}
    return render(request,'tables/bootstrap_tables/basic_tables/bootstrap-basic-table.html',context)


@login_required(login_url="/login")
def bootstrap_border_tables(request):
    context={"breadcrumb":{"parent":"Bootstrap Tables","child":"Border tables"}}
    return render(request,'tables/bootstrap_tables/border_tables/bootstrap-border-table.html',context)


@login_required(login_url="/login")
def bootstrap_sizing_tables(request):
    context={"breadcrumb":{"parent":"Bootstrap Tables","child":"Sizing Tables"}}
    return render(request,'tables/bootstrap_tables/sizing_tables/bootstrap-sizing-table.html',context)


@login_required(login_url="/login")
def bootstrap_styling_tables(request):
    context={"breadcrumb":{"parent":"Bootstrap Tables","child":"Styling Tables"}}
    return render(request,'tables/bootstrap_tables/styling_tables/bootstrap-styling-table.html',context)


@login_required(login_url="/login")
def bootstrap_table_components(request):
    context={"breadcrumb":{"parent":"Bootstrap Tables","child":"Table Components"}}
    return render(request,'tables/bootstrap_tables/table_components/table-components.html',context)

# data tables 


@login_required(login_url="/login")
def data_tables_advance_init(request):
    context={"breadcrumb":{"parent":"Data Tables","child":"Advance Data Tables"}}
    return render(request,'tables/data_tables/advance_init/datatable-advance.html',context)


@login_required(login_url="/login")
def data_tables_AJAX(request):
    context={"breadcrumb":{"parent":"Data Tables","child":"Ajax Data Tables"}}
    return render(request,'tables/data_tables/AJAX/datatable-AJAX.html',context)


@login_required(login_url="/login")
def data_tables_API(request):
    context={"breadcrumb":{"parent":"Data Tables","child":"API Data Tables"}}
    return render(request,'tables/data_tables/API/datatable-API.html',context)


@login_required(login_url="/login")
def data_tables_basic_init(request):
    context={"breadcrumb":{"parent":"Data Tables","child":"Basic DataTables"}}
    return render(request,'tables/data_tables/basic_init/datatable-basic-init.html',context)


@login_required(login_url="/login")
def data_tables_data_source(request):
    context={"breadcrumb":{"parent":"Data Tables","child":"DATA Source DataTables"}}
    return render(request,'tables/data_tables/data_source/datatable-data-source.html',context)


@login_required(login_url="/login")
def data_tables_plug_in(request):
    context={"breadcrumb":{"parent":"Data Tables","child":"Plugin DataTable"}}
    return render(request,'tables/data_tables/plug_in/datatable-plugin.html',context)


@login_required(login_url="/login")
def data_tables_server_side(request):
    context={"breadcrumb":{"parent":"Data Tables","child":"Server Side DataTable"}}
    return render(request,'tables/data_tables/server_side/datatable-server-side.html',context)


@login_required(login_url="/login")
def data_tables_styling(request):
    context={"breadcrumb":{"parent":"Data Tables","child":"Styling DataTables"}}
    return render(request,'tables/data_tables/styling/datatable-styling.html',context)

# ex datatables


@login_required(login_url="/login")
def ex_data_tables_auto_fill(request):
    context={"breadcrumb":{"parent":"Extension Data Tables","child":"Autofill Datatables"}}
    return render(request,'tables/ex_data_tables/auto_fill/datatable-ext-autofill.html',context)


@login_required(login_url="/login")
def ex_data_tables_basic_button(request):
    context={"breadcrumb":{"parent":"Extension Data Tables","child":"Basic Button"}}
    return render(request,'tables/ex_data_tables/basic_button/datatable-ext-basic-button.html',context)


@login_required(login_url="/login")
def ex_data_tables_column_reorder(request):
    context={"breadcrumb":{"parent":"Extension Data Tables","child":"Column Reorder"}}
    return render(request,'tables/ex_data_tables/column_reorder/datatable-ext-col-reorder.html',context)


@login_required(login_url="/login")
def ex_data_tables_fixed_header(request):
    context={"breadcrumb":{"parent":"Extension Data Tables","child":"Fixed Header"}}
    return render(request,'tables/ex_data_tables/fixed_header/datatable-ext-fixed-header.html',context)


@login_required(login_url="/login")
def ex_data_tables_html_5_export(request):
    context={"breadcrumb":{"parent":"Extension Data Tables","child":"HTML 5 Data Export"}}
    return render(request,'tables/ex_data_tables/html_5_export/datatable-ext-html-5-data-export.html',context)


@login_required(login_url="/login")
def ex_data_tables_key_table(request):
    context={"breadcrumb":{"parent":"Extension Data Tables","child":"Key Table"}}
    return render(request,'tables/ex_data_tables/key_table/datatable-ext-key-table.html',context)


@login_required(login_url="/login")
def ex_data_tables_responsive(request):
    context={"breadcrumb":{"parent":"Extension Data Tables","child":"Responsive Datatables"}}
    return render(request,'tables/ex_data_tables/responsive/datatable-ext-responsive.html',context)


@login_required(login_url="/login")
def ex_data_tables_row_reorder(request):
    context={"breadcrumb":{"parent":"Extension Data Tables","child":"Row Reorder"}}
    return render(request,'tables/ex_data_tables/row_reorder/datatable-ext-row-reorder.html',context)


@login_required(login_url="/login")
def ex_data_tables_scroller(request):
    context={"breadcrumb":{"parent":"Extension Data Tables","child":"Scroller"}}
    return render(request,'tables/ex_data_tables/scroller/datatable-ext-scroller.html',context)

# js grid table


@login_required(login_url="/login")
def js_grid_table(request):
    context={"breadcrumb":{"parent":"Tables","child":"JS Grid Tables"}}
    return render(request,'tables/js_grid_table/jsgrid-table.html',context)

# ui kits views


@login_required(login_url="/login")
def ui_kits_accordion(request):
    context={"breadcrumb":{"parent":"Ui Kits","child":"Accordion"}}
    return render(request,'ui_kits/according.html',context)


@login_required(login_url="/login")
def ui_kits_alert(request):
    context={"breadcrumb":{"parent":"Ui Kits","child":"Alert"}}
    return render(request,'ui_kits/alert.html',context)


@login_required(login_url="/login")
def ui_kits_avatars(request):
    context={"breadcrumb":{"parent":"Ui Kits","child":"Avatars"}}
    return render(request,'ui_kits/avatars.html',context)


@login_required(login_url="/login")
def ui_kits_dropdown(request):
    context={"breadcrumb":{"parent":"Ui Kits","child":"Dropdown"}}
    return render(request,'ui_kits/dropdown.html',context)


@login_required(login_url="/login")
def ui_kits_grid(request):
    context={"breadcrumb":{"parent":"Ui Kits","child":"Grid"}}
    return render(request,'ui_kits/grid.html',context)


@login_required(login_url="/login")
def ui_kits_helper_classes(request):
    context={"breadcrumb":{"parent":"Ui Kits","child":"Helper Classes"}}
    return render(request,'ui_kits/helper-classes.html',context)


@login_required(login_url="/login")
def ui_kits_list(request):
    context={"breadcrumb":{"parent":"Ui Kits","child":"List"}}
    return render(request,'ui_kits/list.html',context)


@login_required(login_url="/login")
def ui_kits_loader(request):
    context={"breadcrumb":{"parent":"Ui Kits","child":"Loader"}}
    return render(request,'ui_kits/loader.html',context)


@login_required(login_url="/login")
def ui_kits_modal(request):
    context={"breadcrumb":{"parent":"Ui Kits","child":"Modal"}}
    return render(request,'ui_kits/modal.html',context)


@login_required(login_url="/login")
def ui_kits_popover(request):
    context={"breadcrumb":{"parent":"Ui Kits","child":"Popover"}}
    return render(request,'ui_kits/popover.html',context)


@login_required(login_url="/login")
def ui_kits_progress_bar(request):
    context={"breadcrumb":{"parent":"Ui Kits","child":"Progress Bar"}}
    return render(request,'ui_kits/progress-bar.html',context)


@login_required(login_url="/login")
def ui_kits_state_color(request):
    context={"breadcrumb":{"parent":"Ui Kits","child":"State Color"}}
    return render(request,'ui_kits/state-color.html',context)


@login_required(login_url="/login")
def ui_kits_tag_pills(request):
    context={"breadcrumb":{"parent":"Ui Kits","child":"Tag Pills"}}
    return render(request,'ui_kits/tag-pills.html',context)


@login_required(login_url="/login")
def ui_kits_box_shadow(request):
    context={"breadcrumb":{"parent":"Ui Kits","child":"Shadow"}}
    return render(request,'ui_kits/box-shadow.html',context)


@login_required(login_url="/login")
def ui_kits_tooltip(request):
    context={"breadcrumb":{"parent":"Ui Kits","child":"Tooltip"}}
    return render(request,'ui_kits/tooltip.html',context)


@login_required(login_url="/login")
def ui_kits_typography(request):
    context={"breadcrumb":{"parent":"Ui Kits","child":"Typography"}}
    return render(request,'ui_kits/typography.html',context)

# ui kits tabs views


@login_required(login_url="/login")
def ui_kits_tabs_bootstrap(request):
    context={"breadcrumb":{"parent":"Tabs","child":"Bootstrap Tabs"}}
    return render(request,'ui_kits//tabs/tab-bootstrap.html',context)


@login_required(login_url="/login")
def ui_kits_tabs_line(request):
    context={"breadcrumb":{"parent":"Tabs","child":"Line"}}
    return render(request,'ui_kits//tabs/tab-material.html',context)


# bonus ui views


@login_required(login_url="/login")
def bonus_ui_basic_card(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Basic Card"}}
    return render(request,'bonus_ui/basic-card/basic-card.html',context)


@login_required(login_url="/login")
def bonus_ui_bootstrap_notify(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Bootstrap Notify"}}
    return render(request,'bonus_ui/bootstrap-notify/bootstrap-notify.html',context)


@login_required(login_url="/login")
def bonus_ui_breadcrumb(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Breadcrumb"}}
    return render(request,'bonus_ui/breadcrumb/breadcrumb.html',context)


@login_required(login_url="/login")
def bonus_ui_creative_card(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Creative card"}}
    return render(request,'bonus_ui/creative-card/creative-card.html',context)


@login_required(login_url="/login")
def bonus_ui_dragable_card(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Dragable Card"}}
    return render(request,'bonus_ui/dragable-card/dragable-card.html',context)


@login_required(login_url="/login")
def bonus_ui_dropzone(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Dropzone"}}
    return render(request,'bonus_ui/dropzone/dropzone.html',context)


@login_required(login_url="/login")
def bonus_ui_image_cropper(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Image Cropper"}}
    return render(request,'bonus_ui/image-cropper/image-cropper.html',context)


@login_required(login_url="/login")
def bonus_ui_modal_animated(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Modal Animated"}}
    return render(request,'bonus_ui/modal-animated/modal-animated.html',context)


@login_required(login_url="/login")
def bonus_ui_owl_carousel(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Owl Corousel"}}
    return render(request,'bonus_ui/owl-carousel/owl-carousel.html',context)


@login_required(login_url="/login")
def bonus_ui_pagination(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Pagination"}}
    return render(request,'bonus_ui/pagination/pagination.html',context)


@login_required(login_url="/login")
def bonus_ui_range_slider(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Range Slider"}}
    return render(request,'bonus_ui/range-slider/range-slider.html',context)


@login_required(login_url="/login")
def bonus_ui_rating(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Rating"}}
    return render(request,'bonus_ui/rating/rating.html',context)


@login_required(login_url="/login")
def bonus_ui_ribbons(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Ribbons"}}
    return render(request,'bonus_ui/ribbons/ribbons.html',context)


@login_required(login_url="/login")
def bonus_ui_scrollable(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Scrollable"}}
    return render(request,'bonus_ui/scrollable/scrollable.html',context)


@login_required(login_url="/login")
def bonus_ui_steps(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Steps"}}
    return render(request,'bonus_ui/steps/steps.html',context)


@login_required(login_url="/login")
def bonus_ui_sticky(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Sticky"}}
    return render(request,'bonus_ui/sticky/sticky.html',context)


@login_required(login_url="/login")
def bonus_ui_sweet_alert2(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Sweet Alert 2"}}
    return render(request,'bonus_ui/sweet-alert2/sweet-alert2.html',context)


@login_required(login_url="/login")
def bonus_ui_tabbed_card(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Tabbed Card"}}
    return render(request,'bonus_ui/tabbed-card/tabbed-card.html',context)


@login_required(login_url="/login")
def bonus_ui_tour(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Tour"}}
    return render(request,'bonus_ui/tour/tour.html',context)


@login_required(login_url="/login")
def bonus_ui_tree(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Tree"}}
    return render(request,'bonus_ui/tree/tree.html',context)

    # bonus ui timeline 


@login_required(login_url="/login")
def bonus_ui_timeline_1(request):
    context={"breadcrumb":{"parent":"Timeline","child":"Timeline 1"}}
    return render(request,'bonus_ui/timeline/timeline-v-1.html',context)


@login_required(login_url="/login")
def bonus_ui_timeline_2(request):
    context={"breadcrumb":{"parent":"Timeline","child":"Timeline 2"}}
    return render(request,'bonus_ui/timeline/timeline-v-2.html',context)

# builders  views


@login_required(login_url="/login")
def button_builder(request):
    context={"breadcrumb":{"parent":"Builders","child":"Button Builder"}}
    return render(request,'builders/button-builder/button-builder.html',context)
    

@login_required(login_url="/login")
def form_builder_1(request):
    context={"breadcrumb":{"parent":"Builders","child":"Form Builder 1"}}
    return render(request,'builders/form-builder-1/form-builder-1.html',context)
    

@login_required(login_url="/login")
def form_builder_2(request):
    context={"breadcrumb":{"parent":"Builders","child":"Form Builder 2"}}
    return render(request,'builders/form-builder-2/form-builder-2.html',context)
    

@login_required(login_url="/login")
def page_builder(request):
    context={"breadcrumb":{"parent":"Builders","child":"Page Builder"}}
    return render(request,'builders/pagebuild/pagebuild.html',context)


# animation views


@login_required(login_url="/login")
def animate(request):
    context={"breadcrumb":{"parent":"Animation","child":"Animate"}}
    return render(request,'animation/animate/animate.html',context)


@login_required(login_url="/login")
def scroll_reveal(request):
    context={"breadcrumb":{"parent":"Animation","child":"Scroll Reveal"}}
    return render(request,'animation/scroll-reval/scroll-reval.html',context)


@login_required(login_url="/login")
def AOS_animation(request):
    context={"breadcrumb":{"parent":"Animation","child":"AOS Animation"}}
    return render(request,'animation/AOS/AOS.html',context)


@login_required(login_url="/login")
def tilt_animation(request):
    context={"breadcrumb":{"parent":"Animation","child":"Tilt Animation"}} 
    return render(request,'animation/tilt/tilt.html',context)


@login_required(login_url="/login")
def wow_animation(request):
    context={"breadcrumb":{"parent":"Animation","child":"Wow Animation"}}
    return render(request,'animation/wow/wow.html',context)

# icons views


@login_required(login_url="/login")
def flag_icon(request):
    context={"breadcrumb":{"parent":"Icons","child":"Flag Icons"}}
    return render(request,'icons/flag-icon/flag-icon.html',context)


@login_required(login_url="/login")
def fontawesome_icon(request):
    context={"breadcrumb":{"parent":"Icons","child":"Fontawesome Icons"}}
    return render(request,'icons/font-awesome/font-awesome.html',context)


@login_required(login_url="/login")
def ico_icon(request):
    context={"breadcrumb":{"parent":"Icons","child":"ICO Icons"}}
    return render(request,'icons/ico-icon/ico-icon.html',context)


@login_required(login_url="/login")
def thimify_icon(request):
    context={"breadcrumb":{"parent":"Icons","child":"Themify Icons"}}
    return render(request,'icons/themify-icon/themify-icon.html',context)


@login_required(login_url="/login")
def feather_icon(request):
    context={"breadcrumb":{"parent":"Icons","child":"Feather Icons"}}
    return render(request,'icons/feather-icon/feather-icon.html',context)


@login_required(login_url="/login")
def whether_icon(request):
    context={"breadcrumb":{"parent":"Icons","child":"Weather Icon"}}
    return render(request,'icons/whether-icon/whether-icon.html',context)

# buttons views


@login_required(login_url="/login")
def buttons(request):
    context={"breadcrumb":{"parent":"Buttons","child":"Default Style"}}
    return render(request,'buttons/buttons/buttons.html',context)

@login_required(login_url="/login")
def buttons_flat(request):
    context={"breadcrumb":{"parent":"Buttons","child":"Button-flat"}}
    return render(request,'buttons/buttons-flat/buttons-flat.html',context)

@login_required(login_url="/login")
def buttons_edge(request):
    context={"breadcrumb":{"parent":"Buttons","child":"Button-Edge"}}
    return render(request,'buttons/buttons-edge/buttons-edge.html',context)

@login_required(login_url="/login")
def raised_button(request):
    context={"breadcrumb":{"parent":"Buttons","child":"Raised-Buttons"}}
    return render(request,'buttons/raised-button/raised-button.html',context)

@login_required(login_url="/login")
def button_group(request):
    context={"breadcrumb":{"parent":"Buttons","child":"Button-Group"}}
    return render(request,'buttons/button-group/button-group.html',context)

# charts views


@login_required(login_url="/login")
def apex_chart(request):
    context={"breadcrumb":{"parent":"charts","child":"Apex Chart"}}
    return render(request,'charts/chart-apex/chart-apex.html',context)


@login_required(login_url="/login")
def google_chart(request):
    context={"breadcrumb":{"parent":"charts","child":"Google Chart"}}
    return render(request,'charts/chart-google/chart-google.html',context)


@login_required(login_url="/login")
def sparkline_chart(request):
    context={"breadcrumb":{"parent":"charts","child":"Spakline Chart"}}
    return render(request,'charts/chart-sparkline/chart-sparkline.html',context)


@login_required(login_url="/login")
def flot_chart(request):
    context={"breadcrumb":{"parent":"charts","child":"Flot Chart"}}
    return render(request,'charts/chart-flot/chart-flot.html',context)


@login_required(login_url="/login")
def knob_chart(request):
    context={"breadcrumb":{"parent":"charts","child":"Know Chart"}}
    return render(request,'charts/chart-knob/chart-knob.html',context)


@login_required(login_url="/login")
def morris_chart(request):
    context={"breadcrumb":{"parent":"charts","child":"Morris Chart"}}
    return render(request,'charts/chart-morris/chart-morris.html',context)


@login_required(login_url="/login")
def chartjs(request):
    context={"breadcrumb":{"parent":"charts","child":"ChartJS Chart"}}
    return render(request,'charts/chartjs/chartjs.html',context)


@login_required(login_url="/login")
def chartist(request):
    context={"breadcrumb":{"parent":"charts","child":"Chartist Chart"}}
    return render(request,'charts/chartist/chartist.html',context)


@login_required(login_url="/login")
def peity_chart(request):
    context={"breadcrumb":{"parent":"charts","child":"Peity Chart"}}
    return render(request,'charts/chart-peity/chart-peity.html',context)

# landing page view


@login_required(login_url="/login")
def landing_page(request):
    return render(request,'landing_page/landing-page.html')

# sample page view


@login_required(login_url="/login")
def sample_page(request):
    context={"breadcrumb":{"parent":"Pages","child":"Sample Page"}}
    return render(request,'sample_page/sample-page.html',context)

# internationalization  view


@login_required(login_url="/login")
def internationalization(request):
    context={"breadcrumb":{"parent":"Pages","child":"Internationalization"}}
    return render(request,'internationalization/internationalization.html',context)

# starter kit  view


@login_required(login_url="/login")
def starter_kit(request):
    context={"breadcrumb":{"parent":"Color Version","child":"Layout Light"}}
    return render(request,'starter_kit/index.html',context)


@login_required(login_url="/login")
def starter_layout_dark(request):
    context={"breadcrumb":{"parent":"Color Version","child":"Layout Dark"},"layout":"dark-only"}
    return render(request,'starter_kit/layout-dark.html',context)


@login_required(login_url="/login")
def starter_box_layout(request):
    context={"breadcrumb":{"parent":"Page Layout","child":"Boxed"},"layout":"box-layout"}
    return render(request,'starter_kit/boxed.html',context)


@login_required(login_url="/login")
def starter_RTL(request):
    context={"breadcrumb":{"parent":"Page Layout","child":"RTL"},"layout":"rtl"}
    return render(request,'starter_kit/layout-rtl.html',context)


@login_required(login_url="/login")
def starter_footer_light(request):
    context={"breadcrumb":{"parent":"Footers","child":"Footer Light"}}
    return render(request,'starter_kit/footer-light.html',context)


@login_required(login_url="/login")
def starter_footer_dark(request):
    context={"breadcrumb":{"parent":"Footers","child":"Footer Dark"},"footer":"footer-dark"}
    return render(request,'starter_kit/footer-dark.html',context)


@login_required(login_url="/login")
def starter_footer_fixed(request):
    context={"breadcrumb":{"parent":"Footers","child":"Footer fixed"},"footer":"footer-fix"}
    return render(request,'starter_kit/footer-fixed.html',context)

# others view

    # error pages


@login_required(login_url="/login")
def error_page_1(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/error_page/error-page1/error-page1.html',context)


@login_required(login_url="/login")
def error_page_2(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/error_page/error-page2/error-page2.html',context)


@login_required(login_url="/login")
def error_page_3(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/error_page/error-page3/error-page3.html',context)


@login_required(login_url="/login")
def error_page_4(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/error_page/error-page4/error-page4.html',context)

    # authentication 

def login_simple(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            if 'next' in request.GET:
                nextPage = request.GET['next']
                return HttpResponseRedirect(nextPage)
            else:
                return redirect('dashboard_default')
    else:
        form =AuthenticationForm()
    context={"breadcrumb":{"parent":"parent","child":"child"},"form":form}
    return render(request,'others/authentication/login/login.html',context)


def logout_view(request):
    logout(request)
    return redirect('login?next=/')

def login_with_bg_image(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/authentication/login-one/login_one.html',context)

def login_with_image_two(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/authentication/login-two/login_two.html',context)

def login_with_validation(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/authentication/login-bs-validation/login-bs-validation.html',context)

def login_with_tooltip(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/authentication/login-bs-tt-validation/login-bs-tt-validation.html',context)

def login_with_sweetalert(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/authentication/login-sa-validation/login-sa-validation.html',context)

def register_simple(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('dashboard_ecommerce')
    else:
        form = UserCreationForm()
    
    return render(request,'others/authentication/sign-up/sign-up.html',{"form":form})

def register_with_bg_image(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/authentication/sign-up-one/sign-up-one.html',context)

def register_with_bg_video(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/authentication/sign-up-two/sign-up-two.html',context)


def unlock_user(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/authentication/unlock/unlock.html',context)


def forget_password(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/authentication/forget-password/forget-password.html',context)


def create_password(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/authentication/create-password/creat-password.html',context)


def maintenance(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/authentication/maintenance/maintenance.html',context)



    # coming soon views


@login_required(login_url="/login")
def coming_simple(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/coming_soon/comingsoon/comingsoon.html',context)


@login_required(login_url="/login")
def coming_with_bg_image(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/coming_soon/comingsoon-bg-img/comingsoon-bg-img.html',context)

@login_required(login_url="/login")
def coming_with_bg_video(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/coming_soon/comingsoon-bg-video/comingsoon-bg-video.html',context)

    # email templates views


@login_required(login_url="/login")
def basic_email(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/email_templates/basic-template.html',context)


@login_required(login_url="/login")
def basic_with_header(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/email_templates/email-header.html',context)


@login_required(login_url="/login")
def email_template(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/email_templates/template-email.html',context)

@login_required(login_url="/login")
def email_template_2(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/email_templates/template-email-2.html',context)


@login_required(login_url="/login")
def ecommerce_email(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/email_templates/ecommerce-templates.html',context)


@login_required(login_url="/login")
def order_success(request):
    context={"breadcrumb":{"parent":"parent","child":"child"}}
    return render(request,'others/email_templates/email-order-success.html',context)


# gallery views


@login_required(login_url="/login")
def gallery_grid(request):
    context={"breadcrumb":{"parent":"Gallery","child":"Gallery Grid"}}
    return render(request,'gallery/gallery_grid/gallery.html',context)


@login_required(login_url="/login")
def gallery_grid_desc(request):
    context={"breadcrumb":{"parent":"Gallery","child":"Gallery Grid With Description"}}
    return render(request,'gallery/gallery_grid_desc/gallery-with-description.html',context)


@login_required(login_url="/login")
def masonry_gallery(request):
    context={"breadcrumb":{"parent":"Gallery","child":"Mansory Gallery"}}
    return render(request,'gallery/masonry_gallery/gallery-masonry.html',context)


@login_required(login_url="/login")
def masonry_with_desc(request):
    context={"breadcrumb":{"parent":"Gallery","child":"Mansory Gallery With Description"}}
    return render(request,'gallery/masonry_with_desc/masonry-gallery-with-disc.html',context)


@login_required(login_url="/login")
def hover_effect(request):
    context={"breadcrumb":{"parent":"Gallery","child":"Hover Effect"}}
    return render(request,'gallery/hover_effects/gallery-hover.html',context)

# blog pages views


@login_required(login_url="/login")
def blog_details(request):
    context={"breadcrumb":{"parent":"Blog","child":"Blog Details"}}
    return render(request,'blog/blog_details/blog.html',context)


@login_required(login_url="/login")
def blog_single(request):
    context={"breadcrumb":{"parent":"Blog","child":"Blog Single"}}
    return render(request,'blog/blog_single/blog-single.html',context)


@login_required(login_url="/login")
def add_post(request):
    context={"breadcrumb":{"parent":"Blog","child":"Add Post"}}
    return render(request,'blog/add_post/add-post.html',context)

# FAQ views


@login_required(login_url="/login")
def faq(request):
    context={"breadcrumb":{"parent":"FAQ","child":"FAQ"}}
    return render(request,'faq/faq.html',context)

# job search


@login_required(login_url="/login")
def cards_view(request):
    context={"breadcrumb":{"parent":"Job Search","child":"Cards View"}}
    return render(request,'job_search/cards_view/job-cards-view.html',context)


@login_required(login_url="/login")
def list_view(request):
    context={"breadcrumb":{"parent":"Job Search","child":"List View"}}
    return render(request,'job_search/list_view/job-list-view.html',context)


@login_required(login_url="/login")
def job_details(request):
    context={"breadcrumb":{"parent":"Job Search","child":"Job Details"}}
    return render(request,'job_search/job_details/job-details.html',context)


@login_required(login_url="/login")
def apply(request):
    context={"breadcrumb":{"parent":"Job Search","child":"Apply"}}
    return render(request,'job_search/apply/job-apply.html',context)

# learning views


@login_required(login_url="/login")
def learning_list(request):
    context={"breadcrumb":{"parent":"Learning","child":"Learning List"}}
    return render(request,'learning/learning_list/learning-list-view.html',context)


@login_required(login_url="/login")
def detailed_course(request):
    context={"breadcrumb":{"parent":"Learning","child":"Detailed Course"}}
    return render(request,'learning/detailed_course/learning-detailed.html',context)

# maps views


@login_required(login_url="/login")
def maps_js(request):
    context={"breadcrumb":{"parent":"Maps","child":"Map JS"}}
    return render(request,'maps/maps_js/map-js.html',context)


@login_required(login_url="/login")
def vector_maps(request):
    context={"breadcrumb":{"parent":"Maps","child":"Vector Maps"}}
    return render(request,'maps/vector_maps/vector-map.html',context)

# editors views


@login_required(login_url="/login")
def summer_note(request):
    context={"breadcrumb":{"parent":"Editors","child":"Summer Note"}}
    return render(request,'editors/summer_note/summernote.html',context)


@login_required(login_url="/login")
def ck_editor(request):
    context={"breadcrumb":{"parent":"Editors","child":"Ck Editor"}}
    return render(request,'editors/ck_editor/ckeditor.html',context)


@login_required(login_url="/login")
def mde_editor(request):
    context={"breadcrumb":{"parent":"Editors","child":"MDE Editor"}}
    return render(request,'editors/mde_editor/simple-MDE.html',context)


@login_required(login_url="/login")
def ace_code_editor(request):
    context={"breadcrumb":{"parent":"Editors","child":"ACE Code Editor"}}
    return render(request,'editors/ace_code_editor/ace-code-editor.html',context)

# knowledgebase views


@login_required(login_url="/login")
def knowledgebase(request):
    context={"breadcrumb":{"parent":"Knowledgebase","child":"Knowledgebase"}}
    return render(request,'knowledgebase/knowledgebase/knowledgebase.html',context)


@login_required(login_url="/login")
def knowledge_category(request):
    context={"breadcrumb":{"parent":"Knowledgebase","child":"Knowledge Catagory"}}
    return render(request,'knowledgebase/knowledge_category/knowledge-category.html',context)


@login_required(login_url="/login")
def knowledge_detail(request):
    context={"breadcrumb":{"parent":"Knowledgebase","child":"Knowledge Detail"}}
    return render(request,'knowledgebase/knowledge_detail/knowledge-detail.html',context)

# support ticket


@login_required(login_url="/login")
def support_ticket(request):
    context={"breadcrumb":{"parent":"Apps","child":"Support Ticket"}}
    return render(request,'support_ticket/support-ticket.html',context)

# documentation 


@login_required(login_url="/login")
def documentation_accordian(request):
    return render(request,'documentation/accordian.html')


@login_required(login_url="/login")
def documentation_app(request):
    return render(request,'documentation/app.html')


@login_required(login_url="/login")
def documentation_change_log(request):
    return render(request,'documentation/change-log.html')


@login_required(login_url="/login")
def documentation_component(request):
    return render(request,'documentation/component.html')


@login_required(login_url="/login")
def documentation_customer_review(request):
    return render(request,'documentation/customer-review.html')


@login_required(login_url="/login")
def documentation_feature_list(request):
    return render(request,'documentation/feature-list.html')


@login_required(login_url="/login")
def documentation_getting_started(request):
    return render(request,'documentation/getting-started.html')


@login_required(login_url="/login")
def documentation_index(request):
    return render(request,'documentation/index.html')


@login_required(login_url="/login")
def documentation_layout_setting(request):
    return render(request,'documentation/layout-setting.html')


@login_required(login_url="/login")
def documentation_options(request):
    return render(request,'documentation/options.html')


@login_required(login_url="/login")
def documentation_tree(request):
    return render(request,'documentation/tree.html')


@login_required(login_url="/login")
def documentation_django_to_do(request):
    return render(request,'documentation/django-to-do.html')


@login_required(login_url="/login")
def documentation_django_authentication(request):
    return render(request,'documentation/django-authentication.html')


@login_required(login_url="/login")
def documentation_django_customizer(request):
    return render(request,'documentation/django-customizer.html')


@login_required(login_url="/login")
def documentation_django_components(request):
    return render(request,'documentation/django-component.html')


@login_required(login_url="/login")
def documentation_django_getting_started(request):
    return render(request,'documentation/django-getting-started.html')


@login_required(login_url="/login")
def documentation_django_options(request):
    return render(request,'documentation/django-options.html')

@login_required(login_url="/login")
def documentation_django_tree(request):
    return render(request,'documentation/django-tree.html')

@login_required(login_url="/login")
def documentation_django_app(request):
    return render(request,'documentation/django-app.html')


@login_required(login_url="/login")
def bonus_ui_sweet_alert2(request):
    context={"breadcrumb":{"parent":"Bonus Ui","child":"Sweet Alert 2"}}
    return render(request,'bonus_ui/sweet-alert2/sweet-alert2.html',context)