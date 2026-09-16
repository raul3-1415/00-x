import pandas as pd
import plotly.express as px
from datetime import datetime
import streamlit as st
 
# =============================================================================
# anaconda prompt:
#     cd "C:\Users\pc\OneDrive\01. DIARIO\01. PY\00. PY-SPYDER\00-x"
#     streamlit run x0005.py
#     http://localhost:8501/
# =============================================================================

sheet_id= "1HO5_saIESfWX7eTCE03xWrKrHgc_fHkdF7Qwn9Gx5G4"
url=f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

day_ord= ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]
day_map= {0: "Lun", 1: "Mar", 2: "Mie", 3: "Jue", 4: "Vie", 5: "Sab", 6: "Dom"}
mon_map= {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}
usr_col={    
    "RAUL": "darkorange",
    "ARTURO": "silver",
    "DIEGO": "violet",
    "MIRKO": "lightgreen",}
turn_col={
    "DIA": "lightblue"
    , "NOCHE": "navy"}
ubi_col={
    'San Juan':'navy'
    ,'Miraflores':'lightblue'}

@st.cache_data(ttl=3600)

def load_data(url:str) -> pd.DataFrame:
    df=pd.read_csv(url)
    df=df.rename(columns={'DIEGO-DIA':'D-D'})
    df['D-D']=pd.to_numeric(df['D-D'],errors='coerce')
    df['DIEGO-DIA']=df['D-D']+100
    df=df.drop(columns=['D-D'])
    
    df=df.replace('-',0).fillna(0)
    df=df.melt(
        id_vars=['FECHA','nWK','DIA']
        ,var_name='name-type'
        ,value_name='value')
    df[['name','type']]=df['name-type'].str.split('-',expand=True)
    df=df.drop(columns=['name-type'])
    df=df.dropna(subset=['type'])
    df=df[df['name'].isin(['RAUL','ARTURO','DIEGO','MIRKO'])]
    df=df[['FECHA','name','type','value']]
    
    df['date']=pd.to_datetime(df['FECHA'],errors='coerce',dayfirst=True)
    df['value']=pd.to_numeric(df['value'],errors='coerce').fillna(0)
    df=df.drop(columns=['FECHA'])
    df=df.dropna(subset=['date'])

    df['year']=df['date'].dt.year.astype(int)
    df['month']=df['date'].dt.month.astype(int)
    df['mon name']=df['month'].map(mon_map)
    df['day']=df['date'].dt.weekday.astype(int)
    df['day name']=df['day'].map(day_map)
    df['ubi']=df['name'].apply(lambda x:'San Juan' if x=='RAUL'
                               else 'Miraflores')
    df['week']=df['date'].dt.isocalendar().week.astype(int)
    return df
# 
def money(x):
    return f'{x:,.0f}'
# 
def pct(x):
    return f'{x:+.1f}%'
# 
def add_delta(label,value,prev):
    if prev is None or prev ==0:
        st.metric(label,money(value))
    else:
        st.metric(label,money(value),pct((value/prev-1)*100))
# 
def filter_data(df,week_sel,name_sel,type_sel):
    out=df.copy()
    if week_sel!='Todos':
        out=out[out['week']==int(week_sel)]
    if name_sel!='Todos':
        out=out[out['name']==name_sel]
    if type_sel!='Todos':
        out=out[out['type']==type_sel]
    return out
# 
def weekly_tot(df):
    return(
        df.groupby(['year','week'],as_index=False)['value']
        .sum().sort_values(['year','week'])
        )
# 
def prev_week_val(dfb,seld_wk):
    if seld_wk=='Todos':
        return None
    weeks=sorted(dfb['week'].unique())
    seld_wk=int(seld_wk)
    prev=[w for w in weeks if w < seld_wk]
    if not prev:
        return None
    prev_week=prev[-1]
    return dfb.loc[dfb['week']==prev_week,'value'].sum()
