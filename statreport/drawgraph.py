import pandas as pd
from wordcloud import WordCloud
from scipy.stats import gaussian_kde
import numpy as np

import matplotlib
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号
matplotlib.rcParams['font.family'] = ['SimHei']  # 指定默认字体
from matplotlib import pyplot as plt
from colors import get_colors, random_color_func

def drawymax(logy: bool):
    ax = plt.gca()
    ymin, ymax = ax.get_ylim()
    max_y_label = f'{ymax:.2f}'
    if logy:
        max_y_label = f'{ymax:.2e}'
    plt.text(0.0, 1, max_y_label, transform=ax.transAxes, va='bottom', ha='left', fontsize=10)

# 生成直方图
def drawhist(column_data: pd.Series, output_dir: str, name: str, xlabel: str, ylabel: str, graph_type: str = '直方图', logy: bool = False):
    plt.figure(dpi=300, figsize=(10, 6))
    plt.grid(True)
    plt.hist(column_data, bins=50, color=(0.9, 0.9, 0.9), edgecolor='black')
    plt.title(f'{name} {graph_type}')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    drawymax(logy)
    if logy:
        plt.yscale('log')
    plt.savefig(f'{output_dir}/hist{"" if not logy else "_log"}.png')
    plt.close()

# 生成柱状图
def drawbar(column_data: pd.Series, output_dir: str, name: str, xlabel: str, ylabel: str, graph_type: str = '柱状图', logy: bool = False):
    plt.figure(dpi=300, figsize=(10, 6))
    plt.grid(True)
    x_data = column_data.index
    y_data = column_data.values
    plt.bar(x_data, y_data, color=get_colors(len(x_data)), edgecolor='black')
    for i in range(len(column_data)):
        plt.text(i, column_data[i], column_data[i], ha='center', va='bottom')
    plt.title(f'{name} {graph_type}')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    drawymax(logy)
    if x_data.str.len().max() > 3:
        plt.xticks(rotation=45)

    if logy:
        plt.yscale('log')
    plt.savefig(f'{output_dir}/bar{"" if not logy else "_log"}.png')
    plt.close()

# 生成密度图
def drawkde(column_data: pd.Series, output_dir: str, name: str, xlabel: str, ylabel: str, graph_type: str = '密度图', logy: bool = False):
    plt.figure(dpi=300, figsize=(10, 6))
    plt.grid(True)
    kde = gaussian_kde(column_data.dropna())
    x_data = np.linspace(int(column_data.min()), int(column_data.max()), 1000)

    y_data = kde.evaluate(x_data)
    plt.plot(x_data, y_data, color='black', alpha=0.9)
    plt.title(f'{name} {graph_type}')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    drawymax(logy)
    if logy:
        plt.yscale('log')
        for tick in plt.gca().yaxis.get_major_ticks():
            tick.label1.set_fontproperties('stixgeneral')
    plt.savefig(f'{output_dir}/kde{"" if not logy else "_log"}.png')
    plt.close()

# 生成饼图
def drawpie(column_data: pd.Series, output_dir: str, name: str, legend: str, graph_type: str = '饼图'):
    plt.figure(dpi=300, figsize=(10, 6))
    
    explode = [0.1] * len(column_data)
    
    wedges, texts, autotexts = plt.pie(
        column_data, 
        explode=explode,  
        autopct='%1.1f%%',  
        colors=get_colors(len(column_data)),
        startangle=90, 
        pctdistance=1.1,  
        labeldistance=None  
    )
    
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    plt.legend(wedges, column_data.index, title=legend, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    plt.title(f'{name} {graph_type}')
    plt.ylabel('')
    plt.savefig(f'{output_dir}/pie.png')
    plt.close()

# 生成词云
def drawwordcloud(words: pd.Series, output_dir: str, name: str):
    words = words.dropna()

    wordcloud = WordCloud(
        font_path='C:/Windows/Fonts/simhei.ttf', 
        background_color='white',
        color_func=random_color_func,
        width=1920, height=1080).generate(' '.join(words))
    plt.figure(dpi=300, figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(f'{output_dir}/wordcloud.png')
    plt.close()