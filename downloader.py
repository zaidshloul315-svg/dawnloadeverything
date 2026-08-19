import yt_dlp

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'nocheckcertificate': True,
        'extract_flat': False,
        'extractor_args': {
            'youtube': {
                'client': ['tv', 'ios']
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        resolutions = set()
        for f in info.get('formats', []):
            height = f.get('height')
            if height and f.get('vcodec') != 'none':
                resolutions.add(height)
        
        res_list = sorted(list(resolutions), reverse=True)
        
        return {
            'title': info.get('title', 'Unknown Title'),
            'thumbnail': info.get('thumbnail', ''),
            'resolutions': res_list
        }

def download_media(url, format_type, quality=None, is_playlist=False):
    ydl_opts = {
        'outtmpl': '%(playlist_title)s/%(title)s.%(ext)s' if is_playlist else '%(title)s.%(ext)s',
        'yes_playlist': is_playlist,
        'noplaylist': not is_playlist,
        'ignoreerrors': True,
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'client': ['tv', 'ios']
            }
        }
    }
    
    if format_type == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        if quality:
            format_str = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best'
        else:
            format_str = 'bestvideo+bestaudio/best'
            
        ydl_opts.update({
            'format': format_str,
            'merge_output_format': 'mp4',
        })

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])