# 
def build_kpis(dff,dfb,seld_wk):
    total=dff['value'].sum()
    act_day=dff.loc[dff['value']>0,'date'].nunique()
    avg_day=total/act_day if act_day else 0
    
    daily=dff.groupby('date')['value'].sum()
    best_day=daily.max() if not daily.empty else 0
    best_day_name=daily.idxmax().strftime('%d/%m') if not daily.empty else '-'
    
    user=dff.groupby('name')['value'].sum()
    leader=user.idxmax() if not user.empty else '-'
    leader_value=user.max() if not user.empty else 0
    
    prev=prev_week_val(dfb,seld_wk)
    
    c1,c2,c3,c4,c5=st.columns(5)
    with c1:
        st.metric('RESULTADO',money(total))
    with c2:
        st.metric('PROMEDIO/DIA',money(avg_day))
    with c3:
        st.metric('MEJOR DIA',f'{money(best_day)}',best_day_name)
    with c4:
        st.metric('USUARIO LIDER',leader,money(leader_value))
    with c5:
        if prev is None or prev==0 or seld_wk=='Todos':
            st.metric('VS SEMANA ANTERIOR','N/D')
        else:
            st.metric('VS SEMANA ANTERIOR',pct((total/prev-1)*100))
# 
def main():
    st.set_page_config(
        page_title='ƒ(x)^±n'
        ,page_icon='🧮',layout='wide'
        ,initial_sidebar_state='collapsed')
    df=load_data(url)
    
    if df.empty:
        st.error('x-x sin datos x-x')
        st.stop()
        
    aw=int(datetime.today().isocalendar().week)
    # last data date: ldd
    ldd=df['date'].max()
    
    st.title(f'Semana: N°{aw}')
    #   ___
    st.sidebar.header('FILTROS')
    
    week_values=sorted(df['week'].unique().tolist())
    week_list=['Todos']+week_values
    name_list=['Todos']+sorted(df['name'].dropna().unique().tolist())
    type_list=['Todos']+sorted(df['type'].dropna().unique().tolist())
    
    # default week index: dwi
    dwi=week_list.index(aw) if aw in week_list else 0
    
    week_sel=st.sidebar.selectbox('N° SEMANA',week_list,index=dwi)
    name_sel=st.sidebar.selectbox('NOMBRE',name_list)
    type_sel=st.sidebar.selectbox('TURNO',type_list)
    
    st.sidebar.divider()
    st.sidebar.caption(f'_________Raúl el crack_________')
    
    st.subheader(f'Semana elegida: N°{week_sel}')
    
    dff=filter_data(df,week_sel,name_sel,type_sel)
    
    if dff.empty:
        st.warning('x-x sin datos')
        st.stop()
    # ___
    dfb=filter_data(df,'Todos',name_sel,type_sel)
    build_kpis(dff,dfb,week_sel)
    st.divider()
    
    t1,t2,t3=st.tabs([
        '1️⃣ RESUMEN'
        ,'2️⃣ USUARIO'
        ,'3️⃣ ESTADISTICA'])    
    
    # size number:sn
    sn=16
    # 
    # =============================================================================
    #     TAB-1: RESUME
    # =============================================================================
    with t1:
        c1,c2=st.columns(2)
         
        # TOTAL PER DAY
        g1=(dff.groupby(['day','day name','type'],as_index=False)['value']
               .sum().sort_values('day'))
        
        fig1=px.bar(
            g1,x='day name',y='value',text_auto=',.0f',barmode='group'
            ,title='DIA',color='type',color_discrete_map=turn_col
            )
        fig1.update_layout(hovermode='x unified',font=dict(size=sn)
                           ,xaxis_title=None,yaxis_title=None)
        # TOTAL PER USER
        g2=dff.groupby(['name'],as_index=False)['value'].agg(['sum'])\
            .sort_values('sum')
        fig2=px.bar(g2,x='sum',y='name',text_auto=',.0f',barmode='stack'
                    ,orientation='h',title='USUARIO'
                    ,color='name',color_discrete_map=usr_col)
        fig2.update_layout(hovermode='y unified',font=dict(size=sn)
                           ,xaxis_title=None,yaxis_title=None)
        
        
        # TOTAL PER TURN
        g3=dff.groupby('type',as_index=False)['value'].agg(['sum'])
        fig3=px.pie(g3,names='type',values='sum',hole=.5
                    ,title='POR TURNO',color='type',color_discrete_map=turn_col)
        fig3.update_traces(textposition='outside',textinfo='value+percent')
        fig3.update_layout(font=dict(size=sn))
        
        # TOTAL PER UBI
        g4=dff.groupby('ubi',as_index=False)['value'].agg(['sum'])
        
        fig4=px.pie(g4,names='ubi',values='sum',hole=.5
                    ,title='POR UBICACION',color='ubi',color_discrete_map=ubi_col)
        fig4.update_traces(textposition='outside',textinfo='value+percent')
        fig4.update_layout(font=dict(size=sn))
        
        # PARTICIPATION PER USER   
        g5=dff.groupby(['name'],as_index=False)['value'].sum()\
            .sort_values('value',ascending=False)
        g5['part']=g5['value']/g5['value'].sum()*100
            
        dg5=g5.copy()
        
        dg5['value']=dg5['value'].map(money)
        dg5['part']=dg5['part'].map(lambda x:f'{x:.0f}%')
                
        # 
        with c1:
            st.plotly_chart(fig1,use_container_width=True)
        with c2:
            st.plotly_chart(fig2,use_container_width=True)
        
        st.divider()
        c3,c4=st.columns(2)
        with c3:
            st.plotly_chart(fig3,use_container_width=True)
        with c4:
            st.plotly_chart(fig4,use_container_width=True)
       
        st.divider()
        st.subheader('USUARIO-PARTICIPACION')
        st.dataframe(dg5,use_container_width=True,hide_index=True)
        
