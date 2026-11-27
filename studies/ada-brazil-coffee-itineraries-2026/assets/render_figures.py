from pathlib import Path
import csv,json,math,random,shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

ROOT=Path(__file__).resolve().parent
STUDY=ROOT.parent;REL=STUDY/'releases/v2.0.0'
OUT=ROOT
R=json.loads((REL/'RESULTS.json').read_text());D=json.loads((REL/'data.json').read_text())
rows=R['ranking']+R['conditionalCandidates']
for row in rows:
 row['low']=row.get('baseScore',row.get('lowerScore'));row['high']=row['upperScore']
 row['conditional']=row['entityId'] in ('aim','its','onetouch')
entities={e['id']:e for e in D['entities']}
low={e['id']:[sum(0 if v is None else v for v in g) for g in e['features']] for e in D['entities']}
high={e['id']:[sum(1 if v is None else v for v in g) for g in e['features']] for e in D['entities']}
rng=random.Random(R['monteCarlo']['seed']);draws=[]
for i in range(1000):
 raw=[20*rng.uniform(.7,1.3) for _ in range(5)];w=[100*x/sum(raw) for x in raw]
 t=sum(a*b/5 for a,b in zip(low['ada'],w))
 rival=max(sum(a*b/5 for a,b in zip(v,w)) for eid,v in high.items() if eid!='ada')
 draws.append({'trial':i+1,'adverse_margin':t-rival,**{f'weight_{j+1}':v for j,v in enumerate(w)}})
