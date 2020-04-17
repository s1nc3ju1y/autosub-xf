import os
import shelve
import subprocess


def text2speech(text, wav_name, speed=60, volume=70, pitch=50):
    # command_line = f"/home/chris/projects/PycharmProjects/Auto_dub/Tts/xtts " \
    #                f"-t {text} -s {speed} -v {volume} -p {pitch} -o {wav_name}"
    # print(command_line)
    args = ["./xtts",
            "-t", text,
            "-s", str(speed),
            "-v", str(volume),
            "-p", str(pitch),
            "-o", wav_name]
    ret = subprocess.Popen(args,
                           cwd="Tts",
                           stdout=subprocess.PIPE)
    for lines in ret.stdout.readlines():
        print(lines.decode('utf-8'))


def line2speech(line):
    pass


def tts(wav_file):
    audios = []
    with shelve.open("DB/lines.db") as db:
        record = db[wav_file]
        start_time = record["start"]
        for i, line in enumerate(record['lines']):
            offset = line["bg"]
            output = f"/home/chris/projects/PycharmProjects/Auto_dub/Audio/{start_time + offset}.wav"
            if line["translation"]:
                # text2speech(line["translation"], output)
                audios.append(output)

    return audios


def dub(video, audios):
    """
    视频配音实现
    :param video: 要进行配音的视频文件
    :param audios: 输入的音频片段
    :return:
    """

    cmd = ["ffmpeg -y -i " + video]
    cmd2 = [" -filter_complex \""]
    cmd3 = [""]

    for i, audio in enumerate(audios):
        cmd.append(" -i " + audio)
        # 提取文件名, 文件名即为时间信息
        path, file_name = os.path.split(audio)
        time_out = int(file_name.split('.')[0])
        cmd2.append("[" + str(i + 1) + "]adelay=" + str(time_out) + "|" + str(time_out) + "[aud" + str(i + 1) + "];")
        cmd3.append("[aud" + str(i + 1) + "]")

    cmd3.append("amix=inputs=" + str(len(audios)) + ":dropout_transition=1000,volume=13,dynaudnorm[a]" + "\"")
    cmd2.append("".join(cmd3))
    cmd.append("".join(cmd2))

    output = "Video/dub.mp4"
    cmd.append(" -map 0:v -map \"[a]\"")
    cmd.append(" -c:v copy " + output)
    ret = subprocess.Popen("".join(cmd),
                           shell=True,
                           stdout=subprocess.PIPE)
    for line in ret.stdout.readlines():
        print(line.decode('utf-8'))
    # print("".join(cmd))

# with shelve.open("DB/lines.db") as db:
#     print(db[f"Audio/part_sound_1.wav"]["lines"])

# audios = []
# for i in range(1, 2):
#     audios = tts(f"Audio/part_sound_{i}.wav")
#     # print(audios)
#
# dub("Video/Ted.mp4", audios)
