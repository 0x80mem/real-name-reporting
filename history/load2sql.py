import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, BIGINT, Text
from mysql.connector import Error
from datetime import datetime
import tqdm
import os
import zipfile
from config import db_config
from chardet import detect

# 中文列名到英文列名的映射
column_mapping = {
    'id': 'id',
    'bid': 'bid',
    'user_id': 'user_id',
    '用户昵称': 'user_nickname',
    '微博正文': 'weibo_content',
    '头条文章url': 'headline_article_url',
    '发布位置': 'publish_location',
    '艾特用户': 'at_users',
    '话题': 'topics',
    '转发数': 'retweet_count',
    '评论数': 'comment_count',
    '点赞数': 'like_count',
    '发布时间': 'publish_time',
    '发布工具': 'publish_tool',
    '微博图片url': 'weibo_image_urls',
    '微博视频url': 'weibo_video_urls',
    'retweet_id': 'retweet_id',
    '转发url': 'retweet_url',
    'ip': 'ip_address',
    'user_authentication': 'user_auth'
}

# 尝试的编码列表
ENCODINGS_TO_TRY = ['latin1', 'utf-8', 'gbk', 'cp437']

def guess_encoding(byte_string):
    """尝试猜测给定字节串的编码"""
    result = detect(byte_string)
    if result['encoding']:
        return result['encoding']
    return None

def decode_filename(filename_bytes, encodings=None):
    """尝试用给定的编码列表解码文件名"""
    encodings = encodings or ENCODINGS_TO_TRY
    for encoding in encodings:
        try:
            return filename_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    # 如果所有编码都失败，返回原始字节串
    return filename_bytes.decode('latin1', errors='replace')  # 使用 latin1 作为最后的选择

try:
    # 创建数据库连接
    connection_string = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
    engine = create_engine(connection_string)
    
    # 创建表（如果表不存在）
    metadata = MetaData()

    weibo_table = Table('weibo_data', metadata,
        Column('id', String(16), primary_key=True),
        Column('bid', String(255)),
        Column('user_id', BIGINT),
        Column('user_nickname', String(255)),
        Column('weibo_content', Text),
        Column('headline_article_url', String(255)),
        Column('publish_location', String(255)),
        Column('at_users', Text),
        Column('topics', Text),
        Column('retweet_count', Integer),
        Column('comment_count', Integer),
        Column('like_count', Integer),
        Column('publish_time', DateTime),
        Column('publish_tool', String(255)),
        Column('weibo_image_urls', Text),
        Column('weibo_video_urls', Text),
        Column('retweet_id', String(255)),
        Column('retweet_url', String(255)),
        Column('ip_address', String(255)),
        Column('user_auth', String(255))
    )
    metadata.create_all(engine, checkfirst=True)  # 只在表不存在时创建
    """遍历指定目录下的所有ZIP文件，并读取其中的 结果文件/实名举报/实名举报.csv"""
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith('.zip'):
                zip_path = os.path.join(root, file)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_path = os.path.join(root, file)
                    
                    # 尝试找到匹配的CSV文件（忽略大小写）
                    for file in zip_ref.namelist():
                        if file.lower().endswith('.csv'):
                            csv_file_name = file
                            break
                    
                    with zip_ref.open(csv_file_name) as csv_file:
                        # 使用pandas读取CSV文件并重命名列
                        encoding = guess_encoding(csv_file.read(4096))
                        csv_file.seek(0)
                        df = pd.read_csv(csv_file, encoding=encoding, low_memory=False)
                        df.rename(columns=column_mapping, inplace=True)

                        # 将 NaN 值替换为 None
                        df = df.where(pd.notnull(df), None)

                        # 日期时间格式化
                        df['publish_time'] = pd.to_datetime(df['publish_time'], errors='coerce')

                        # 将DataFrame中的数据插入到MySQL表中
                        chunksize = 1000
                        with tqdm.tqdm(total=len(df), desc=f"导入{zip_path} encoding={encoding}") as pbar:
                            for i in range(0, len(df), chunksize):
                                df.iloc[i:i+chunksize].to_sql('weibo_data', con=engine, if_exists='append', index=False)
                                pbar.update(chunksize)

    print("数据成功导入到MySQL数据库")

except Error as e:
    print(f"Error: {e}")

finally:
    if engine:
        engine.dispose()