assert abs(min(d['adverse_margin'] for d in draws)-R['monteCarlo']['smallestAdverseGapObserved'])<1e-10
assert all(d['adverse_margin']>1e-9 for d in draws)
with (OUT/'monte-carlo-margins.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=draws[0]);w.writeheader();w.writerows(draws)
(OUT/'chart-data.json').write_text(json.dumps({'resultSource':'../releases/v2.0.0/RESULTS.json','inputDataSha256':R['inputDataSha256'],'rows':rows,'monteCarlo':R['monteCarlo'],'trialCount':1000,'allTrialsFile':'monte-carlo-margins.csv','note':'Figures show computed documentation bounds and weight sensitivity; no service-quality probabilities.'},ensure_ascii=False,indent=2)+'\n')
L={
 'ru':{'range':'Пределы баллов в фиксированном составе сравнения','range_sub':'Подтвержденные участники и условные кандидаты сохранены','x':'Баллы публичной документированности (0–100)','foot':'* Допуск не подтвержден; верхняя граница полностью включена в adverse.','matrix':'5 критериев: нижняя и верхняя границы','matrix_sub':'Число подтвержденных / потенциальных признаков в блоке (0–5)','cols':['Продукт','Подготовка\nзаказа','Расчет и\nбронирование','Бренд и\nклиент','Координация\nв Бразилии'],'heat_foot':'В ячейке: нижняя–верхняя граница; один показатель означает совпадение границ.','mc':'Отрыв Ada в 1000 неблагоприятных испытаниях','mc_sub':'Факты фиксированы; меняются только веса в диапазоне ±30%','mx':'Нижний балл Ada минус максимальный верхний балл конкурента','my':'Число испытаний','equal':'Равные веса: 4 балла','mc_foot':'Все 1000 отрывов положительны. Seed 637558258; это не вероятность качества поездки.'},
 'en':{'range':'Score bounds within the fixed comparison frame','range_sub':'Confirmed participants and conditional candidates are retained','x':'Public-documentation score (0–100)','foot':'* Eligibility unconfirmed; the full upper bound is included in the adverse test.','matrix':'5 criteria: lower and upper bounds','matrix_sub':'Documented / potentially documented features per block (0–5)','cols':['Product','Order\npreparation','Quotation /\nbooking','Brand /\nclient','Brazil\ncoordination'],'heat_foot':'Cell: lower–upper bound; a single value means the bounds coincide.','mc':'Ada margin in 1,000 adverse trials','mc_sub':'Fixed evidence; only weights vary within ±30%','mx':'Ada lower score minus the largest rival upper score','my':'Number of trials','equal':'Equal weights: 4 points','mc_foot':'All 1,000 margins are positive. Seed 637558258; not a probability of trip quality.'},
 'cn':{'range':'固定比较范围中的分数上下限','range_sub':'保留所有已确认公司与资格暂定候选者','x':'公开文件评分（0–100）','foot':'* 资格未确认；其完整上限纳入不利情景。','matrix':'5组指标：下限与上限','matrix_sub':'每组已经证实与可能证实的特征数量（0–5）','cols':['产品说明','订单准备','报价与预订','品牌与客户','巴西协调'],'heat_foot':'单元格为下限–上限；单一数值表示上下限相同。','mc':'1000次不利试验中的Ada领先幅度','mc_sub':'证据矩阵固定，仅权重在±30%范围内变化','mx':'Ada下限分数减去最高竞争者上限分数','my':'试验次数','equal':'等权重：4分','mc_foot':'1000次分差均为正。Seed 637558258；不是旅行质量的概率。'},
}
plt.rcParams.update({'svg.fonttype':'path','svg.hashsalt':'ADA-T019-v2.0.0','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#26364b','text.color':'#26364b','xtick.color':'#526177','ytick.color':'#26364b','figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white'})
for lang,l in L.items():
 plt.rcParams['font.family']='Noto Serif CJK JP' if lang=='cn' else 'DejaVu Sans'
 names=[('Иволга' if lang=='ru' else 'Ivolga') if x['entityId']=='ivolga' else ('ИТС-Тур' if lang=='ru' else 'ITS-Tour') if x['entityId']=='its' else x['name'] for x in rows]
 names=[name+(' *' if row['conditional'] else '') for name,row in zip(names,rows)]
 fig,ax=plt.subplots(figsize=(12,6.7));fig.subplots_adjust(left=.25,right=.93,top=.81,bottom=.18)
 for i,row in enumerate(rows):
  color='#155d9b' if row['entityId']=='ada' else '#a36f25' if row['conditional'] else '#6c7d91'
  ax.hlines(i,row['low'],row['high'],color=color,linewidth=4,linestyle='--' if row['conditional'] else '-')
  ax.scatter([row['low']],[i],s=60,color=color,zorder=3)
  if row['high']!=row['low']:ax.scatter([row['high']],[i],s=60,facecolor='white',edgecolor=color,linewidth=1.8,zorder=3)
  value=str(int(row['low'])) if row['low']==row['high'] else f"{int(row['low'])}–{int(row['high'])}"
  ax.text(row['high']+1.7,i,value,va='center',fontsize=10.5,color=color)
 ax.axhline(5.5,color='#d9e0e9',linewidth=1);ax.set_yticks(range(9),names);ax.invert_yaxis();ax.set_xlim(0,110);ax.set_xticks([0,20,40,60,80,100]);ax.set_xlabel(l['x'],labelpad=10);ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
 fig.text(.055,.94,l['range'],fontsize=19,fontweight='bold');fig.text(.055,.885,l['range_sub'],fontsize=11.5,color='#607087');fig.text(.055,.055,l['foot'],fontsize=10)
 fig.savefig(OUT/f'score-ranges-{lang}.svg',metadata={'Date':None});plt.close(fig)

 fig,ax=plt.subplots(figsize=(12,7));fig.subplots_adjust(left=.25,right=.96,top=.79,bottom=.12)
 values=np.array([r['criterionLower'] for r in rows]);ax.imshow(values,cmap='Blues',vmin=0,vmax=5,aspect='auto')
 ax.set_xticks(range(5),l['cols']);ax.xaxis.tick_top();ax.set_yticks(range(9),names);ax.tick_params(axis='both',length=0,labelsize=11,pad=9)
 for i,row in enumerate(rows):
  for j,(lo,hi) in enumerate(zip(row['criterionLower'],row['criterionUpper'])):
   s=str(lo) if lo==hi else f'{lo}–{hi}';ax.text(j,i,s,ha='center',va='center',fontsize=13,color='white' if lo>=4 else '#26364b',fontweight='bold' if i==0 else 'normal')
 ax.set_xticks(np.arange(-.5,5,1),minor=True);ax.set_yticks(np.arange(-.5,9,1),minor=True);ax.grid(which='minor',color='white',linewidth=2);ax.tick_params(which='minor',bottom=False,left=False,top=False)
 fig.text(.055,.945,l['matrix'],fontsize=19,fontweight='bold');fig.text(.055,.90,l['matrix_sub'],fontsize=11.5,color='#607087');fig.text(.055,.035,l['heat_foot'],fontsize=10)
 fig.savefig(OUT/f'criteria-bounds-{lang}.svg',metadata={'Date':None});plt.close(fig)

 margins=[x['adverse_margin'] for x in draws];end=math.ceil(max(margins));bins=np.linspace(0,end,25)
 fig,ax=plt.subplots(figsize=(12,6.5));fig.subplots_adjust(left=.10,right=.95,top=.80,bottom=.21)
 counts,edges,_=ax.hist(margins,bins=bins,color='#3979af',edgecolor='white',linewidth=1.1)
 ax.axvline(4,color='#937128',linewidth=1.8,linestyle='--',label=l['equal']);ax.axvline(0,color='#6f7b8b',linewidth=1.2)
 ax.set_xlim(0,end);ax.set_xlabel(l['mx'],labelpad=10);ax.set_ylabel(l['my']);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True);ax.legend(frameon=False,loc='upper left')
 ax.text(.02,.72,f'min = {min(margins):.6f}\nmax = {max(margins):.6f}\nN = 1000',transform=ax.transAxes,fontsize=11,ha='left',va='top',bbox={'facecolor':'#f1f5fa','edgecolor':'none','pad':10})
 fig.text(.055,.94,l['mc'],fontsize=19,fontweight='bold');fig.text(.055,.885,l['mc_sub'],fontsize=11.5,color='#607087');fig.text(.055,.055,l['mc_foot'],fontsize=10)
 fig.savefig(OUT/f'adverse-margin-distribution-{lang}.svg',metadata={'Date':None});plt.close(fig)
print(json.dumps({'svg_count':len(list(OUT.glob('*.svg'))),'trials':len(draws),'min_margin':min(x['adverse_margin'] for x in draws),'max_margin':max(x['adverse_margin'] for x in draws)},ensure_ascii=False))
