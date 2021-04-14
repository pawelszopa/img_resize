import time
from urllib.parse import urlparse
from urllib.request import urlretrieve

import PIL
import requests
from PIL import Image
import os
# aby logowac informacje w pythonie - aby nasz program zapisywal co sie dzieje
# logging
import logging

logging.basicConfig(filename='logfile.log', level=logging.DEBUG)


class ThumbnailMakerService:
    def __init__(self, home_dir='.'):
        self.home_dir = home_dir
        self.input_dir = os.path.join(self.home_dir, 'incoming')
        self.output_dir = os.path.join(self.home_dir, 'outgoing')

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
        if not os.listdir(self.input_dir):
            return

        os.makedirs(self.output_dir, exist_ok=True)

        logging.info('beginning image resizing')

        target_sizes = [32, 64, 200]
        num_images = len(os.listdir(self.input_dir))

        start = time.perf_counter()
        for filename in os.listdir(self.input_dir):
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
            end = time.perf_counter()
            logging.info(f'created {num_images} thumbnails in {end - start} seconds')

    def make_thumbnails(self, img_url_list):
        logging.info("START make_thumbnails")
        start = time.perf_counter()
        self.download_images(img_url_list)
        self.perform_resize()

        end = time.perf_counter()
        logging.info(f'END make_thumbnails in {end - start} seconds')