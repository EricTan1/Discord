import youtube_dl

import asyncio

class MusicPlayer:
    def __init__(self, bot):
        self.bot = bot
    async def play_music(self, source, text_channel, voice_channel):
        if(text_channel.guild.voice_client == None or not text_channel.guild.voice_client.is_connected()):
            print("not connected")
            await voice_channel.connect()
        text_channel.guild.voice_client.play(source)
            

    async def stop_music(self, channel):
        channel.guild.voice_client.stop()

    def download(self, title, video_url):
        outtmpl = '{}.%(ext)s'.format(title)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': outtmpl,
            'noplaylist': True,
            'default_search': 'auto',
            'restrictfilenames': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'source_address': '0.0.0.0',
            'no_warnings': True,
            'postprocessors': [
                {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3',
                 'preferredquality': '192',
                 },
                {'key': 'FFmpegMetadata'},
            ],

        }
        # check if its a video or a search and get the temp
        # streaming URL accordingly
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(video_url, download=False)
            print(data)
            if(data.get('_type') != None):
                if(data.get('entries') != None):
                    data = data.get('entries').pop(0)
                    # ydl.download([new_video_url])
                else:
                    print("ERROR NO ATTRIBUTE ENTRIES")
            url_list = data.get('formats')
            data = url_list.pop(len(url_list) - 1)
            data = data.get('url')
        # return '{}.mp3'.format(title)
        return data
