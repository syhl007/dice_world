import re

import os


def xml_file_check(file_path):
    if file_path and os.path.exists(file_path):
        with open(file_path, 'r+', encoding='utf-8') as f:
            texts = [re.sub(u"[&\x00-\x08\x0b-\x0c\x0e-\x1f]", u" ", text) for text in f.readlines()]
            # 读写偏移位置移到最开始处
            f.seek(0, 0)
            f.writelines(texts)
