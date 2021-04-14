import multiprocessing
import time
from queue import Queue
from threading import Thread, Lock
from urllib.parse import urlparse
from urllib.request import urlretrieve
import queue

import PIL
import requests
from PIL import Image
import os
# aby logowac informacje w pythonie - aby nasz program zapisywal co sie dzieje
# logging
import logging

FORMAT = '[%(threadName)s, %(asctime)s, %(levelname)s] %(message)s'

logging.basicConfig(filename='logfile.log', level=logging.DEBUG, format=FORMAT)


class ThumbnailMakerService:
    def __init__(self, home_dir='.'):
        self.home_dir = home_dir
        self.input_dir = os.path.join(self.home_dir, 'incoming')
        self.output_dir = os.path.join(self.home_dir, 'outgoing')
        self.img_queue = multiprocessing.JoinableQueue()  # nie jest to Queue ktore jest 100% kompatibilne z python queue wiec uzywamy joinableQueue
        # self.dl_queue = Queue() kolejka out bo jest nie picklowalna
        self.dl_size = 0
        self.resized_size = multiprocessing.Value('i',
                                                  0)  # i(integer) to typ danych bo jest z C++// sumowanie pomiedzy procesami (synchronizacja - shared memory oznacza sie zmienna ze jest szarowana or process manager - moze polaczyc processy - moze skonfigurowac kilka procesorow(np PC))

    def download_image(self, dl_queue, dl_size_lock): # queueue moze byc uzywane bo jest przez thready wiec tutaj ja przekazujemy
        while not dl_queue.empty():
            logging.info('Yolo')
            try:
                url = dl_queue.get(block=False)

                img_filename = urlparse(url).path.split('/')[-1]
                img_filepath = self.input_dir + os.path.sep + img_filename
                urlretrieve(url, img_filepath)

                with dl_size_lock:
                    self.dl_size += os.path.getsize(img_filepath)

                self.img_queue.put(img_filename)

                dl_queue.task_done()
            except queue.Empty:
                logging.info('Queue empty')

    def download_images(self, img_url_list):

        if not img_url_list:
            return

        os.makedirs(self.input_dir, exist_ok=True)
        start = time.perf_counter()
        logging.info('beginning image downloads')
        for url in img_url_list:
            img_filename = urlparse(url).path.split('/')[-1]
            urlretrieve(url, self.input_dir + os.path.sep + img_filename)

        end = time.perf_counter()

        logging.info(f'downloaded {len(img_url_list)} images in {end - start}')

    def perform_resize(self):
        os.makedirs(self.output_dir, exist_ok=True)

        logging.info('beginning image resizing')

        target_sizes = [32, 64, 200]

        while True:
            filename = self.img_queue.get()
            if filename is not None:
                logging.info(f'resizing image {filename}')
                orig_img = Image.open(self.input_dir + os.path.sep + filename)
                for base_width in target_sizes:
                    img = orig_img
                    w_percent = (base_width / float(img.size[0]))
                    h_size = int(float(img.size[1] * float(w_percent)))

                    img = img.resize((base_width, h_size), PIL.Image.LANCZOS)
                    new_filename = os.path.splitext(filename)[0] + '_' + str(base_width) + os.path.splitext(filename)[1]
                    out_filepath = os.path.join(self.output_dir, new_filename)
                    img.save(out_filepath)

                    # self.output_dir + os.path.sep+new_filename
                    with self.resized_size.get_lock():
                        self.resized_size.value += os.path.getsize(out_filepath)

                os.remove(self.input_dir + os.path.sep + filename)
                logging.info(f"done resizing image: {filename}")

                self.img_queue.task_done()
            else:
                self.img_queue.task_done()
                break

    def make_thumbnails(self, img_url_list):
        logging.info("START make_thumbnails")
        start = time.perf_counter()

        dl_queue = Queue()
        dl_size_lock = Lock()

        for img_url in img_url_list:
            dl_queue.put(img_url)

        num_dl_threads = 2
        for _ in range(num_dl_threads):
            t = Thread(target=self.download_image, args=(dl_queue, dl_size_lock))
            t.start()

        num_process = multiprocessing.cpu_count() # zwraca ilosc rdzeni
        for _ in range(num_process):
            p = multiprocessing.Process(target=self.perform_resize)
            p.start()

        dl_queue.join()
        # trzeba zrobic poison na kazdy process
        for _ in range(num_process):
            self.img_queue.put(None)

        end = time.perf_counter()
        logging.info(f'END make_thumbnails in {end - start} seconds')
        logging.info(f'Initial size of downloads {self.dl_size}. Final size of images: {self.resized_size.value}')
