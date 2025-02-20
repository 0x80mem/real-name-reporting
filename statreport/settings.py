COLUMN_TYPE_MAP = {
    'id': 'String',
    'bid': 'String',
    'user_id': 'Int',
    'user_nickname': 'String',
    'weibo_content': 'Text',
    'headline_article_url': 'URL',
    'publish_location': 'Location',
    'at_users': 'List[String]',
    'topics': 'List[String]',
    'retweet_count': 'Int',
    'comment_count': 'Int',
    'like_count': 'Int',
    'publish_time': 'DateTime',
    'publish_tool': 'Enum',
    'weibo_image_urls': 'URL',
    'weibo_video_urls': 'URL',
    'retweet_id': 'String',
    'retweet_url': 'URL',
    'ip_address': 'Enum',
    'user_auth': 'Enum'
}

COLUMN_IGNORE = [
    'id',
    'bid',
    'user_id',
    'user_nickname',
    'headline_article_url',
    'at_users',
    'weibo_image_urls',
    'weibo_video_urls',
    'retweet_id',
    'retweet_url',
]

COLUMN_TRANSLATE = {
    'id': 'ID',
    'bid': '某博ID',
    'user_id': '用户ID',
    'user_nickname': '用户昵称',
    'weibo_content': '某博内容',
    'headline_article_url': '头条文章链接',
    'publish_location': '发布位置',
    'at_users': 'AT用户',
    'topics': '话题',
    'retweet_count': '转发数',
    'comment_count': '评论数',
    'like_count': '点赞数',
    'publish_time': '发布时间',
    'publish_tool': '发布工具',
    'weibo_image_urls': '某博图片链接',
    'weibo_video_urls': '某博视频链接',
    'retweet_id': '转发ID',
    'retweet_url': '转发链接',
    'ip_address': 'IP地址',
    'user_auth': '用户认证'
}

COLUMN_SERIAL_LIST = [
    'weibo_content',
    'topics',
]
