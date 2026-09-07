import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
#pio.renderers.default = 'browser' # 'png'-to stay in spyder

from plotly.subplots import make_subplots

pd.options.display.float_format='{:20.2f}'.format
pd.set_option('display.max_columns',None)
pd.set_option('display.expand_frame_repr', False)
plt.style.use('dark_background')
#____________________________________________________



df_bat=pd.read_csv('x11-batting.csv')
df_bat.info()

df_bat['yearID'].sort_values().unique()

tot_years=max(df_bat['yearID'])-min(df_bat['yearID'])
tot_yearsactive_players=df_bat.loc[df_bat['AB']>0]

active_players=df_bat.loc[df_bat['AB']>0]
active_players['playerID'].nunique()

top_hr=df_bat.groupby('playerID')['HR'].sum().sort_values(ascending=False).head(3).reset_index()
top_hr=df_bat.groupby('playerID')['HR'].sum().sort_values(ascending=False).head(3).reset_index()

plt.figure(figsize=(6,3))
ax = sns.barplot(data=top_hr,x='playerID',y='HR',palette='Blues_r',hue='playerID')\
    .set(title='TOP',xlabel='id',ylabel='conteo')
sns.despine()
plt.tight_layout()
plt.show()

fig = px.bar(top_hr,x='playerID',y='HR',color='HR',color_continuous_scale='blues',text='HR',title='TOP')
fig.update_layout(xaxis_title='idr',yaxis_title='conteo',template='plotly_dark',width=600,height=300)
fig.show()

fig=px.bar(top_hr,x='HR',y='playerID'\
           ,color='HR',color_continuous_scale='blues',text='HR',title='TOP',orientation='h')
fig.update_layout(xaxis_title='id',yaxis_title='count',template='plotly_dark',width=600,height=300)
fig.show()

thy=df_bat.groupby('yearID')['HR'].sum().sort_index(ascending=False).reset_index()

fig=px.line(thy,x='yearID',y='HR',title='xxx',markers=False)
fig.update_layout(xaxis_title='x',yaxis_title='y',template='plotly_dark'\
                  ,hovermode='x unified',width=800,height=400)
fig.update_traces(line=dict(width=1,color='yellow'))
fig.show() 

best_team=df_bat.groupby('teamID')['HR'].sum().reset_index().sort_values(by='HR',ascending=False)

team_hr_py=df_bat.groupby(['yearID','teamID'])['HR'].sum().reset_index()

rockies_1=team_hr_py.loc[team_hr_py['teamID']=='COL',['yearID','HR']].reset_index(drop=True).sort_values(by='yearID',ascending=True)

yankees=team_hr_py.loc[team_hr_py['teamID']=='NYA',['yearID','HR']].reset_index(drop=True).sort_values(by='yearID')
yankees=yankees.loc[yankees['yearID']>1993]

league_avghr=team_hr_py.groupby('yearID')['HR'].mean().reset_index().sort_values(by='yearID',ascending=True)
league_avghr.head()
league_avghr=league_avghr.loc[league_avghr['yearID']>1993]

df_plot = pd.DataFrame({
    'L': league_avghr.set_index('yearID')['HR'],
    'R': rockies_1.set_index('yearID')['HR'],
    'Y':yankees.set_index('yearID')['HR']
})
fig = px.line(df_plot,title='xxx')
fig.update_layout(xaxis_title='x',yaxis_title='y',template='plotly_dark')
fig.update_traces(line=dict(width=5,color='steelblue'),line_dash='dot', selector=dict(name='L'))
fig.update_traces(line=dict(width=1,color='yellow'),selector=dict(name='R'))
fig.update_traces(line=dict(width=1,color='white'),selector=dict(name='Y'))
fig.show()

df_bat.isna().sum()[df_bat.isna().sum()>0].sort_values(ascending=False)

df_bat[['BB','HBP','SF','IBB']]=df_bat[['BB','HBP','SF','IBB']].fillna(0)

df_bat['OBP']=((df_bat['H']+df_bat['BB']+df_bat['HBP'])/(df_bat['AB']+df_bat['BB']+df_bat['HBP']+df_bat['SF']))
df_bat['OBP']=df_bat['OBP'].fillna(0)

df_salaries=pd.read_csv('x11-salaries.csv')

battingwsal=df_bat.merge(df_salaries,on=['playerID','yearID','teamID'],how='left')
battingwsal['salary']=battingwsal['salary'].fillna(0)

df_value=battingwsal.dropna(subset=['salary','OBP','AB'])
df_value=battingwsal[(battingwsal['salary']>0)&(battingwsal['OBP']>0)&(battingwsal['AB']>=200)].copy()
df_value.head()

df_value['OBPperDOL']=df_value['OBP']/df_value['salary']
df_value=df_value.loc[:,['playerID','yearID','teamID','OBP','salary','OBPperDOL']]

