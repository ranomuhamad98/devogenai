import math

def spredConf(data_out):
    list_out = []
    for data in data_out.split(' '):
        list_out.append(data.split('_')[0])
    return ' '.join(list_out)

def rougueLiteTest(response,spander):
    result = response['result']
    if result != 'not found':
        for i in response.keys():
            if i != 'result':
                for r in range(len(result.split(' ')),0,-1):
                    for s in range(math.ceil(len(result.split(' '))/r)):
                        r_check = ' '.join(result.split(' ')[s:r+s])
                        try:
                            instart = response[i].split(' ').index(r_check)
                            instend = 0
                            if instart+spander>=len(response[i].split(' ')):
                                instend = len(response[i].split(' '))-1
                            else:
                                instend = instart+spander
                                
                            if instart-spander<0:
                                instart = 0
                            else:
                                instart -=spander
                            return response[i].split(' ')[instart:instend],1
                        except:
                            pass
    return response['Doc0'].split(' '),0

def formatConfi(data_out):
    list_out = []
    for data in data_out.split(' '):
        if data != '':
            dtext = data.split('_')
            dcon = float(dtext[-1])
            dtext = dtext[0]
            if dcon>0.95:
                list_out.append(' '+dtext)
            elif dcon>0.7:
                list_out.append((' '+dtext,"","#fbec5d"))
            else:
                list_out.append((' '+dtext,"","#faa"))
    return  list_out

def Under_Tresh_Count(data_out):
    GoodData = 0
    LenData = 0
    for data in data_out.split(' '):
        if data != '':
            dtext = data.split('_')
            dcon = float(dtext[-1])
            dtext = dtext[0]
            if dcon>0.95:
                GoodData+=1
            LenData+=1
    return  str(GoodData/LenData)