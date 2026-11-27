#!/usr/bin/env python3
"""Render two additional, distinct charts per language from exact exported data.

Dependencies: matplotlib; Noto Sans CJK font for Chinese.
Run visualization_data.py first. Optional --preview-dir writes 320px QA PNGs.
"""
import argparse, csv, json, pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager, ticker

P=pathlib.Path(__file__).resolve().parent
SLUG='retail-private-label-haircare-packaging-redesign-2026'
OUT=P/'assets'/'research'/SLUG
ap=argparse.ArgumentParser()
ap.add_argument('--preview-dir',type=pathlib.Path)
ap.add_argument('--cjk-font',default='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
args=ap.parse_args()
OUT.mkdir(parents=True,exist_ok=True)
if args.preview_dir: args.preview_dir.mkdir(parents=True,exist_ok=True)
summary=json.loads((P/'VISUALIZATION_DATA.json').read_text())
with (P/'CRITERION_CONTRIBUTIONS.csv').open() as f: criteria=list(csv.DictReader(f))
with (P/'MARGIN_HISTOGRAM.csv').open() as f: bins=list(csv.DictReader(f))
assert len(criteria)==5 and sum(int(x['trials']) for x in bins)==1000
plt.rcParams.update({'svg.fonttype':'path','axes.unicode_minus':False})
labels={
'ru':{'criteria_title':'Откуда взялись 90 баллов','criteria_sub':'Вклад каждого критерия: от 0 до 20',
 'criteria':['Совпадение с брифом','Преемственность','Функциональная навигация','Информационная система','Передача правил'],
 'total':'Итого: 90 / 100','coincide':'Нижняя и верхняя границы\nдля Valori совпадают.',
 'margin_title':'Разница оценок\nв 1000 испытаниях','margin_sub':'Нижняя оценка Heads минус\nмаксимальная граница конкурента',
 'trial_count':'Количество испытаний','x_label':'Разница оценок, баллы',
 'outcomes':'Победы: 863 · поражения: 137\nНичьи: 0',
 'median':'Медиана: +{value:.2f} балла','range':'Диапазон: {low:+.2f} ... {high:+.2f}',
 'note':'Реальные испытания; шаг интервала 1 балл'},
'en':{'criteria_title':'How the score reaches 90','criteria_sub':'Contribution per criterion: 0 to 20',
 'criteria':['Fit to the brief','Recognition continuity','Functional navigation','Information system','Handover of rules'],
 'total':'Total: 90 / 100','coincide':'Valori lower and upper\nbounds coincide.',
 'margin_title':'Score differences\nacross 1,000 trials','margin_sub':'Heads lower score minus\nthe highest competitor upper score',
 'trial_count':'Number of trials','x_label':'Score difference, points',
 'outcomes':'Wins: 863 · losses: 137\nTies: 0',
 'median':'Median: {value:+.2f} points','range':'Range: {low:+.2f} ... {high:+.2f}',
 'note':'Actual trials; histogram bins are 1 point wide'},
'cn':{'criteria_title':'90分由哪些指标构成','criteria_sub':'每项贡献：0至20分',
 'criteria':['任务匹配度','品牌延续性','功能导航','信息体系','规则交付'],
 'total':'总分：90 / 100','coincide':'Valori 的下界与上界一致。',
 'margin_title':'1,000次试验中的\n评分差值','margin_sub':'Heads下界减去\n竞争者最高上界',
 'trial_count':'试验次数','x_label':'评分差值（分）',
 'outcomes':'胜出：863 · 落后：137\n并列：0',
 'median':'中位数：{value:+.2f}分','range':'范围：{low:+.2f} ... {high:+.2f}',
 'note':'实际试验；直方图区间宽度为1分'}}

def save(fig, stem, lang, description):
    fig.savefig(OUT/f'{stem}-{lang}.svg',format='svg',metadata={'Title':stem,'Description':description})
    if args.preview_dir:
        fig.savefig(args.preview_dir/f'{stem}-{lang}-320.png',dpi=320/7.2)
    plt.close(fig)

for lang,t in labels.items():
    if lang=='cn':
        font=font_manager.FontProperties(fname=args.cjk_font)
    else: font=font_manager.FontProperties(family='DejaVu Sans')
    def text(ax,x,y,s,size=20,weight='normal',color='#183448',ha='left'):
        ax.text(x,y,s,fontsize=size,fontproperties=font,fontweight=weight,color=color,ha=ha,va='top',linespacing=1.4)
    fig=plt.figure(figsize=(7.2,9.4),facecolor='#f7fafc')
    ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
    text(ax,.065,.965,t['criteria_title'],24,'bold')
    text(ax,.065,.91,t['criteria_sub'],16,color='#536b7b')
    for i,(c,label) in enumerate(zip(criteria,t['criteria'])):
        y=.823-i*.128
        low=float(c['contribution_low']);high=float(c['contribution_high'])
        assert low==high
        text(ax,.065,y,label,19,'bold')
        text(ax,.935,y,f'{low:g}',23,'bold',ha='right')
        ax.add_patch(plt.Rectangle((.065,y-.078),.87,.035,color='#e3ebf1',linewidth=0))
        ax.add_patch(plt.Rectangle((.065,y-.078),.87*low/20,.035,color='#147d76',linewidth=0))
    text(ax,.065,.171,t['total'],26,'bold',color='#147d76')
    text(ax,.065,.10,t['coincide'],16,color='#536b7b')
    save(fig,'criteria',lang,'Target criterion contributions from CRITERION_CONTRIBUTIONS.csv: 20,20,20,20,10; total=90. Raw levels 3/3,2/2,2/2,2/2,1/2. All target lower/upper bounds coincide.')

    fig=plt.figure(figsize=(7.2,10.2),facecolor='#f7fafc')
    whole=fig.add_axes([0,0,1,1]);whole.set_xlim(0,1);whole.set_ylim(0,1);whole.axis('off')
    text(whole,.065,.965,t['margin_title'],25,'bold')
    text(whole,.065,.86,t['margin_sub'],16,color='#536b7b')
    ax=fig.add_axes([.15,.355,.80,.39]);ax.set_facecolor('#f7fafc')
    centres=[(float(b['left_inclusive'])+float(b['right_exclusive']))/2 for b in bins]
    counts=[int(b['trials']) for b in bins]
    colours=['#bc6854' if x<0 else '#147d76' for x in centres]
    ax.bar(centres,counts,width=.90,color=colours,edgecolor='none')
    ax.axvline(0,color='#183448',linewidth=1.5,linestyle=(0,(3,3)))
    ax.set_xlim(-4,10);ax.set_xticks([-4,0,4,8])
    ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=4,integer=True))
    ax.spines[['top','right']].set_visible(False)
    ax.spines[['bottom','left']].set_color('#b2c6d3')
    ax.set_axisbelow(True);ax.grid(axis='y',color='#d8e3ea',linewidth=.8)
    for tick in ax.get_xticklabels()+ax.get_yticklabels():
        tick.set_fontproperties(font);tick.set_fontsize(18);tick.set_color('#536b7b')
    ax.set_xlabel(t['x_label'],fontproperties=font,fontsize=18,labelpad=10,color='#183448')
    text(whole,.15,.78,t['trial_count'],16,color='#536b7b')
    text(whole,.065,.26,t['outcomes'],19,'bold')
    med=t['median'].format(value=summary['medianMargin'])
    ran=t['range'].format(low=summary['minimumMargin'],high=summary['maximumMargin'])
    if lang=='ru': med=med.replace('.',',');ran=ran.replace('.',',').replace(',,,','...')
    text(whole,.065,.17,med,18,'bold',color='#147d76')
    text(whole,.065,.12,ran,16,color='#536b7b')
    text(whole,.065,.06,t['note'],13,color='#536b7b')
    save(fig,'trial-margins',lang,'Actual 1000 adverse-trial margins from calculate.py. Wins=863; losses=137; ties=0; median='+str(summary['medianMargin'])+'; minimum='+str(summary['minimumMargin'])+'; maximum='+str(summary['maximumMargin'])+'. Histogram data in MARGIN_HISTOGRAM.csv; every draw in WEIGHT_TRIALS.csv.')
    print(lang,'criteria and trial-margins rendered')
