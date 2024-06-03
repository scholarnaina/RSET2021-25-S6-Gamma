import pandas as pd
import numpy as np
import joblib
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
df=pd.read_csv("dataset.csv")
print(df)
x = df.iloc[:, 1:-1]
#print(x)# Select columns from index 1 (inclusive) to -1 (exclusive)
y=df.iloc[:,-1]
x_train,x_test,y_train,y_test=train_test_split(x,y,random_state=42)
clf=RandomForestClassifier(criterion="gini",max_depth=8,min_samples_split=10,random_state=5)
clf.fit(x,y)
y_pred=clf.predict(x_test)#print(y_pred)
m=accuracy_score(y_test,y_pred)
print(clf.feature_importances_)
print("y",y_test)
joblib.dump(clf,'mymodel.pkl')
print(y_pred)
print(m*100)