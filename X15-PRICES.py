import pandas as pd
pd.options.display.float_format='{20.2f}'.format
import plotly.express as px
import plotly.io as pio
pio.renderers.default='png'
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('dark_background')
import numpy as np

import pickle
import math

# OrdinalEncoder better then LabelEncoder, allows to work grouping cols
from sklearn.preprocessing import OrdinalEncoder
from sklearn.model_selection import GridSearchCV

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error,mean_absolute_error,r2_score

from sklearn.model_selection import train_test_split

# |________________________________________

with open(r"C:\Users\pc\OneDrive\01. DIARIO\01. PY\00. PY-SPYDER\00-x\x15-PRICES.pkl",'rb') as f:
    df=pickle.load(f)
    
df.info()
df.isna().sum()[df.isna().sum()>0].sort_values(ascending=False)

# looking if exist uppercase in values of the cols
df['zone'].value_counts()
df['neighbourhood'].value_counts()
df['finished'].value_counts()

# reducing to lowercase
cols=['zone','neighbourhood','finished']
df[cols]=df[cols].apply(lambda x:x.str.lower())

# checking
df['neighbourhood'].value_counts()

# OrdinalEncoder: change string values to numerical 
oe=OrdinalEncoder()
df[cols]=oe.fit_transform(df[cols])

# transform type to 'category', to reduce the memory
df[cols]=df[cols].astype('category')

# correlation
sns.heatmap(df.corr(numeric_only=True).dropna(),annot=True,cmap='Blues')
sns.pairplot(df,plot_kws={'alpha':.5})      # ,hue='name of column to segmentation'

# outliers
fig=px.box(df,y=['size','price_euro'],title='searching outliers')
fig.update_layout(template='plotly_dark')

# eliminating ourliers, in function of col:'price euro'
q1=np.percentile(df['price_euro'],25)
q3=np.percentile(df['price_euro'],75)
iqr=q3-q1
ul=q3+1.5*iqr   #ul:upper limit
df=df[df['price_euro']<=ul]

# trin-test: randomForest
y=df.price_euro         #objective vector to learn to predict
# x=df.iloc[:,1:11]       #predicted variables
df.columns
x=df.iloc[:,[1,2,3,8,9]]

# percentage to test
x_train,x_test,y_train,y_test=train_test_split(x,y,random_state=13,test_size=.1)

# model
# __|these technique optimize the search
# __|sqrt: evaluate the model by its square root of the  predicted variables
bm=RandomForestRegressor(max_features='sqrt',random_state=42
                         ,oob_score=True,n_jobs=1) #bm:base model
parameters={'n_estimators':[100,200,500,750]}
search=GridSearchCV(bm,parameters,cv=5,n_jobs=-1)
search.fit(x_train,y_train)

print('optimal number:',search.best_params_['n_estimators'])
print(f'OOB score:{search.best_estimator_.oob_score_}')

# __|defining the best model
rf=search.best_estimator_
# __|defining the relevant variables for the predict variable
df_i=pd.DataFrame({'variable':rf.feature_names_in_
                       ,'importance':rf.feature_importances_})
df_i=df_i.sort_values(by='importance',ascending=False)

fig=px.bar(df_i,x='importance',y='variable',orientation='h',text_auto=True)
fig.update_layout(template='plotly_dark',hovermode='y unified')
# fig.update_yaxes(autorange='reversed')
fig.show()

# __|performance evaluation - predicted variable:price 

pred_var=rf.predict(x_test)
y_test      #real values

mae=mean_absolute_error(y_true=y_test,y_pred=pred_var)
mse=mean_squared_error(y_true=y_test,y_pred=pred_var)
rmse= np.sqrt(mse)
r2=r2_score(y_true=y_test,y_pred=pred_var)
print(f'R2 score:{r2:.2f}')
print(f'mae: {mae:.2f}')
print(f'rmse:{rmse:.2f}')

# __|graphic the performance of data
# scatter
fig=px.scatter(x=y_test,y=pred_var,opacity=.5,
               title='prediction(x) vs reality(y)')
fig.add_shape(type='line',x0=y_test.min(),y0=y_test.min(),
              x1=y_test.max(),y1=y_test.max(),line=dict(color='red',dash='dash'))
fig.update_layout(template='plotly_dark',hovermode='x unified')
fig.show()
# distribution

waste=y_test-pred_var
fig=px.histogram(x=waste,nbins=10,marginal='violin')
fig.update_layout(template='plotly_dark')
fig.show()

























































