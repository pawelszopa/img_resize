import time
from queue import Queue
from threading import Thread
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
        self.img_queue = Queue()
        self.dl_queue = Queue()

    def download_image(self):
        while not self.dl_queue.empty():
            logging.info('Yolo')
            try:
                url = self.dl_queue.get(block=False)

                img_filename = urlparse(url).path.split('/')[-1]
                urlretrieve(url, self.input_dir + os.path.sep + img_filename)

                self.img_queue.put(img_filename)

                self.dl_queue.task_done()
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

        start = time.perf_counter()
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
                    img.save(os.path.join(self.output_dir, new_filename))
                    # self.output_dir + os.path.sep+new_filename
                os.remove(self.input_dir + os.path.sep + filename)

                self.img_queue.task_done()
            else:
                self.img_queue.task_done()
                break
        end = time.perf_counter()
        logging.info(f'created thumbnails in {end - start} seconds')

    def make_thumbnails(self, img_url_list):
        logging.info("START make_thumbnails")
        start = time.perf_counter()
        for img_url in img_url_list:
            self.dl_queue.put(img_url)

        num_dl_threads = 12
        for _ in range(num_dl_threads):
            t = Thread(target=self.download_image)
            t.start()

        t2 = Thread(target=self.perform_resize)
        t2.start()

        self.dl_queue.join()
        self.img_queue.put(None)  # poison pill aby przerwac threada
        t2.join()

        end = time.perf_counter()
        logging.info(f'END make_thumbnails in {end - start} seconds')
