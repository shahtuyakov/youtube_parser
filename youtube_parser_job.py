import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_youtube_service(api_key):
    try:
        return build('youtube', 'v3', developerKey=api_key)
    except HttpError as e:
        logging.error(f"An error occurred: {e}")
        raise

def get_channel_id(youtube, channel_name):
    try:
        request = youtube.search().list(
            part='snippet',
            q=channel_name,
            type='channel',
            maxResults=1
        )
        response = request.execute()
        return response['items'][0]['id']['channelId']
    except (KeyError, IndexError):
        logging.error("Channel not found or invalid response from YouTube API.")
        return None
    except HttpError as e:
        logging.error(f"An error occurred: {e}")
        return None

def get_video_statistics(youtube, video_id):
    try:
        request = youtube.videos().list(
            part='statistics',
            id=video_id
        )
        response = request.execute()
        stats = response['items'][0]['statistics']
        return {
            'View Count': stats.get('viewCount', 0),
            'Like Count': stats.get('likeCount', 0),
            'Comment Count': stats.get('commentCount', 0)
        }
    except HttpError as e:
        logging.error(f"An error occurred while fetching video statistics: {e}")
        return {
            'View Count': 0,
            'Like Count': 0,
            'Comment Count': 0
        }

def get_channel_videos(youtube, channel_id):
    videos = []
    next_page_token = None
    while True:
        try:
            request = youtube.search().list(
                part='snippet',
                channelId=channel_id,
                maxResults=50,
                pageToken=next_page_token,
                type='video'
            )
            response = request.execute()
            for item in response['items']:
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                link = f'https://www.youtube.com/watch?v={video_id}'
                description = item['snippet'].get('description', 'No description available')
                thumbnail_url = item['snippet']['thumbnails']['high']['url']
                stats = get_video_statistics(youtube, video_id)
                video_data = {
                    'Title': title,
                    'Link': link,
                    'Description': description,
                    'Thumbnail': thumbnail_url,
                    'View Count': stats['View Count'],
                    'Like Count': stats['Like Count'],
                    'Comment Count': stats['Comment Count']
                }
                videos.append(video_data)
            next_page_token = response.get('nextPageToken')
            if next_page_token is None:
                break
        except HttpError as e:
            logging.error(f"An error occurred: {e}")
            break
    return videos

def save_to_excel(videos, output_file):
    df = pd.DataFrame(videos)
    df.to_excel(output_file, index=False)

def main():
    api_key = 'AIzaSyD1o2Ec9A-34ncynQg4UA_hNI9mdAWamkA'  # Replace with your API key
    channel_name = input("Enter the YouTube channel name: ").strip()
    if not channel_name:
        logging.error("You must enter a channel name.")
        return

    output_file = input("Enter the output Excel file name (with .xlsx extension): ").strip()
    if not output_file.endswith('.xlsx'):
        logging.error("Invalid file name. The output file must have a .xlsx extension.")
        return

    youtube = get_youtube_service(api_key)
    channel_id = get_channel_id(youtube, channel_name)
    if channel_id:
        logging.info("Fetching videos...")
        videos = get_channel_videos(youtube, channel_id)
        if videos:
            save_to_excel(videos, output_file)
            logging.info(f"Excel file '{output_file}' created successfully with {len(videos)} videos.")
        else:
            logging.info("No videos found for the specified channel.")
    else:
        logging.error("Could not retrieve channel ID.")

if __name__ == '__main__':
    main()