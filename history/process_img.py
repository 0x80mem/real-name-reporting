import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HOME'] = 'pretrained/'
import cv2
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR
from transformers import BlipProcessor, BlipForConditionalGeneration
import logging
import torch
import multiprocessing
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Text
import traceback
from config import db_config
import paddle

logging.getLogger('ppocr').setLevel(logging.ERROR)

ocr = PaddleOCR(
    lang='ch', 
    use_gpu=True, 
    ocr_version="PP-OCRv4", 
    # use_tensorrt=True,
    use_pdserving=True,
    precision="int8")

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to("cuda")

def should_use_det(image):
    hist_size = [8, 8, 8]
    hist_range = [0, 256, 0, 256, 0, 256]
    channels = [0, 1, 2]
    
    hist = cv2.calcHist([image], channels, None, hist_size, hist_range)
    cv2.normalize(hist, hist)
    
    # 计算直方图的熵作为复杂度指标
    entropy = -np.sum(hist * np.log2(hist + 1e-7))
    
    # 使用Canny边缘检测检查图像是否有明显的边缘
    edges = cv2.Canny(image, 100, 200)
    edge_density = cv2.countNonZero(edges) / (edges.size)
    
    if entropy < 1.5 and edge_density < 0.02:
        return False
    
    return True

def recognize_text_from_image(image):
    try:
        result = ocr.ocr(image)
        paddle.device.cuda.empty_cache()
        if result == [None]:
            return []
        return [line[1][0] for line in result[0]]
    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        print(e)
        traceback.print_exc()
        return e

def generate_caption_from_image(image):
    try:
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        inputs = processor(image, return_tensors="pt").to("cuda")
        out = model.generate(**inputs)
        torch.cuda.empty_cache()
        return processor.decode(out[0], skip_special_tokens=True)
    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        if str(e) not in [
            "mean must have 1 elements if it is an iterable, got 3"
        ]:
            print(e)
            traceback.print_exc()
        return e

connection_string = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
engine = create_engine(connection_string)

metadata = MetaData()

# 定义 image_text 表结构
image_table = Table(
    'image_text', metadata,
    Column('url', String(255), primary_key=True),
    Column('texts', Text),
    Column('description', Text)
)

request_image_queue = multiprocessing.Queue(20)
request_text_from_image_queue = multiprocessing.Queue(1)
request_caption_from_image_queue = multiprocessing.Queue(1)
response_text_from_image_queue = {}
response_caption_from_image_queue = {}
image2sql_queue = multiprocessing.Queue(5)

def request_image(url, image):
    request_image_queue.put((url, image))

def response_text_from_image():
    while True:
        try:
            url, image = request_text_from_image_queue.get()
            texts = recognize_text_from_image(image)
            response_text_from_image_queue[url].put(texts)
        except KeyboardInterrupt:
            break
        except EOFError:
            break
        except OSError:
            break
        except Exception as e:
            print(e)
            traceback.print_exc()

def response_caption_from_image():
    while True:
        try:
            url, image = request_caption_from_image_queue.get()
            caption = generate_caption_from_image(image)
            response_caption_from_image_queue[url].put(caption)
        except KeyboardInterrupt:
            break
        except EOFError:
            break
        except OSError:
            break
        except Exception as e:
            print(e)
            traceback.print_exc()

def image2sql():
    while True:
        try:
            url = image2sql_queue.get()
            with engine.connect() as conn:
                image_table = Table('image_text', metadata, autoload_with=conn)
                has_old = conn.execute(image_table.select().where(image_table.c.url == url)).fetchone()
                texts = response_text_from_image_queue[url].get()
                caption = response_caption_from_image_queue[url].get()
                if isinstance(texts, Exception) or isinstance(caption, Exception):
                    continue

                texts = "\n".join(texts)
                # print(url, texts, caption)
                if has_old:
                    conn.execute(image_table.update().where(image_table.c.url == url).values(texts=texts, description=caption))
                else:
                    conn.execute(image_table.insert().values(url=url, texts=texts, description=caption))
                conn.commit()
        except KeyboardInterrupt:
            break
        except EOFError:
            break
        except OSError:
            break
        except Exception as e:
            print(e)
            traceback.print_exc()
    

def response_image():
    while True:
        try:
            url, image = request_image_queue.get()
            if url not in response_text_from_image_queue:
                response_text_from_image_queue[url] = multiprocessing.Queue(1)
                response_caption_from_image_queue[url] = multiprocessing.Queue(1)
            request_text_from_image_queue.put((url, image))
            request_caption_from_image_queue.put((url, image))
            image2sql_queue.put(url)
        except KeyboardInterrupt:
            break
        except EOFError:
            break
        except OSError:
            break
        except Exception as e:
            print(e)
            traceback.print_exc()



