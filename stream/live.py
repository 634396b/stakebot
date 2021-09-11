from loop_audio import get_audio
import asyncio
import sys
from traceback import print_exc


def format_txt(txt):
    filters = [
        f"drawtext=fontfile=stream/um.ttf:fontsize=18:fontcolor=white:x=0:y=0:expansion=none:reload=1:fix_bounds=true:textfile='{txt}'",
        f"drawtext=fontfile=stream/um.ttf:fontsize=12:fontcolor=white:x=(w):y=(h*0.16):expansion=none:reload=1:fix_bounds=true:textfile='logs/data/big-wins.txt'",
        f"drawtext=fontfile=stream/um.ttf:fontsize=18:fontcolor=white:x=(w):y=0:expansion=none:reload=1:fix_bounds=true:textfile='stream/message.txt'",
        # f"drawtext=fontfile=stream/um.ttf:fontsize=12:fontcolor=white:x=(w*0.5):y=(h-th):expansion=none:reload=1:textfile='logs/data/chat.txt'",
        # f"drawtext=fontfile=stream/um.ttf:fontsize=18:fontcolor=white:x=(w - tw - 25):y=(h - th):expansion=none:reload=1:fix_bounds=true:textfile='stream/song.txt'",
        # f'scale=-1:1080',
        # f'yadif',
    ]
    filters_str = ','.join(filters)
    return f"[in]{filters_str}[out]"


proc = None


async def stream():
    global proc
    sk = 'rtmp://yto.contribute.live-video.net/app/{stream-key}'
    live = f"""ffmpeg -fflags +igndts+nobuffer -flags low_delay -max_error_rate 1.0 -report -progress progress.log \
            -stream_loop -1 -re -i pipe:0\
            -stream_loop -1 -f lavfi -i color=c=black:s=1920x1080 -vf "{format_txt("logs/data/Wiggle.txt")}"\
            -r 25 -g 60 -tune zerolatency -preset veryfast -vcodec libx264 -acodec aac -b:v 4000k -ac 2 -f flv {sk}"""
    while True:
        try:
            proc = await asyncio.create_subprocess_shell(live, stdin=asyncio.subprocess.PIPE,
                                                         stdout=sys.stdout,
                                                         stderr=sys.stderr)
            await proc.wait()
        except:
            print_exc()


async def do_audio():
    while True:
        try:
            a_file_name, duration = get_audio()
            p_audio = await asyncio.create_subprocess_exec(*["ffmpeg", "-i", a_file_name, '-af', 'adelay=15000|15000', '-map_metadata', '-1',
                                                             "-q:a", "0", "-map", "0:a", "-ac", "2", "-f", "mp3", "pipe:"], stdout=asyncio.subprocess.PIPE, stderr=sys.stdout)
            audio, _ = await p_audio.communicate()
            proc.stdin.write(audio)
            duration = duration - 10
            duration = max(duration, 30)
            duration = min(duration, 500)
            print(a_file_name, duration)
            await asyncio.sleep(duration)
        except:
            print_exc()
            await asyncio.sleep(30)

if __name__ == '__main__':
    asyncio.get_event_loop().create_task(stream())
    asyncio.get_event_loop().create_task(do_audio())
    asyncio.get_event_loop().run_forever()
