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
# df=df.drop(columns=['TOT'])

df=df.rename(columns={
    'DIEGO-DIA':'D-D'})

df['D-D']=pd.to_numeric(df['D-D'],errors='coerce')
df['DIEGO-DIA']=df['D-D']+100
df=df.drop(columns=['D-D'])

df=df.replace('-',0).fillna(0)
df=df.melt(id_vars=['FECHA','nWK','DIA'],
             var_name='name-type',
             value_name='value')
df[['name','type']]=df['name-type'].str.split('-',expand=True)
df=df.drop(columns=['name-type'])
df=df[['FECHA', 'name', 'type', 'value']]

df['date']=pd.to_datetime(df['FECHA'],errors='coerce',dayfirst=True)
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
df['day name']=df['day'].map(day_l)

df['ubi']=df['name'].apply(lambda x: 'San juan'if x=='RAUL'
                           else 'Miraflores')

df['week']=df['date'].dt.isocalendar().week



# ________________________________________________
#   EDA:1

# =============================================================================
# g1=df1.groupby(['month','ubi','name','type']).agg({'type':'count','value':['mean','max','min']})
# =============================================================================
df1=df.loc[(df['year']==2026) & (df['month']>1)]

g2=df1.groupby(['week','ubi','type','day','day name'])['value'].agg(['mean','sum']).reset_index()

g3=df1.groupby(['type','name','day name'])['value'].agg(['mean','sum']).reset_index()


#   fig#.type.#______________________________
#   ___
fig1=px.bar(g2,x='day name',y='sum',title='DIAS',text_auto=',.0f'
            ,color='type',color_discrete_map={'DIA':'lightblue','NOCHE':'navy'}
            ,orientation='v')
fig1.update_layout(xaxis_title='dia',yaxis_title='INGRESO'
                  ,template='plotly_dark',hovermode='x unified')
# fig1.show()

#   ___
fig2=px.pie(g2,names='type',values='sum',hole=.5)
fig2.update_traces(textposition='outside',textinfo='value+percent')
fig2.update_layout(template='plotly_dark')
# fig2.show()

#   ___
fig3=px.pie(g2,names='ubi',values='sum',hole=.5)
fig3.update_traces(textposition='outside',textinfo='value+percent')
fig3.update_layout(template='plotly_dark')
# fig3.show()

#   ___
fig4=px.bar(g3,x='sum',y='name',text_auto=',.0f',orientation='h'
            ,color='type',color_discrete_map={'DIA':'lightblue','NOCHE':'navy'})
fig4.update_layout(template='plotly_dark')
# fig4.show()
#   ___
g4=df1[df1['type']=='DIA'].groupby(['type','name','day','day name'])\
    ['value'].agg(['sum']).reset_index()
# 
fig5=px.line(g4,x='day name',y='sum',markers=True,color='name'
             ,color_discrete_map={'RAUL':'lightgreen','ARTURO':'red'
                                  ,'DIEGO':'yellow','MIRKO':'white'})
fig5.update_layout(template='plotly_dark')
# fig5.show()
# 
g5=df1[df1['type']=='NOCHE'].groupby(['type','name','day','day name'])\
    ['value'].agg(['sum']).reset_index()

fig6=px.line(g5,x='day name',y='sum',markers=True,color='name'
             ,color_discrete_map={'RAUL':'lightgreen','ARTURO':'red'
                                  ,'DIEGO':'yellow','MIRKO':'lightblue'})
fig6.update_layout(template='plotly_dark')
# fig6.show()



#___________________________________________________________________ 
#___________________________________________________________________  
#__________________________|STREAMLIT|_______________________________
# 
# =============================================================================
# google sheets:_________
# https://docs.google.com/spreadsheets/d/1HO5_saIESfWX7eTCE03xWrKrHgc_fHkdF7Qwn9Gx5G4/edit?usp=sharing
# ANACONDA PROMPT:_________
# cd "C:\Users\pc\OneDrive\01. DIARIO\01. PY\00. PY-SPYDER\00-x"
# streamlit run x0003.py
# MICROSOFT EDGE-LOCAL:
#    http://localhost:8501/
# =============================================================================
# 
#__________________________|STREAMLIT|_______________________________

st.set_page_config(page_title='ƒ(±x)',layout='wide'
                   ,initial_sidebar_state='collapsed')
