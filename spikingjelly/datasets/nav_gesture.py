import spikingjelly
import zipfile
import os
import threading
import tqdm
import numpy as np
import torch
from torch.utils.data import Dataset
from torchvision.datasets import utils
import shutil

# url md5
resource = {
    'walk': ['https://www.neuromorphic-vision.com/public/downloads/navgesture/navgesture-walk.zip',
             '5d305266f13005401959e819abe206f0'],
    'sit': ['https://www.neuromorphic-vision.com/public/downloads/navgesture/navgesture-sit.zip', None]
}


# The file format is .dat (CCAM ATIS), and contains only td events (no aps events).
# It can be easily read using the Loris python toolbox -- https://github.com/neuromorphic-paris/loris/ -- or the python script provided -- read_td_events.py --.
#
# Events are encoded in binary format on 64 bits (8 bytes):
# 32 bits for timestamp
# 9 bits for x address
# 8 bits for y address
# 2 bits for polarity
# 13 bits padding
class NavGesture(Dataset):
    # @staticmethod
    # def read_bin(file_name: str):
    #     '''
    #     :param file_name: N-MNIST原始bin格式数据的文件名
    #     :return: 一个字典，键是{'t', 'x', 'y', 'p'}，值是np数组
    #
    #     原始的NavGesture提供的是bin格式数据，不能直接读取。本函数提供了一个读取的接口。
    #     '''
    #
    #     with open(file_name, 'rb') as bin_f:
    #         raw_data = np.uint64(np.fromfile(bin_f, dtype=np.uint64))
    #         x = raw_data[1::5]
    #         y = raw_data[0::5]
    #         p = (raw_data[2::5] & 128) >> 7  # bit 7
    #         t = ((raw_data[2::5] & 127) << 16) | (raw_data[3::5] << 8) | (raw_data[4::5])
    #     return {'t': t, 'x': x, 'y': y, 'p': p}

    @staticmethod
    def download_and_extract(dataset_name: str, download_root: str, extract_root=None):
        assert dataset_name == 'walk' or dataset_name == 'sit'
        file_name = os.path.basename(resource[dataset_name][0])
        # utils.download_url(url=resource[dataset_name][0], root=download_root,
        #                    filename=file_name, md5=resource[dataset_name][1])
        if extract_root is None:
            extract_root = os.path.join(download_root, 'extract')
        temp_extract_root = os.path.join(extract_root, 'temp_extract')
        utils.download_and_extract_archive(url=resource[dataset_name][0], download_root=download_root,
                                           extract_root=temp_extract_root,
                                           filename=file_name, md5=resource[dataset_name][1])
        # 解压后仍然是zip 要继续解压
        for zip_file in utils.list_files(root=temp_extract_root, suffix='.zip', prefix=True):
            print(f'extract {zip_file} to {extract_root}')
            utils.extract_archive(zip_file, extract_root)
        shutil.rmtree(temp_extract_root)
        print(f'dataset dir is {extract_root}')
        return extract_root