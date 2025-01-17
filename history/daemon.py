import datetime
import time
import multiprocessing
from request_img import main

if __name__ == "__main__":
    while True:
        process = multiprocessing.Process(target=main)
        process.start()
        print(f"{datetime.datetime.now()}: Started request_img.py with PID {process.pid}")
        process.join()
        time.sleep(10)