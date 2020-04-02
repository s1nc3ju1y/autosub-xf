import argparse

from dictation import APIParam, DictationAPP
from extract import video2wav, wav_split, mount_sub
from srt import gen_srt, merge_srts

if __name__ == '__main__':
    # 配置参数解析
    # usage -i input -d diction, -t translation -s subtitle -m merge -0 output
    parser = argparse.ArgumentParser(description="Auto generate subtitle and translate it")
    parser.add_argument('-i', help='input a video file', default='Video/Ted.mp4')
    parser.add_argument('-o', help='video output')
    parser.add_argument('-d', help='dictation', action='store_true', default=False)
    parser.add_argument('-t', help='translation', action='store_true', default=False)
    parser.add_argument('-s', help='subtitle', action='store_true', default=False)
    parser.add_argument('-m', help='merge', action='store_true', default=False)
    parser.add_argument('--debug', action='store_true', default=False)

    # 生成解析参数
    args = parser.parse_args()

    # 获取输入/输出文件名
    input_video = args.i if args.i else ''
    output_video = args.o if args.o else ''

    # 预处理
    # 提取完整音频并切分成60s的片段
    if args.d:
        video = args.i
        wav = video2wav(video)
        parts = wav_split(wav)
        num_of_parts = len(parts)
        audios = [f'Audio/part_sound_{i}.wav' for i in range(num_of_parts)]

        # 语音识别
        # 识别结果保存到本地数据库
        for i in range(num_of_parts):
            wp = APIParam(APPID='5e2952b0', APIKey='414ea9ed44eda8363fbc10a5d6483ebc',
                          APISecret='9b7d258ee7d3bfbb014e0d2aa956652c',
                          AudioFile=audios[i])
            app = DictationAPP(wp)
            app.start()

    if args.s:
        # 制作分段字幕
        audios = [f'Audio/part_sound_{i}.wav' for i in range(15)]
        srts = []
        for audio in audios:
            srt_file = gen_srt(audio, 'cn') if args.t else gen_srt(audio, 'en')
            srts.append(srt_file)
        # 合并分段字幕
        merge_srts(srts)

    # 合并字幕与视频
    if args.m:
        mount_sub(args.i, 'Video/main.srt')
