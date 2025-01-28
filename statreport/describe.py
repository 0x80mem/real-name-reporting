import os
import pandas as pd
from tqdm import tqdm
from collections import Counter
from settings import COLUMN_TRANSLATE
from drawgraph import drawhist, drawkde, drawwordcloud, drawpie, drawbar, drawline

def createDir(column_data: pd.Series):
    output_dir = f'output/{COLUMN_TRANSLATE[column_data.name]}'
    os.makedirs(output_dir, exist_ok=True)
    for file in os.listdir(output_dir):
        os.remove(f'{output_dir}/{file}')
    return output_dir

# 合并较小项
def mergeSmallItems(df: pd.Series, n: int):
    if len(df) > n:
        limit = df.head(n - 1).min()
        other_sum = df[df < limit].sum()
        df = df[df >= limit]
        df['其他'] = other_sum
    return df


def describeToFile(df: pd.Series, name, file):
    file.write(f'{name}数量: {len(df)}\n')
    file.write(f'{name}最大值: {df.max()}\n')
    file.write(f'{name}最小值: {df.min()}\n')
    file.write(f'{name}平均值: {df.mean()}\n')
    file.write(f'{name}中位数: {df.median()}\n')
    file.write(f'{name}标准差: {df.std()}\n')
    file.write(f'{name}缺失值: {df.isnull().sum()}\n')
    file.write(f'{name}众数: {df.mode()}\n')
    file.write(f'{name}众数数量: {df.value_counts().max()}\n')
    file.write(f'{name}25%分位数: {df.quantile(0.25)}\n')
    file.write(f'{name}50%分位数: {df.quantile(0.5)}\n')
    file.write(f'{name}75%分位数: {df.quantile(0.75)}\n')
    file.write(f'{name}偏度: {df.skew()}\n')
    file.write(f'{name}峰度: {df.kurt()}\n')

def describeInt(column_data: pd.Series):
    # 创建输出文件
    output_dir = createDir(column_data)

    # print(f"{COLUMN_TRANSLATE[column_data.name]}: type counts:{column_data.apply(type).value_counts()}")

    # 生成描述文件
    with open(f'{output_dir}/describe.txt', 'w') as f:
        describeToFile(column_data, COLUMN_TRANSLATE[column_data.name], f)
    
    drawhist(column_data, output_dir, COLUMN_TRANSLATE[column_data.name], COLUMN_TRANSLATE[column_data.name], '数量', '直方图')
    drawkde(column_data, output_dir, COLUMN_TRANSLATE[column_data.name], COLUMN_TRANSLATE[column_data.name], '概率密度', '密度图')

    if column_data.kurt() > 3:
        drawhist(column_data, output_dir, COLUMN_TRANSLATE[column_data.name], COLUMN_TRANSLATE[column_data.name], '数量', '对数直方图', logy=True)
        drawkde(column_data, output_dir, COLUMN_TRANSLATE[column_data.name], COLUMN_TRANSLATE[column_data.name], '概率密度', '对数密度图', logy=True)

    print(f'{COLUMN_TRANSLATE[column_data.name]}: complete')

def describeListString(column_data: pd.Series):
    output_dir = createDir(column_data)
    # 使用生成器逐行处理数据
    def extract_words(series: pd.Series):
        for words in series:
            if isinstance(words, list):
                yield from words

    word_counter = Counter()
    with tqdm(total=len(column_data)) as pbar:
        pbar.set_description(f'处理{COLUMN_TRANSLATE[column_data.name]}')
        for word in extract_words(column_data):
            word_counter[word] += 1
            pbar.update(1)
    words = pd.Series(word_counter)
    words = words.sort_values(ascending=False)

    # 生成描述文件
    with open(f'{output_dir}/describe.txt', 'w') as f:
        describeToFile(words, COLUMN_TRANSLATE[column_data.name], f)
        
    # 生成词云
    drawwordcloud(words, output_dir, COLUMN_TRANSLATE[column_data.name])

    # 合并较小项
    words = mergeSmallItems(words, 20)

    drawbar(words, output_dir, COLUMN_TRANSLATE[column_data.name], '词', '数量', '')

    if words.kurt() > 3:
        drawbar(words, output_dir, COLUMN_TRANSLATE[column_data.name], '词', '数量', '对数柱状图', logy=True)

    drawpie(words, output_dir, COLUMN_TRANSLATE[column_data.name], '词', '饼图')

    print(f'{COLUMN_TRANSLATE[column_data.name]}: complete')

def describeText(column_data: pd.Series):
    describeListString(column_data)

def describeEnum(column_data: pd.Series):
    output_dir = createDir(column_data)

    # 生成描述文件
    with open(f'{output_dir}/describe.txt', 'w') as f:
        describeToFile(column_data.value_counts(), COLUMN_TRANSLATE[column_data.name], f)

    # 生成词云
    enums = column_data.value_counts()
    drawwordcloud(enums, output_dir, COLUMN_TRANSLATE[column_data.name])

    # 合并较小项
    enums = mergeSmallItems(enums, 20)

    # 生成词频图
    drawbar(enums, output_dir, COLUMN_TRANSLATE[column_data.name], '词', '数量', '')

    # 生成饼图
    drawpie(enums, output_dir, COLUMN_TRANSLATE[column_data.name], COLUMN_TRANSLATE[column_data.name], '占比')

    print(f'{COLUMN_TRANSLATE[column_data.name]}: complete')

def describeLocation(column_data: pd.Series):
    output_dir = createDir(column_data)

    location_df = pd.DataFrame(index=column_data.index, columns=['城市'])
    for idx, locations in column_data.items():
        if locations != None:
                location_df.at[idx, '城市'] = locations[0]

    # 生成描述文件
    with open(f'{output_dir}/describe.txt', 'w') as f:
        describeToFile(location_df['城市'].value_counts(), '城市', f)
    
    locations = location_df['城市'].value_counts()
    drawwordcloud(locations, output_dir, '城市')

    # 合并较小项
    locations = mergeSmallItems(locations, 15)

    drawbar(locations, output_dir, '城市', '城市', '数量')
    drawpie(locations, output_dir, '城市', '城市', '占比')

    print(f'{COLUMN_TRANSLATE[column_data.name]}: complete')

def describeDateTime(column_data: pd.Series):
    output_dir = createDir(column_data)

    if not pd.api.types.is_datetime64_any_dtype(column_data):
        column_data = pd.to_datetime(column_data)
    
    # 按月统计数量
    counts = column_data.groupby(column_data.dt.to_period("M")).count()
    counts.index = counts.index.to_timestamp()

    # 生成描述文件
    with open(f'{output_dir}/describe.txt', 'w') as f:
        describeToFile(counts, f"{COLUMN_TRANSLATE[column_data.name]}每月", f)
    drawline(counts, output_dir, COLUMN_TRANSLATE[column_data.name], '年', '每月数量', '折线图', peak_count=3)

    print(f'{COLUMN_TRANSLATE[column_data.name]}: complete')


def __describeNone(column_data: pd.Series):
    pass

COLUMN_DESCRIBE = {
    'Int': describeInt,
    'List[String]': describeListString,
    'Text': describeText,
    'Location': describeLocation,
    'DateTime': describeDateTime,
    'Enum': describeEnum,
    'URL': __describeNone,
    'String': __describeNone,
}