# =============================================================================
#     TAB-2: USER
# =============================================================================
    
    with t2:
        # TYPE:DIA
        g6=dff[dff['type']=='DIA'].groupby(['type','name','day name']
                                           ,as_index=False)['value'].agg(['sum'])
        
        fig6=px.line(g6,x='day name',y='sum',markers=True,text='sum'
                     ,title='DIA'
                     ,color='name',color_discrete_map=usr_col)
        fig6.update_traces(textposition='top center',texttemplate='%{text:,.0f}'
                          ,textfont=dict(size=sn))
        fig6.update_layout(hovermode='x unified',xaxis_title=None,yaxis_title=None)
        
        # TYPE:NOCHE
        g7=dff[dff['type']=='NOCHE'].groupby(['type','name','day name']
                                             ,as_index=False)['value'].agg(['sum'])
        
        fig7=px.line(g7,x='day name',y='sum',markers=True,text='sum'
                     ,title='NOCHE'
                     ,color='name',color_discrete_map=usr_col)
        fig7.update_traces(textposition='top center',texttemplate='%{text:,.0f}'
                     ,textfont=dict(size=sn))
        fig7.update_layout(hovermode='x unified',xaxis_title=None,yaxis_title=None)
        
        # PIVOT TABLE
        tmt=pd.pivot_table(data=dff,values='value',index=['type','name']
                           ,columns='day name',aggfunc='sum')
        od=['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom']
        cols_in = [dia for dia in od if dia in tmt.columns]
        tmt= tmt[cols_in]
        
        # 
        c5,c6=st.columns(2)
        with c5:
            st.plotly_chart(fig6,use_container_width=True)
        with c6:
            st.plotly_chart(fig7,use_container_width=True)
        
        st.divider()
        
        st.dataframe(tmt.style.format('{:,.0f}')
                     ,use_container_width=True)


# =============================================================================
#     TAB-3: STATS
# =============================================================================
   
         
# 
# 
if __name__=='__main__':
    main()















































































































