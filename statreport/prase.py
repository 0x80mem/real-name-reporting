from datetime import datetime
import jieba

from settings import COLUMN_TYPE_MAP

def parseInt(column_data):
    if not column_data:
        return None
    if type(column_data) == str:
        if column_data.endswith('万+'):
            return int(column_data.replace('万+', '')) * 10000
        return int(column_data.replace(',', ''))
    return int(column_data)

def praseListString(column_data):
    if not column_data:
        return None
    return column_data.split(',')

with open('baidu_stopwords.txt', 'r', encoding='utf-8') as f:
    stopwords = set(f.read().splitlines())

def parseText(column_data):
    if not column_data:
        return None
    words = jieba.lcut(column_data, cut_all=True)
    return [word for word in words if word not in stopwords]

jieba.load_userdict('location_dict.txt')
def praseLocation(column_data):
    if not column_data:
        return None
    locations = jieba.lcut(column_data)
    return [location for location in locations if location not in stopwords]

def praseDateTime(column_data):
    if not column_data:
        return None
    return datetime.fromtimestamp(column_data.timestamp())
        
def praseColumn(args):
    column, column_type = args
    match COLUMN_TYPE_MAP[column_type]:
        case 'Int':
            return column.apply(parseInt)
        case 'List[String]':
            return column.apply(praseListString)
        case 'Text':
            return column.apply(parseText)
        case 'Location':
            return column.apply(praseLocation)
        case 'DateTime':
            return column.apply(praseDateTime)
        case _:
            return column