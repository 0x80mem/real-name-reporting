from sqlalchemy import create_engine, MetaData, Table, Column, String, Text, text
from PIL import UnidentifiedImageError
from mysql.connector import Error
from threading import Thread
from chardet import detect
import numpy as np
import traceback
import shutil
import time
import math
import tqdm
import cv2

from utils import get_img_from_url
from process_img import request_image, response_text_from_image, response_caption_from_image, image2sql, response_image
from config import db_config

SHRT_MAX = 32767
REPLACE_OLD = False

class ExceptionDiskRunningOut(Exception):
    pass

def check_disk_space(threshold_gb=5):
    """Check if the C drive has more than `threshold_gb` gigabytes free."""
    total, used, free = shutil.disk_usage("C:\\")
    free_gb = free // (2**30)
    return free_gb > threshold_gb

def guess_encoding(byte_string):
    """尝试猜测给定字节串的编码"""
    result = detect(byte_string)
    if result['encoding']:
        return result['encoding']
    return None

def preprocess_image(image):
    img = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    height, width = img.shape[:2]
    max_scale = min(math.sqrt(pow(2, 28) / (height * width)), math.floor(SHRT_MAX / max(height, width)))  # 限制最大尺寸为 2^30 像素
    img = cv2.resize(img, (int(width * min(max_scale, 1)), int(height * min(max_scale, 1))))
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 灰度化
    # img = cv2.GaussianBlur(img, (5, 5), 0)   # 高斯模糊去噪
    # img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)  # 自适应二值化

    return img

def download_and_process_image(url):
    """下载并处理图像"""
    img = get_img_from_url(url)
    return preprocess_image(np.array(img))

def download_and_request_image():
    try:
        clock = time.time()
        # 创建数据库连接
        connection_string = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
        engine = create_engine(connection_string)
        
        # 创建表（如果表不存在）
        metadata = MetaData()

        image_table = Table(
            'image_text', metadata,
            Column('url', String(255), primary_key=True),
            Column('texts', Text),
            Column('description', Text)
        )

        metadata.create_all(engine)

        # 遍历表 weibo_data
        with engine.connect() as conn:
            with tqdm.tqdm(total=conn.execute(text("SELECT COUNT(*) FROM weibo_data")).fetchone()[0]) as pbar:
                pbar.set_description("Processing images")
                for row in conn.execute(text("SELECT weibo_image_urls FROM weibo_data")):
                    if not row[0]:
                        pbar.update(1)
                        continue
                    urls = row[0].split(",")
                    for url in urls:
                        try:
                            start_time = time.time()
                            has_old = conn.execute(image_table.select().where(image_table.c.url == url)).fetchone()
                            if not REPLACE_OLD and has_old:
                                continue

                            # 打开图像
                            img = download_and_process_image(url)
                            request_image(url, img)
                            
                            end_time = time.time()
                            time.sleep(max(0.5, 0.5 - (end_time - start_time)))
                        except UnidentifiedImageError as e:
                            continue
                        except OSError as e:
                            continue
                        except Exception as e:
                            print(f"Error processing {url}")
                            print(e)
                            traceback.print_exc()
                            continue
                    pbar.update(1)
                    if time.time() - clock > 60 * 40:
                        print("Time out")
                        break
                    if not check_disk_space():
                        raise ExceptionDiskRunningOut
    except Error as e:
        print(f"Error: {e}")
        traceback.print_exc()
    except ExceptionDiskRunningOut:
        print("Disk running out")
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
        traceback.print_exc()

    finally:
        if engine:
            engine.dispose()

def main():
    download_and_process_thread = Thread(target=download_and_request_image)
    download_and_process_thread.start()

    Thread(target=response_text_from_image).start()
    Thread(target=response_caption_from_image).start()
    Thread(target=image2sql).start()
    Thread(target=response_image).start()

    download_and_process_thread.join()
    time.sleep(10)

if __name__ == "__main__":
    main()