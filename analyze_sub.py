import os
import re
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_vtt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        vtt_content = file.readlines()

    cleaned_lines = []
    for line in vtt_content:
        # Remove metadata and styling tags
        if line.startswith('WEBVTT') or line.startswith('NOTE') or line.strip() == '':
            continue
        # Remove styling tags within the text
        cleaned_line = re.sub(r'<[^>]+>', '', line)
        cleaned_lines.append(cleaned_line)

    cleaned_content = ''.join(cleaned_lines)
    return cleaned_content

def parse_and_remove_duplicates(cleaned_content):
    pattern = re.compile(r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\s(.*?)\s(?=\d{2}:\d{2}:\d{2}\.\d{3}|\Z)', re.DOTALL)
    matches = pattern.findall(cleaned_content)
    
    subtitles = {}
    for match in matches:
        start_time, end_time, text = match
        text = re.sub(r'align:start position:0%', '', text).strip()
        if start_time in subtitles:
            if text not in subtitles[start_time]['text']:
                subtitles[start_time]['text'] += ' ' + text
        else:
            subtitles[start_time] = {'end_time': end_time, 'text': text}

    return subtitles

def parse_vtt(subtitles):
    parsed_subtitles = []
    seen_texts = set()  # To keep track of seen texts and remove duplicates
    for start_time, data in subtitles.items():
        text = data['text']
        if text and text not in seen_texts:  # Check if text is not empty and not seen before
            seen_texts.add(text)
            parsed_subtitles.append({'start_time': start_time, 'end_time': data['end_time'], 'text': text})
    return parsed_subtitles


def find_hook(subtitles):
    hook = []
    for subtitle in subtitles:
            hook.append(subtitle['text'])
    return ' '.join(hook)

def save_hook(hook_text, video_title, output_folder):
    hook_filename = f"{video_title}.txt"
    hook_filepath = os.path.join(output_folder, hook_filename)
    with open(hook_filepath, 'w', encoding='utf-8') as file:
        file.write(hook_text)
    logging.info(f"Hook saved to {hook_filepath}")

def analyze_subtitles(subtitles_folder, hooks_folder):
    if not os.path.exists(subtitles_folder):
        logging.error(f"Subtitles folder '{subtitles_folder}' does not exist.")
        return
    
    if not os.path.exists(hooks_folder):
        os.makedirs(hooks_folder)
    
    for root, dirs, files in os.walk(subtitles_folder):
        for file in files:
            if file.endswith('.vtt'):
                file_path = os.path.join(root, file)
                try:
                    cleaned_content = clean_vtt(file_path)

                    subtitles = parse_and_remove_duplicates(cleaned_content)
                    
                    parsed_subtitles = parse_vtt(subtitles)
                    if not parsed_subtitles:
                        logging.warning(f"No subtitles found in {file_path}")
                        continue
                    
                    hook = find_hook(parsed_subtitles)
                    if not hook:
                        logging.warning(f"No hook found in {file_path}")
                        continue
                    
                    video_title = os.path.splitext(file)[0]
                    save_hook(hook, video_title, hooks_folder)
                except Exception as e:
                    logging.error(f"Error parsing {file_path}: {e}")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.realpath(__file__))
    subtitles_folder = os.path.join(script_dir, 'youtube_subs')
    hooks_folder = os.path.join(script_dir, 'hooks')
    analyze_subtitles(subtitles_folder, hooks_folder)