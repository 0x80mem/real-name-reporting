import os
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = "1"

import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, String, BIGINT, Text, Integer, DateTime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from config import db_config
from settings import COLUMN_TYPE_MAP, COLUMN_IGNORE, COLUMN_SERIAL_LIST
from describe import COLUMN_DESCRIBE
from describe2 import COLUMN_DESCRIBE_2
from prase import praseColumn


def get_df_from_db():
    connection_string = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
    engine = create_engine(connection_string)

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

    # 读取weibo_table中的数据
    df = pd.DataFrame()
    with engine.connect() as conn:
        query = weibo_table.select()
        df = pd.read_sql(query, conn)

    # 测试随机抽取10000条数据
    # df = df.sample(n=10000, random_state=1)

    return df

def praseDf(df: pd.DataFrame):
    pool = ThreadPoolExecutor(8)
    features = []
    for column in df.columns:
        if column in COLUMN_IGNORE:
            continue
        features.append((column, pool.submit(praseColumn, ((df[column], column)))))
    for column, feature in features:
        df[column] = feature.result()
    pool.shutdown(wait=True)
    print("praseDf done")
    return df

def statSingleColumns(df):
    pool = ProcessPoolExecutor(8)
    features = []

    for column in df.columns:
        if column in COLUMN_IGNORE or column in COLUMN_SERIAL_LIST:
            continue
        features.append(pool.submit(COLUMN_DESCRIBE[COLUMN_TYPE_MAP[column]], (df[column])))
    for feature in features:
        feature.result()
    for column in COLUMN_SERIAL_LIST:
        if column in COLUMN_IGNORE:
            continue
        COLUMN_DESCRIBE[COLUMN_TYPE_MAP[column]](df[column])
    print("statSingleColumns done")

def statTwoColumns(df):
    pool = ProcessPoolExecutor(8)
    features = []
    for column1 in df.columns:
        for column2 in df.columns:
            if column1 in COLUMN_IGNORE or column2 in COLUMN_IGNORE or column1 == column2:
                continue
            if COLUMN_TYPE_MAP[column2] in COLUMN_DESCRIBE_2[COLUMN_TYPE_MAP[column1]]:
                features.append(pool.submit(COLUMN_DESCRIBE_2[COLUMN_TYPE_MAP[column1]][COLUMN_TYPE_MAP[column2]], (df[column1], df[column2])))
    for feature in features:
        feature.result()
    print("statTwoColumns done")

def main():
    df = get_df_from_db()
    df = praseDf(df)
    statSingleColumns(df)
    statTwoColumns(df)

if __name__ == '__main__':
    main()