def main():

    # actual week:aw
    aw=datetime.today().isocalendar()[1]
    
    
    st.sidebar.header('Filtros')
    
    week_list= ['Todos']+list(df1['week'].unique())
    name_list = ['Todos']+list(df1['name'].unique())
    type_list=['Todos']+list(df1['type'].unique())
    
    try:
        iw=week_list.index(aw) #index week:iw
    except ValueError:
        iw=0
    
    week_sel=st.sidebar.selectbox('N° Semana', week_list,index=iw)
    name_sel= st.sidebar.selectbox('Nombre', name_list)
    type_sel=st.sidebar.selectbox('Turno',type_list)
    
    st.title(f'Semana actual: {aw}')
    st.subheader(f'Semana elegida: {week_sel}')
    
    
    
    df_fil=df1.copy()
    if week_sel != 'Todos':
        df_fil = df_fil[df_fil['week'] == week_sel]
    if name_sel != 'Todos':
        df_fil = df_fil[df_fil['name'] == name_sel]
    if type_sel!='Todos':
        df_fil=df_fil[df_fil['type']==type_sel]

    # ___|font size
    sn=16
    # ___|graphs
    #
    g1=df_fil.groupby(['day','day name','type'])['value']\
        .agg(['sum','mean']).reset_index()
        
    fig1=px.bar(g1,x='day name',y='sum',text_auto=',.0f'
                ,title='DIAS'
                ,color='type',color_discrete_map={'DIA':'lightblue','NOCHE':'navy'}
                ,orientation='v')
    fig1.update_layout(hovermode='x unified',font=dict(size=sn)
                       ,xaxis_title=None,yaxis_title=None)
    #   ___
    g2=df_fil.groupby(['type'])['value'].agg(['sum']).reset_index()
    
    fig2=px.pie(g2,names='type',values='sum',hole=.5,title='TURNO')
    fig2.update_traces(textposition='outside',textinfo='value+percent')
    fig2.update_layout(font=dict(size=sn)
                       ,height=200,margin=dict(t=30, b=30, l=10, r=10))
    #   ___
    g3=df_fil.groupby(['ubi'])['value'].agg(['sum']).reset_index()
    
    fig3=px.pie(g3,names='ubi',values='sum',hole=.5,title='UBICACION')
    fig3.update_traces(textposition='outside',textinfo='value+percent')
    fig3.update_layout(font=dict(size=sn)
                       ,height=200,margin=dict(t=30, b=30, l=10, r=10))
    #   ___
    g4=df_fil.groupby(['name','type'])['value'].agg(['sum']).reset_index()
    
    fig4=px.bar(g4,x='sum',y='name',text_auto=',.0f',orientation='h'
                ,title='USUARIOS'
                ,color='type',color_discrete_map={'DIA':'lightblue','NOCHE':'navy'})
    fig4.update_layout(hovermode='x unified',font=dict(size=sn)
                       ,xaxis_title=None,yaxis_title=None)
    #   ___
    g5=df_fil[df_fil['type']=='DIA'].groupby(['type','name','day','day name'])\
        ['value'].agg(['sum']).reset_index()
    
    fig5=px.line(g5,x='day name',y='sum',markers=True,text='sum'
                 ,title='TURNO: DIA',color='name'
                 ,color_discrete_map={'RAUL':'lightgreen','ARTURO':'red'
                                      ,'DIEGO':'yellow','MIRKO':'white'})
    fig5.update_traces(textposition='top center',texttemplate='%{text:,.0f}'
                       ,textfont=dict(size=11))
    fig5.update_layout(hovermode='x unified',xaxis_title=None,yaxis_title=None)
    
    # 
    g6=df_fil[df_fil['type']=='NOCHE'].groupby(['type','name','day','day name'])\
        ['value'].agg(['sum']).reset_index()
        
    fig6=px.line(g6,x='day name',y='sum',markers=True,text='sum'
                 ,title='TURNO: NOCHE',color='name'
                 ,color_discrete_map={'RAUL':'lightgreen','ARTURO':'red'
                                      ,'DIEGO':'yellow','MIRKO':'lightblue'})
    fig6.update_traces(textposition='top center',texttemplate='%{text:,.0f}'
                       ,textfont=dict(size=11))
    fig6.update_layout(hovermode='x unified',xaxis_title=None,yaxis_title=None)
    
     
    
    #   ___|pivot table
    #       table matrix:tmt
    tmt=pd.pivot_table(data=df_fil,values='value',index=['type','name']
                       ,columns='day name',aggfunc='sum')
        # order of days=od 
    od=['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom']
    cols_in = [dia for dia in od if dia in tmt.columns]
    tmt= tmt[cols_in]
    
    # ___|distribution page
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(fig5, use_container_width=True)
    with c2:
        st.plotly_chart(fig6, use_container_width=True)
    # 
    st.divider()
    st.dataframe(tmt.style.format('{:,.0f}')
                 ,use_container_width=True)
    # 
    st.divider()
    c3,c4=st.columns(2)
    with c3:
        st.plotly_chart(fig4, use_container_width=True)
    with c4:
        st.plotly_chart(fig1)
    # 
    st.divider()
    c5,c6=st.columns(2)
    with c5:
        st.plotly_chart(fig2)
    with c6:
        st.plotly_chart(fig3)
    
if __name__=='__main__':
    main()















































































































