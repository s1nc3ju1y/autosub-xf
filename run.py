import argparse

from dictation import APIParam, DictationAPP
from dub import tts, dub
from extract import prepare
from srt import gen_srt, merge_srts

if __name__ == '__main__':
    # 配置参数解析
    # usage -i input -d diction, -t translation -s subtitle -m merge -0 output
    parser = argparse.ArgumentParser(description="Auto generate subtitle and translate it")
    # 配置输入文件
    parser.add_argument('-i', help='input a video file', default='Video/Ted.mp4')
    # 配置输出文件
    parser.add_argument('-o', help='video output', default='Video/Ted.Auto_dub.mp4')
    # 开启配音功能
    parser.add_argument('-d', help='dub', action='store_true', default=False)
    # 开启翻译功能
    parser.add_argument('-t', help='translation', action='store_true', default=False)
    # 开启字幕功能
    parser.add_argument('-s', help='subtitle', action='store_true', default=False)
    # 配置是否使用缓存
    parser.add_argument('--cache', action='store_true', default=False)

    # 生成解析参数
    args = parser.parse_args()

    # 获取输入/输出文件名
    input_video = args.i if args.i else ''
    output_video = args.o if args.o else ''

    # 预处理
    audios = prepare(input_video)
    num_of_parts = len(audios)

    # 根据cache参数决定是否进行网络请求
    # 若使用cache, 则直接使用本地数据库的数据, 否则, 先进行一次网络请求获取数据
    if not args.cache:
        for audio in audios:
            wp = APIParam(APPID='5e2952b0', APIKey='414ea9ed44eda8363fbc10a5d6483ebc',
                          APISecret='9b7d258ee7d3bfbb014e0d2aa956652c',
                          AudioFile=audio)
            app = DictationAPP(wp)
            app.start()

    # 开启字幕功能
    if args.s:
        # 制作分段字幕
        audios = [f'Audio/part_sound_{i}.wav' for i in range(num_of_parts)]
        srts = []
        for audio in audios:
            # 根据翻译选项, 生成英文或中文字幕
            srt_file = gen_srt(audio, 'cn') if args.t else gen_srt(audio, 'en')
            srts.append(srt_file)

        # 合并分段字幕
        if args.t:
            merge_srts(srts, 'Video/main.cn.srt')
        else:
            merge_srts(srts, 'Video/main.srt')

    # 开启配音功能
    if args.d:
        speech_parts = []

        # 对于每个输入的音轨片段, 将其中的对话文字转为speech_part, 再按照时间信息输入到视频的特定位置
        for audio in audios:
            for part in tts(audio):
                speech_parts.append(part)
        print(speech_parts)
        dub(input_video, speech_parts)
