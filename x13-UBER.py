import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
import seaborn as sns
import matplotlib.pyplot as plt
plt.style.use('dark_background')
from datetime import datetime
from sklearn.preprocessing import OneHotEncoder
pio.renderers.default='png'
pd.options.display.float_format='{:20.2f}'.format

#   READING_________________
df=pd.read_csv(r'C:\Users\pc\OneDrive\01. DIARIO\01. PY\00. PY-SPYDER\00-x\x13-uber.csv')
df.info()
dfe=df.isna().sum()[df.isna().sum()>0].sort_values(ascending=False)

#  CLEANING ____________
df['PURPOSE'].fillna('NOT',inplace=True)

df['START_DATE']=pd.to_datetime(df['START_DATE'],errors='coerce')
df['END_DATE']=pd.to_datetime(df['END_DATE'],errors='coerce')

dfe=df.isna().sum()[df.isna().sum()>0].sort_values(ascending=False)
#       create cols of date and time
df['date']=pd.DatetimeIndex(df['START_DATE']).date
df['time']=pd.DatetimeIndex(df['START_DATE']).hour
#       create col of time at day
df['day-night']=pd.cut(x=df['time'],bins=[0,10,15,19,24]
                       ,labels=['morning','afternoon','evening','night'])
#   last total cleaning
df.dropna(inplace=True)
df.drop_duplicates(inplace=True)
df.reset_index(inplace=True)

#   EDA_____________
#       identify: 1.cols with text|2.count unique values in each one
obj=(df.dtypes=='object')
object_cols=list(obj[obj].index)
unique_val={}
for col in object_cols:
    unique_val[col]=df[col].unique().size
unique_val
#   unique values
#   graph-histogram
# =============================================================================
# fig=make_subplots(rows=1,cols=2,subplot_titles=('category-1','purpose'))
# fig_1=px.pie(df,names='PURPOSE')
# fig_2=px.histogram(df,x='PURPOSE')
# fig.add_trace(fig_1.data[0],row=1,col=1)
# fig.add_trace(fig_2.data[0],row=1,col=2)
# fig.update_layout(template='plotly_dark')
# fig.update_xaxes(tickangle=90)
# fig.show()
# =============================================================================

fig=px.histogram(df,x='day-night',text_auto=True,title='day-night')
fig.update_layout(template='plotly_dark')
fig.show()

fig=px.pie(df,names='day-night',title='day-night',hole=.5)
fig.update_traces(textposition='outside',textinfo='value+percent+label')
fig.update_layout(template='plotly_dark')
fig.show()

fig=px.pie(df,names='PURPOSE',hole=.5,title='purpose')
fig.update_traces(textposition='outside',textinfo='value+percent')
fig.update_layout(template='plotly_dark')
fig.show()

fig=px.pie(df,names='CATEGORY',hole=.5,title='category')
fig.update_traces(textposition='outside',textinfo='value+percent')
fig.update_layout(template='plotly_dark')
fig.show()

df['PURPOSE'].value_counts()
#       graph-pie-without:NOT in purpose
fig=px.pie(df[df['PURPOSE']!='NOT'],names='PURPOSE',hole=.5,title='purpose w/o NOT')
fig.update_traces(textposition='outside',textinfo='value+percent')
fig.update_layout(template='plotly_dark')
fig.show()

fig=px.histogram(df,x='PURPOSE',text_auto=True,color='CATEGORY'
                 ,barmode='group')  #barmode:stack (serie)
fig.update_layout(template='plotly_dark')
fig.show()

#   bridge- from EDA to ML (machine learning)
#   techinque:ONEHOTENCODER to go from 'text' to binari (0,1)
object_cols=['CATEGORY','PURPOSE']
OH_encoder=OneHotEncoder(sparse_output=False,handle_unknown='ignore')
OH_cols=pd.DataFrame(OH_encoder.fit_transform(df[object_cols]))

OH_cols.index=df.index
OH_cols.columns=OH_encoder.get_feature_names_out()

df_f=df.drop(object_cols,axis=1)
df=pd.concat([df_f,OH_cols],axis=1)

df_num=df.select_dtypes(include=['number'])

#   graph-heatmap -px
fig=px.imshow(df_num.corr(),text_auto='.2f'
              ,color_continuous_scale='BrBG')
fig.update_traces(xgap=2,ygap=2)
fig.update_layout(template='plotly_dark')
fig.show()

# 
df['MONTH']=pd.DatetimeIndex(df['START_DATE']).month
month_label={1.0:'Jan',2.0:'Feb',3.0: 'Mar', 4.0: 'April',
               5.0: 'May', 6.0: 'June', 7.0: 'July', 8.0: 'Aug',
               9.0: 'Sep', 10.0: 'Oct', 11.0: 'Nov', 12.0: 'Dec'}
df['MONTH']=df.MONTH.map(month_label)
mon=df.MONTH.value_counts(sort=False)
df_m=pd.DataFrame({'count':mon.values
                 ,'max':df.groupby('MONTH',sort=False)['MILES'].max()})
#   line-g|total count vs max
fig=px.line(df_m,title='total count vs max'
              ,markers=True,color_discrete_sequence=['steelblue','lightgreen'])
fig.update_layout(template='plotly_dark',hovermode='x unified')
fig.show()

#   weekdays
df['day']=df.START_DATE.dt.weekday
day_label={0: 'Mon', 1: 'Tues', 2: 'Wed', 3: 'Thus'
           , 4: 'Fri', 5: 'Sat', 6: 'Sun'}
df['day']=df['day'].map(day_label)
day_label=df.day.value_counts(sort=False)

#   pie graph
fig=px.histogram(df,x='day',text_auto=True
                 ,category_orders={'day': ['Mon', 'Tues', 'Wed'
                                           , 'Thus', 'Fri', 'Sat', 'Sun']})
fig.update_layout(template='plotly_dark')
fig.show()











































































