import os
import shelve
import textwrap

from ffmpy3 import FFmpeg


class Lines(object):
    pass


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


def translate_srt(file_name):
    # 生成srt字幕文件
    path, name = os.path.split(file_name)
    srt_file = 'Srt/' + name + '.srt'
    with shelve.open('DB/lines.db') as db:
        # 每个字典提取一行, 获取开始时间, 结束时间和行号
        record = db[file_name]
        for i, line in enumerate(record['lines']):
            words = tl.get_translation(line['words'])
            line["translation"] = words
            lines = []
        # 写回数据库
        db[file_name] = record


def gen_srt(file_name, target='en'):
    # 生成srt字幕文件
    path, name = os.path.split(file_name)
    srt_file = 'Srt/' + name + '.srt'
    with shelve.open('DB/lines.db') as db, open(srt_file, 'w+', encoding='utf-8') as srt:
        # 每个字典提取一行, 获取开始时间, 结束时间和行号
        record = db[file_name]
        for i, line in enumerate(record['lines']):
            # 每句话的开始和结束时间
            bg = line['bg'] + db[file_name]['start']
            ed = line['ed'] + db[file_name]['start']
            # 行号(可省略)
            index = str(i + 1)
            # 时间线
            timeline = time_convert(bg) + ' --> ' + time_convert(ed)

            # 翻译选项
            if target == 'cn':
                words = line['translation']
            else:
                words = line['words']

            # 组装并写入字幕文件
            lines = []
            for line in textwrap.wrap(words):
                lines.append(line + '\n')
            s = ''.join(index + '\n' + timeline + '\n' + ''.join(lines) + '\n\n')
            srt.write(s)
            print('new line generated')

    return srt_file


def merge_srts(part_srts, main_srt):
    """
    合并多个字幕分段文件到一个文件中
    :param part_srts:
    :param main_srt:
    :return:
    """
    with open(main_srt, 'w', encoding='utf-8') as full:
        for file in part_srts:
            with open(file, 'r', encoding='utf-8') as part:
                data = part.read()
                full.write(data)


def mount_sub(video, srt):
    """
    (deprecated 字幕直接串流到视频中)
    :param video:
    :param srt:
    :return:
    """
    extension = video.split('.')[-1]
    output_video = video.replace(extension, 'mkv')
    ff = FFmpeg(inputs={video: None, srt: None},
                global_options='-y',
                outputs={output_video: None})
    print(ff.cmd)
    ff.run()
    return output_video
