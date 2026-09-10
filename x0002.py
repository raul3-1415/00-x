import pandas as pd
pd.options.display.float_format='{:20.2f}'.format
import plotly.express as px
import plotly.io as pio
pio.renderers.default='png'
from datetime import datetime
import streamlit as st

# READING_______________________
sheet_id = "1HO5_saIESfWX7eTCE03xWrKrHgc_fHkdF7Qwn9Gx5G4"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data(ttl=3600) 
def exp_data(path):
    df = pd.read_csv(path)
    return df
df= exp_data(url)








# PREPARED______________________
df=df.replace('-',0).fillna(0)
df=df.melt(id_vars=['FECHA','nWK','DIA'],
             var_name='name-type',
             value_name='value')
df[['name','type']]=df['name-type'].str.split('-',expand=True)
df=df.drop(columns=['name-type'])
df=df[['FECHA', 'name', 'type', 'value']]

df['date']=pd.to_datetime(df['FECHA'],errors='coerce')
df['value']=pd.to_numeric(df['value'],errors='coerce')

df=df.drop('FECHA',axis=1)

df['year']=df.date.dt.year
df['month']=df.date.dt.month
mon_l={1:'Ene',2:'Feb',3:'Mar',4:'Abr',
               5:'May',6:'Jun',7:'Jul',8:'Ago',
               9:'Sep',10:'Oct',11:'Nov',12:'Dic'}
df['mon name']=df['month'].map(mon_l)
df['day']=df.date.dt.weekday
day_l={0:'Lun',1:'Mar',2:'Mie',3:'Jue',4:'Vie',5:'Sab',6:'Dom'}
df['day']=df['day'].map(day_l)

df['ubi']=df['name'].apply(lambda x: 'San juan'if x=='RAUL'
                           else 'Miraflores')

#   EDA:1
df_1=df.loc[(df['year']==2026) & (df['month']>1)]
df_1['year'].value_counts()

#   grouped data
g1=df_1.groupby(['month','ubi','name','type']).agg({'type':'count','value':['mean','max','min']})

g2=df_1.groupby(['month','mon name'])['value'].agg(['mean','sum']).reset_index()

df_1.info()

#   df_1
fig=px.line(g2[g2['mon name']!='Ene'],x='mon name',y='sum',title='Totales por mes',markers=True)
fig.update_traces(line=dict(color='lightgreen'))
fig.update_layout(xaxis_title='MES',yaxis_title='INGRESO'
                  ,template='plotly_dark',hovermode='x unified')
fig.show()

#   PAGE________________

# =============================================================================
# ANACONDA PROMPT:_________
# google link:https://docs.google.com/spreadsheets/d/1HO5_saIESfWX7eTCE03xWrKrHgc_fHkdF7Qwn9Gx5G4/edit?usp=sharing
# 
# cd "C:\Users\pc\OneDrive\01. DIARIO\01. PY\00. PY-SPYDER\00-x"
# streamlit run x00-x01.py
# =============================================================================

# =============================================================================
# st.set_page_config(page_title='X',layout='wide'
#                    ,initial_sidebar_state='collapsed')
# =============================================================================
def main():
    st.title('xad')
    # st.sidebar.header('Otros')
    
if __name__=='__main__':
    main()

































































































