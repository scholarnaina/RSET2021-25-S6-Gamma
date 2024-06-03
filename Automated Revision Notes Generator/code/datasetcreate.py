import fitz
import nltk
import re
import pandas as pd
import csv
import string
def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    return text.split('\n')  # Split text into lines and return as a list

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
# Example usage:
m1=[]
m2=[]
m3=[]
m4=[]
m5=[]
p1=[]
p2=[]
p3=[]
p4=[]
p5=[]
qcheck=['answer','question','questions','carries','marks','module','each']
pdf_paths = ["1.pdf","4.pdf"]
for pdf_path in pdf_paths:
    all_text_lines = extract_text_from_pdf(pdf_path)
    qno=1
    q_list = ["find_qn_here : ",""]
    flag1=0
    flag2=0
    qn = ""
    for line in all_text_lines:
        if line[0:6].upper() == "PART-A" or line[0:6].upper() == "PART A":
            flag1=1
            continue
        if line[0:6].upper() == "PART-B" or line[0:6].upper() == "PART B":
            flag2=1
            continue
        if flag1==1:
            if flag2==1:
                flag2=0
                continue
            if line == "":
                continue
            if line[0] == str(qno) and qno<=9:
                qn = line[1:].replace("\n", " ")
                q_list.append(qn)
                qno=qno+1
            elif line[0:2] == str(qno) and qno>=10:
                qn = line[2:].replace("\n", " ")
                q_list.append(qn)
                qno=qno+1
            else:
                qn = qn + " " + line.replace("\n", " ")
                q_list[qno] = qn
    #print("total questions is "+str(qno-1))
    q_index = qno
    for qline in q_list:
        text = qline
        pattern = r"[^\w\s_]"  # Matches any character except word characters (alphanumeric), whitespace, and underscore
        clean_text = re.sub(pattern, " ", text)

        q_list[qno-q_index] = clean_text.replace("_","")
        q_list[qno-q_index] = clean_text.replace("\xa0"," ")
        q_index=q_index-1

    for item in q_list:
        if similarity(list(item.split()),qcheck)>0.5:
            q_list.remove(item)
    while q_list.count(''):q_list.remove('')
    module=[]
    priority=[]

    l=0
    default_stopwords = nltk.corpus.stopwords.words('english')
    custom_stopwords = ['one','two','three','four','five','how', 'explain', 'follow','following','consider','ha','describe','yes','happen','given','give','define','term','ii','i','iii','iv','v','vi','vii','viii','ix','x','1','2','3','4','5','6','7','8','9','10']
    stopwords_with_custom = default_stopwords + custom_stopwords
    for i in range(1,6):#to insert qns module wise
        for num in [2*i-1,2*i,2*i+9,2*i+10]:
            tokens = nltk.word_tokenize(q_list[num].lower())
            new_tokens = [token for token in tokens if token not in string.punctuation]
            filtereed_tokens = [token for token in new_tokens if token not in stopwords_with_custom]
            if 'operating' in filtereed_tokens:
                oind=filtereed_tokens.index('operating')
                if oind!=len(filtereed_tokens)-1 and filtereed_tokens[oind+1]=='system':
                    filtereed_tokens[oind:oind+2]=['OS']
            if filtereed_tokens[-1]=='page': filtereed_tokens.pop(-1)
            for z in filtereed_tokens:
                if '_' in z:
                    filtereed_tokens[filtereed_tokens.index(z)]=filtereed_tokens[filtereed_tokens.index(z)].replace('_',"")
            while filtereed_tokens.count(''): filtereed_tokens.remove('') 
            pflag=0
            for k in module:
                if similarity(k,filtereed_tokens)>0.5:
                    ind=module.index(k)
                    priority[ind]+=1
                    if len(filtereed_tokens)>len(module[ind]):
                        module[ind]=filtereed_tokens
                    pflag=1
            if pflag!=1:
                priority.append(1)
                module.append(filtereed_tokens)
            for z in range(len(module)):
                if module[z][-1].isnumeric(): module[z].pop(-1)
        if i == 1:
            for k in module:
                for m in m1:
                    if similarity(k,m)>0.5:
                        ind=module.index(k)
                        priority[ind]+=1
            for k in range(len(module)):
                m1.append(module[k])
                p1.append(priority[k])
            module = []
            priority=[]

        elif i == 2:
            for k in module:
                for m in m2:
                    if similarity(k,m)>0.5:
                        ind=module.index(k)
                        priority[ind]+=1
            for k in range(len(module)):
                m2.append(module[k])
                p2.append(priority[k])
            module = []
            priority=[]
        elif i == 3:
            for k in module:
                for m in m3:
                    if similarity(k,m)>0.5:
                        ind=module.index(k)
                        priority[ind]+=1
            for k in range(len(module)):
                m3.append(module[k])
                p3.append(priority[k])
            module = []
            priority=[]
        elif i == 4:
            for k in module:
                for m in m4:
                    if similarity(k,m)>0.5:
                        ind=module.index(k)
                        priority[ind]+=1
            for k in range(len(module)):
                m4.append(module[k])
                p4.append(priority[k])
            module = []
            priority=[]
        elif i==5:
            for k in module:
                for m in m5:
                    if similarity(k,m)>0.5:
                        ind=module.index(k)
                        priority[ind]+=1
            for k in range(len(module)):
                m5.append(module[k])
                p5.append(priority[k])
            module = []
            priority=[]
        else:
            print("end")

    print("module 1 = ")
    print(m1)
    print(p1)
    print("module 2 = ")
    print(m2)
    print(p2)
    print("module 3 = ")
    print(m3)
    print(p3)
    print("module 4 = ")
    print(m4)
    print(p4)
    print("module 5 = ")
    print(m5)
    print(p5)


def append_to_csv(file_path, column_values):
    with open(file_path, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(column_values)

# Example usage:
csv_file_path = "data.csv"
for token in range(len(m1)):
    new_column_values = ['OS', '01', m1[token],p1[token]]  # Example list of column values
    append_to_csv(csv_file_path, new_column_values)

for token in range(len(m2)):
    new_column_values = ['OS', '02', m2[token],p2[token]]
    append_to_csv(csv_file_path, new_column_values)

for token in range(len(m3)):
    new_column_values = ['OS', '03', m3[token],p3[token]]
    append_to_csv(csv_file_path, new_column_values)

for token in range(len(m4)):
    new_column_values = ['OS', '04', m4[token],p4[token]]
    append_to_csv(csv_file_path, new_column_values)

for token in range(len(m5)):
    new_column_values = ['OS', '05', m5[token],p5[token]]
    append_to_csv(csv_file_path, new_column_values)
