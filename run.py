from dictation import APIParam, DictationAPP
from extract import video2wav, wav_split, mount_sub
from srt import gen_srt, merge_srts

stored = True
subtitle = True
# 预处理
# 提取完整音频并切分成60s的片段
if not stored:
    video = 'Video/Ted.mp4'
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

if not subtitle:
    # 制作分段字幕
    audios = [f'Audio/part_sound_{i}.wav' for i in range(15)]
    srts = []
    for audio in audios:
        srt_file = gen_srt(audio, 'cn')
        srts.append(srt_file)
    # 合并分段字幕
    merge_srts(srts)

# 合并字幕与视频
mount_sub('Video/Ted.mp4', 'Video/main.srt')
