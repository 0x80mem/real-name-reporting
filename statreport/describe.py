import os
import pandas as pd
from settings import COLUMN_TRANSLATE
from drawgraph import drawhist, drawkde, drawwordcloud, drawpie, drawbar

def createDir(column_data: pd.Series):
    output_dir = f'output/{COLUMN_TRANSLATE[column_data.name]}'
    os.makedirs(output_dir, exist_ok=True)
    for file in os.listdir(output_dir):
        os.remove(f'{output_dir}/{file}')
    return output_dir

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
    words = column_data.apply(pd.Series).stack()

    # 生成描述文件
    with open(f'{output_dir}/describe.txt', 'w') as f:
        describeToFile(words.value_counts(), COLUMN_TRANSLATE[column_data.name], f)
        
    # 生成词云
    drawwordcloud(words, output_dir, COLUMN_TRANSLATE[column_data.name])

    # 合并较小项
    words = words.value_counts()
    words = words[words.index.str.len() > 1]
    limit = words.head(19).min()
    words['其他'] = words[words < limit].sum()
    words = words[words >= limit]

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
    drawwordcloud(column_data, output_dir, COLUMN_TRANSLATE[column_data.name])

    # 合并较小项
    enums = column_data.value_counts()
    limit = enums.head(19).min()
    enums['其他'] = enums[enums < limit].sum()
    enums = enums[enums >= limit]

    # 生成词频图
    drawbar(enums, output_dir, COLUMN_TRANSLATE[column_data.name], '词', '数量', '')

    # 生成饼图
    drawpie(enums, output_dir, COLUMN_TRANSLATE[column_data.name], COLUMN_TRANSLATE[column_data.name], '占比')

    print(f'{COLUMN_TRANSLATE[column_data.name]}: complete')

def __describeNone(column_data: pd.Series):
    pass

COLUMN_DESCRIBE = {
    'Int': describeInt,
    'List[String]': describeListString,
    'Text': describeText,
    'Location': __describeNone,
    'DateTime': __describeNone,
    'Enum': describeEnum,
    'URL': __describeNone,
    'String': __describeNone,
}
