import pandas as pd

def __describeNone(columns_data: list):
    x_data: pd.Series = columns_data[0]
    y_data: pd.Series = columns_data[1]
    pass

COLUMN_DESCRIBE_2 = {
    'Int': {
        'Int': __describeNone,
        'List[String]': __describeNone,
        'Text': __describeNone,
        'Location': __describeNone,
        'DateTime': __describeNone,
        'Enum': __describeNone,
        'URL': __describeNone,
        'String': __describeNone,
    },
    'List[String]': {
        'Int': __describeNone,
        'List[String]': __describeNone,
        'Text': __describeNone,
        'Location': __describeNone,
        'DateTime': __describeNone,
        'Enum': __describeNone,
        'URL': __describeNone,
        'String': __describeNone,
    },
    'Text': {
        'Int': __describeNone,
        'List[String]': __describeNone,
        'Text': __describeNone,
        'Location': __describeNone,
        'DateTime': __describeNone,
        'Enum': __describeNone,
        'URL': __describeNone,
        'String': __describeNone,
    },
    'Location': {
        'Int': __describeNone,
        'List[String]': __describeNone,
        'Text': __describeNone,
        'Location': __describeNone,
        'DateTime': __describeNone,
        'Enum': __describeNone,
        'URL': __describeNone,
        'String': __describeNone,
    },
    'DateTime': {
        'Int': __describeNone,
        'List[String]': __describeNone,
        'Text': __describeNone,
        'Location': __describeNone,
        'DateTime': __describeNone,
        'Enum': __describeNone,
        'URL': __describeNone,
        'String': __describeNone,
    },
    'Enum': {
        'Int': __describeNone,
        'List[String]': __describeNone,
        'Text': __describeNone,
        'Location': __describeNone,
        'DateTime': __describeNone,
        'Enum': __describeNone,
        'URL': __describeNone,
        'String': __describeNone,
    },
    'URL': {
        'Int': __describeNone,
        'List[String]': __describeNone,
        'Text': __describeNone,
        'Location': __describeNone,
        'DateTime': __describeNone,
        'Enum': __describeNone,
        'URL': __describeNone,
        'String': __describeNone,
    },
    'String': {
        'Int': __describeNone,
        'List[String]': __describeNone,
        'Text': __describeNone,
        'Location': __describeNone,
        'DateTime': __describeNone,
        'Enum': __describeNone,
        'URL': __describeNone,
        'String': __describeNone,
    }
}