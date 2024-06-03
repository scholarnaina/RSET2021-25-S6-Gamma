import fitz
import pandas as pd
import unidecode
import re
from nltk.stem import WordNetLemmatizer
import google.generativeai as genai
from sentence_transformers import SentenceTransformer, util
def similarity(a,b):
    sim=0
    for k in range(len(b)):
        b[k]=b[k].lower()
    for item in a:
        if item.lower() in b:
            sim+=1
    maxsim=min(len(a),len(b))
    if maxsim==0:
        return 0
    r=sim/maxsim
    return(round(r,2))

def removesp(lst):
    for t in lst:
        tno=len(t)
        t_index=tno
        ind=lst.index(t)
        for tline in t:
            text = tline
            pattern = r"[^\w\s_]"  # Matches any character except word characters (alphanumeric), whitespace, and underscore
            clean_text = re.sub(pattern, " ", text)
            t[tno-t_index] = clean_text.replace("_"," ")
            t_index-=1
        while t.count(''):t.remove('')
        while t.count(' '):t.remove(' ')
        lst[ind]=t
    return lst
def summarizer(fname,modnum):
    if modnum==0:
        module=[1,2,3,4,5]
    else:
        module=[modnum]
    your_api_key = "enter_key_here"
    smodel = SentenceTransformer('all-MiniLM-L6-v2')
    genai.configure(api_key=your_api_key)
    model_name = 'gemini-1.0-pro'   
    model = genai.GenerativeModel(model_name)
    bldict={}
    pg=1
    tot=0
    df=pd.read_csv('data.csv',names=['sub','mod','topic','priority'])
    doc=fitz.open(fname)
    for page in doc:
        text=page.get_text("dict")
        block=text['blocks']
        bldict[pg]=block
        pg+=1
    num=0
    for a in bldict.values():
        for b in a:
            if 'lines' in b.keys():
                tot+=b['lines'][0]['spans'][0]['size']        
                num+=1
    avg=tot/num
    headings=[]
    text=[]
    t=-1
    for a in bldict.values():
        for b in a:
            if 'lines' not in b.keys():
                continue
            bld=b['lines'][0]['spans'][0]['font'].lower()
            sz=b['lines'][0]['spans'][0]['size']
            if sz>(avg*1.3) or ('bold' in bld and sz>(avg*1.05)):
                headings.append(b['lines'][0]['spans'][0]['text'].lower())
                t+=1
                text.append('')
            elif t>=0 and sz>avg*0.6:
                text[t]+=b['lines'][0]['spans'][0]['text'].lower()
    modcheck=['module','1','2','3','4','5','module1','module2','module3','module4','module5']
    for g in headings:
        if similarity(list(g.split()),modcheck)>0.9:
            ind=headings.index(g)
            headings.pop(ind)
            text.pop(ind)
    count=0
    scores={'heading':[],'score':[]}
    for text1 in df[df['mod'].isin(module)]['topic']:
        i=0
        for text2 in headings:
            embedding1 = smodel.encode(text1)
            embedding2 = smodel.encode(text2)   
            similar=  util.cos_sim(embedding1, embedding2)
            scores['heading'].append(text2)
            scores['score'].append(text1)
    combined = list(zip(scores['heading'], scores['score']))
    sorted_combined = sorted(combined, key=lambda x: x[1],reverse=True)
    sorted_headings, sorted_scores = zip(*sorted_combined)
    scores['heading'] = list(sorted_headings)
    scores['score'] = list(sorted_scores)
    notes=""
    for k in scores['heading'][:5]:
        ind=headings.index(k)
        notes+=k+':'+text[ind]+';'
    query="make a short summary of given text into bullet points in such a way that a ktu btech student can revise this topic in the last minute. Avoid using the module number. Add at least one explanation for each point. Here are the notes: "+notes
    response = model.generate_content(query)
    summary=response.text
    return summary