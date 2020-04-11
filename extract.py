import os
import shelve

from ffmpy3 import FFmpeg
from pydub.audio_segment import AudioSegment
from pydub.utils import mediainfo


def video2wav(file):
    input_file = file
    extension = file.split('.')[-1]
    path, filename = os.path.split(input_file)
    output_file = 'Audio/' + filename.replace(extension, 'wav')
    ff = FFmpeg(inputs={input_file: None},
                global_options=['-y'],
                outputs={output_file: '-vn -ar 16000 -ac 1 -ab 128k -f wav'})
    print(ff.cmd)
    ff.run()
    return output_file


def wav_split(file):
    main_wav_path = file
    path = os.path.dirname(file) + '/'
    sound_len = int(float(mediainfo(main_wav_path)['duration']))
    sound = AudioSegment.from_wav(main_wav_path)
    part_file_list = list()
    n = 1
    if sound_len > 60:
        n = sound_len // 60
        while n * 60 < sound_len:
            n = n + 1
    with shelve.open('DB/lines.db') as db:
        for i in range(n):
            start_time = i * 60 * 1000 + 1
            end_time = (i + 1) * 60 * 1000
            if end_time > sound_len * 1000:
                end_time = sound_len * 1000
            word = sound[start_time: end_time]
            part_file_name = '{}part_sound_{}.wav'.format(path, i)
            word.export(part_file_name, format='wav')
            part_file_list.append(part_file_name)
            record = {
                "start": start_time,
                "end": end_time,
                "lines": []
            }
            db[part_file_name] = record
    return part_file_list


def mount_sub(video, srt):
    extension = video.split('.')[-1]
    output_video = video.replace(extension, 'avi')
    ff = FFmpeg(inputs={video: None},
                global_options='-y',
                outputs={output_video: '-vf subtitles=%s' % srt})
    print(ff.cmd)
    ff.run()
    return output_video
