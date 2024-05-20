import pandas as pd
import yt_dlp
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_video_urls_from_excel(file_path):
    df = pd.read_excel(file_path)
    return df['Link'].dropna().tolist()

def list_subtitles(video_url):
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'listsubtitles': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        return info_dict.get('subtitles', {}), info_dict.get('automatic_captions', {})

def download_subtitles(video_url, output_path, languages, auto_captions=False):
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'subtitleslangs': languages,
        'subtitlesformat': 'vtt',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
    }

    if auto_captions:
        ydl_opts['writeautomaticsub'] = True

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def main():
    # Ask for the path of the Excel file to process
    excel_file = input("Enter the path of the Excel file to process: ").strip()
    if not os.path.isfile(excel_file):
        logging.error(f"The file '{excel_file}' does not exist.")
        return
    
    script_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Get video URLs from the Excel file
    video_urls = get_video_urls_from_excel(excel_file)
    
    # Directory to save subtitles
    output_path = os.path.join(script_dir, 'youtube_subs')
    os.makedirs(output_path, exist_ok=True)

    # Download subtitles for each video URL
    for video_url in video_urls:
        try:
            logging.info(f"Listing subtitles for {video_url}")
            subtitles, auto_captions = list_subtitles(video_url)
            if subtitles:
                languages = list(subtitles.keys())
                logging.info(f"Available subtitles languages for {video_url}: {languages}")
                logging.info(f"Downloading subtitles for {video_url}")
                download_subtitles(video_url, output_path, languages)
            elif 'en' in auto_captions:
                logging.info(f"No manual subtitles available for {video_url}. Downloading automatic captions in English.")
                download_subtitles(video_url, output_path, ['en'], auto_captions=True)
            else:
                logging.info(f"No subtitles available for {video_url}")
        except Exception as e:
            logging.error(f"Error processing {video_url}: {e}")

if __name__ == '__main__':
    main()