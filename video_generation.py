import requests
from dotenv import load_dotenv
import os
import time
import re
import json
from moviepy.editor import VideoFileClip, concatenate_videoclips


# .envファイルをロード
load_dotenv()

# 動画ディレクトリの設定
video_dir = "videos"

endpoint = os.environ['AZURE_OPENAI_ENDPOINT']
api_key = os.environ['AZURE_OPENAI_API_KEY']

with open('./video_prompt.json', 'r', encoding='utf-8') as f:
    prompt = json.load(f)

def create_video(prompt, video_dir):
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)

    # 1. Create a video generation job
    print("Creating video generation job...")
    max_retries = 3

    api_version = 'preview'
    headers= { "api-key": api_key, "Content-Type": "application/json" }
    create_url = f"{endpoint}/openai/v1/video/generations/jobs?api-version={api_version}"
    for i in range(len(prompt)):
        for attempt in range(1, max_retries + 1):
            print(f"\n--- Video {i+1}/{len(prompt)}: Attempt {attempt} ---")
            body = {
                "prompt": f"""{prompt[i]}""",
                "width": "720p",
                "height": "720p",
                "n_seconds": 5,
                "model": "sora"
            }

            try:
                response = requests.post(create_url, headers=headers, json=body)
                response.raise_for_status()
                print("Full response JSON:", response.json())
                job_id = response.json()["id"]
                print(f"Job created: {job_id}")

                # 2. Poll for job status
                status_url = f"{endpoint}/openai/v1/video/generations/jobs/{job_id}?api-version={api_version}"
                status=None
                while status not in ("succeeded", "failed", "cancelled"):
                    time.sleep(5)  # Wait before polling again
                    status_response = requests.get(status_url, headers=headers).json()
                    status = status_response.get("status")
                    print(f"Job status: {status}")

                # 3. Retrieve generated video 
                if status == "succeeded":
                    generations = status_response.get("generations", [])
                    if generations:
                        print(f"✅ Video generation succeeded.")
                        generation_id = generations[0].get("id")
                        video_url = f"{endpoint}/openai/v1/video/generations/{generation_id}/content/video?api-version={api_version}"
                        video_response = requests.get(video_url, headers=headers)
                        if video_response.ok:
                            output_filename = f"{video_dir}/output{i}.mp4"
                            with open(output_filename, "wb") as file:
                                file.write(video_response.content)
                                print(f'Generated video saved as "{output_filename}"')
                        else:
                            print("Failed to download video content.")
                        break  # 成功したのでリトライ終了
                    else:
                        print("No generations found in job result.")
                        # 失敗としてリトライ
                else:
                    print(f"Job didn't succeed. Status: {status}")
                    if attempt == max_retries:
                        raise Exception(f"Job failed after {max_retries} attempts. Status: {status}")
                    else:
                        print("Retrying...")
                        continue
                break  # 成功したのでリトライ終了
            except Exception as e:
                print(f"Error: {e}")
                if attempt == max_retries:
                    raise
                else:
                    print("Retrying...")
                    time.sleep(3)
    
def merge_videos(video_dir):
    video_files = sorted([f for f in os.listdir(video_dir) if re.match(r"output\d+\.mp4$", f)])

    print(video_files)

    clips = []
    for file in video_files:
        filepath = f"{video_dir}/{file}"
        clip = VideoFileClip(filepath)
        clips.append(clip)

    # 動画を結合
    final_clip = concatenate_videoclips(clips, method="compose")

    # 出力ファイル名
    final_clip.write_videofile("merged_output.mp4", codec="libx264", audio_codec="aac")

    # リソース解放
    for clip in clips:
        clip.close()
    final_clip.close()

def main():
    create_video(prompt, video_dir)
    merge_videos(video_dir)

# 実行部分
if __name__ == "__main__":
    main()