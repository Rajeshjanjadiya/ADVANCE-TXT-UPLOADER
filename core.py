# Don't Remove Credit Tg - @newstudent1885

import os
import time
import datetime
import aiohttp
import aiofiles
import asyncio
import logging
import requests
import tgcrypto
import subprocess
import concurrent.futures

from utils import progress_bar

from pyrogram import Client, filters
from pyrogram.types import Message

from pytube import Playlist  #Youtube Playlist Extractor
from yt_dlp import YoutubeDL
import yt_dlp as youtube_dl

def duration(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)
    
def exec(cmd):
        process = subprocess.run(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output = process.stdout.decode()
        print(output)
        return output
        #err = process.stdout.decode()
def pull_run(work, cmds):
    with concurrent.futures.ThreadPoolExecutor(max_workers=work) as executor:
        print("Waiting for tasks to complete")
        fut = executor.map(exec,cmds)
async def aio(url,name):
    k = f'{name}.pdf'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(k, mode='wb')
                await f.write(await resp.read())
                await f.close()
    return k


async def download(url,name):
    ka = f'{name}.pdf'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(ka, mode='wb')
                await f.write(await resp.read())
                await f.close()
    return ka



def parse_vid_info(info):
    info = info.strip()
    info = info.split("\n")
    new_info = []
    temp = []
    for i in info:
        i = str(i)
        if "[" not in i and '---' not in i:
            while "  " in i:
                i = i.replace("  ", " ")
            i.strip()
            i = i.split("|")[0].split(" ",2)
            try:
                if "RESOLUTION" not in i[2] and i[2] not in temp and "audio" not in i[2]:
                    temp.append(i[2])
                    new_info.append((i[0], i[2]))
            except:
                pass
    return new_info


def vid_info(info):
    info = info.strip()
    info = info.split("\n")
    new_info = dict()
    temp = []
    for i in info:
        i = str(i)
        if "[" not in i and '---' not in i:
            while "  " in i:
                i = i.replace("  ", " ")
            i.strip()
            i = i.split("|")[0].split(" ",3)
            try:
                if "RESOLUTION" not in i[2] and i[2] not in temp and "audio" not in i[2]:
                    temp.append(i[2])
                    
                    # temp.update(f'{i[2]}')
                    # new_info.append((i[2], i[0]))
                    #  mp4,mkv etc ==== f"({i[1]})" 
                    
                    new_info.update({f'{i[2]}':f'{i[0]}'})

            except:
                pass
    return new_info



async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')
    if proc.returncode == 1:
        return False
    if stdout:
        return f'[stdout]\n{stdout.decode()}'
    if stderr:
        return f'[stderr]\n{stderr.decode()}'

    

def old_download(url, file_name, chunk_size = 1024 * 10):
    if os.path.exists(file_name):
        os.remove(file_name)
    r = requests.get(url, allow_redirects=True, stream=True)
    with open(file_name, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                fd.write(chunk)
    return file_name


def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"


def time_name():
    date = datetime.date.today()
    now = datetime.datetime.now()
    current_time = now.strftime("%H%M%S")
    return f"{date} {current_time}.mp4"

def get_playlist_videos(playlist_url):
    try:
        # Create a Playlist object
        playlist = Playlist(playlist_url)
        
        # Get the playlist title
        playlist_title = playlist.title
        
        # Initialize an empty dictionary to store video names and links
        videos = {}
        
        # Iterate through the videos in the playlist
        for video in playlist.videos:
            try:
                video_title = video.title
                video_url = video.watch_url
                videos[video_title] = video_url
            except Exception as e:
                logging.error(f"Could not retrieve video details: {e}")
        
        return playlist_title, videos
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None, None
        
def get_all_videos(channel_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True
    }

    all_videos = []
    with YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(channel_url, download=False)
        
        if 'entries' in result:
            channel_name = result['title']
            all_videos.extend(result['entries'])
            
            while 'entries' in result and '_next' in result:
                next_page_url = result['_next']
                result = ydl.extract_info(next_page_url, download=False)
                all_videos.extend(result['entries'])
            
            video_links = {index+1: (video['title'], video['url']) for index, video in enumerate(all_videos)}
            return video_links, channel_name
        else:
            return None, None

def save_to_file(video_links, channel_name):
    # Sanitize the channel name to be a valid filename
    sanitized_channel_name = re.sub(r'[^\w\s-]', '', channel_name).strip().replace(' ', '_')
    filename = f"{sanitized_channel_name}.txt"    
    with open(filename, 'w', encoding='utf-8') as file:
        for number, (title, url) in video_links.items():
            # Ensure the URL is formatted correctly
            if url.startswith("https://"):
                formatted_url = url
            elif "shorts" in url:
                formatted_url = f"https://www.youtube.com{url}"
            else:
                formatted_url = f"https://www.youtube.com/watch?v={url}"
            file.write(f"{number}. {title}: {formatted_url}\n")
    return filename



async def download_video(url, cmd, name):
    import glob
    import json

    base = os.path.splitext(name)[0]
    extensions = (".mp4", ".mkv", ".webm", ".m4v", ".mov")

    def valid_video(filename):
        if not os.path.isfile(filename) or os.path.getsize(filename) == 0:
            return False

        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "stream=codec_type",
                "-show_entries", "format=duration",
                "-of", "json", filename
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return False

        try:
            data = json.loads(result.stdout)
            streams = data.get("streams", [])
            duration = float(data.get("format", {}).get("duration", 0))
            return duration > 0 and any(
                stream.get("codec_type") == "video"
                for stream in streams
            )
        except (ValueError, TypeError, json.JSONDecodeError):
            return False

    candidates = list(dict.fromkeys(
        [name] +
        [base + ext for ext in extensions] +
        glob.glob(base + ".*")
    ))

    candidates = [
        f for f in candidates
        if os.path.splitext(f)[1].lower() in extensions
    ]

    for attempt in range(1, 4):
        old_state = {}

        for filename in candidates:
            if os.path.isfile(filename):
                stat = os.stat(filename)
                old_state[filename] = (stat.st_mtime_ns, stat.st_size)

        download_cmd = (
            f'{cmd} --retries 5 '
            f'--fragment-retries 10 '
            f'--retry-sleep 3'
        )

        logging.info("Download attempt %s: %s", attempt, download_cmd)
        print(f"Download attempt {attempt}/3")

        result = await asyncio.to_thread(
            subprocess.run,
            download_cmd,
            shell=True,
            check=False
        )

        for filename in candidates:
            if not os.path.isfile(filename):
                continue

            stat = os.stat(filename)
            current_state = (stat.st_mtime_ns, stat.st_size)

            if current_state == old_state.get(filename):
                continue

            if await asyncio.to_thread(valid_video, filename):
                logging.info("Verified video: %s", filename)
                return filename

        if attempt < 3:
            print(f"Download failed. Retry {attempt}/3")
            await asyncio.sleep(5)

    raise RuntimeError(
        f"Download failed or video verification failed after 3 attempts. "
        f"Exit code: {result.returncode}"
    )

async def send_doc(bot: Client, m: Message,cc,ka,cc1,prog,count,name):
    reply = await m.reply_text(f"🚀🚀🚀𝗨𝗣𝗟𝗢𝗔𝗗𝗜𝗡𝗚🚀🚀🚀 » `{name}`\n\n🤖𝗕𝗢𝗧 𝗠𝗔𝗗𝗘 𝗕𝗬 ➤ 𝗧𝗨𝗦𝗛𝗔𝗥")
    time.sleep(1)
    start_time = time.time()
    await m.reply_document(ka,caption=cc1)
    count+=1
    await reply.delete (True)
    time.sleep(1)
    os.remove(ka)
    time.sleep(3) 


async def send_vid(bot: Client, m: Message,cc,filename,thumb,name,prog):
    
    subprocess.run(f'ffmpeg -i "{filename}" -ss 00:00:12 -vframes 1 "{filename}.jpg"', shell=True)
    await prog.delete (True)
    reply = await m.reply_text(f"**🚀🚀🚀𝗨𝗣𝗟𝗢𝗔𝗗𝗜𝗡𝗚🚀🚀🚀** » `{name}`\n\n🤖𝗕𝗢𝗧 𝗠𝗔𝗗𝗘 𝗕𝗬 ➤ 𝗧𝗨𝗦𝗛𝗔𝗥")
    try:
        if thumb == "no":
            thumbnail = f"{filename}.jpg"
        else:
            thumbnail = thumb
    except Exception as e:
        await m.reply_text(str(e))

    dur = int(duration(filename))

    start_time = time.time()

    try:
        await m.reply_video(filename,caption=cc, supports_streaming=True,height=720,width=1280,thumb=thumbnail,duration=dur, progress=progress_bar,progress_args=(reply,start_time))
    except Exception:
        await m.reply_document(filename,caption=cc, progress=progress_bar,progress_args=(reply,start_time))

    
    os.remove(filename)

    os.remove(f"{filename}.jpg")
    await reply.delete (True)
    
