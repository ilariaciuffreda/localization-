import pandas as pd 
from sklearn import tree 
from sklearn import metrics
from sklearn.tree import plot_tree 
from sklearn.model_selection import cross_val_score 
from itertools import groupby
from itertools import product
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from scipy import spatial
import matplotlib.pyplot as plt
import numpy as np
import cv2
import pickle


df = pd.read_csv(r"C:\Users\Utente\Downloads\prova_templates_6.0_CORRETTO_NO_B&F.csv", sep =';')
print (df)
df.head()
#indipendent variable 
inputs = df.drop('Result', axis = 'columns')
target = df["Result"]

#model = tree.DecisionTreeClassifier()
X_train, X_test, y_train, y_test = train_test_split (inputs,target,test_size = 0.25,random_state=0)
model = tree.DecisionTreeClassifier()
clf_gini = model.fit(X_train, y_train)
model.score(X_test,  y_test)
y_pred_gini = clf_gini.predict (X_test)
print (classification_report (y_test, y_pred_gini))
labels = ["si","no"]
cm = confusion_matrix(y_test,y_pred_gini )
print(metrics.accuracy_score(y_test,y_pred_gini))
import seaborn as sn 
plt.figure (figsize = (3,3)) 
sn.heatmap ( cm, annot = True )
plt.xlabel('predicted')
plt.ylabel ('Truth')
pickle.dump(clf_gini,open("model.pkl","wb"))