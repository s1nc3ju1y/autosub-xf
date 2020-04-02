import os
import shelve
import textwrap

from translate import Translator


def time_convert(m):
    """
    将offset转化为 hh:mm:ss,ms 格式
    :param m:
    :return:
    """
    hh, mm, ss, ms = 0, 0, 0, m
    ss, ms = divmod(ms, 1000)
    mm, ss = divmod(ss, 60)
    hh, mm = divmod(mm, 60)
    return '%02d:%02d:%02d,%d' % (hh, mm, ss, ms)


def gen_srt(file_name, target):
    tl = Translator("itrans.xfyun.cn")
    # 生成srt字幕文件
    path, name = os.path.split(file_name)
    srt_file = 'Srt/' + name + '.srt'
    with shelve.open('DB/lines.db') as db, open(srt_file, 'w+', encoding='utf-8') as srt:
        # 每个字典提取一行, 获取开始时间, 结束时间和行号
        for i, record in enumerate(db[file_name]['lines']):
            # 写行号
            bg = record['bg'] + db[file_name]['start']
            ed = record['ed'] + db[file_name]['start']
            index = str(i + 1)
            timeline = time_convert(bg) + ' --> ' + time_convert(ed)
            words = record['words']
            if target == 'cn':
                words = tl.get_translation(words)
            lines = []
            for line in textwrap.wrap(words):
                lines.append(line + '\n')
            s = ''.join(index + '\n' + timeline + '\n' + ''.join(lines) + '\n\n')
            srt.write(s)
    return srt_file


def merge_srts(filenames):
    """
    合并多个字幕分段文件到一个文件中
    :param filenames:
    :return:
    """
    with open('Video/main.srt', 'w', encoding='utf-8') as full:
        for file in filenames:
            with open(file, 'r', encoding='utf-8') as part:
                data = part.read()
                full.write(data)
