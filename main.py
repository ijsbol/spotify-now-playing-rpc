import datetime
from os import getenv
from typing import Final
from requests import get
import time

from dotenv import load_dotenv
from pypresence import Presence, ActivityType


load_dotenv()


DISCORD_CLIENT_ID: Final[str] = str(getenv("DISCORD_CLIENT_ID"))
SPOTIFY_NOW_PLAYING_API_URL: Final[str] = str(getenv("SPOTIFY_NOW_PLAYING_API_URL"))


rpc = Presence(DISCORD_CLIENT_ID)
rpc.connect()


def format_ms(ms: int) -> str:
    total_seconds = ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    mm_ss = f"{minutes:02}:{seconds:02}"
    return mm_ss


def create_progress_bar(percentage: int) -> str:
    percentage = max(0, min(percentage, 100))
    total_segments = 30
    completed_segments = round((percentage / 100) * total_segments)
    progress_bar = '▰' * completed_segments + '▱' * (total_segments - completed_segments)
    return progress_bar


def str_numbers_to_emojis(text: str) -> str:
    emoji_table = {
        "1": "𝟷",#0𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿
        "2": "𝟸",
        "3": "𝟹",
        "4": "𝟺",
        "5": "𝟻",
        "6": "𝟼",
        "7": "𝟽",
        "8": "𝟾",
        "9": "𝟿",
        "0": "0️",
    }
    for k, v in emoji_table.items():
        text = text.replace(k, v)
    return text


def main() -> None:
    try:
        while True:
            try:
                spotify_data = get(SPOTIFY_NOW_PLAYING_API_URL).json()
            except Exception:
                continue
            if spotify_data.get("status", None) is not None:
                continue
            lyrics_now = spotify_data["current_lyric"]
            song_name = spotify_data["song_data"]["item"]["name"]
            artist_names = ', '.join(a["name"] for a in spotify_data["song_data"]["item"]["artists"])
            progress_ms = spotify_data["song_data"]["progress_ms"]
            duration_ms = spotify_data["song_data"]["item"]["duration_ms"]
            album_image_url = spotify_data["song_data"]["item"]["album"]["images"][0]["url"]
            start_time = format_ms(progress_ms)
            end_time = format_ms(duration_ms)
            progress_bar = create_progress_bar(int((progress_ms / duration_ms)*100))
            rpc.update(
                activity_type=ActivityType.LISTENING,
                state=f"{str_numbers_to_emojis(start_time)} {progress_bar} {str_numbers_to_emojis(end_time)}",
                details=f"{song_name} by {artist_names}",
                large_image=album_image_url,
                large_text=f"🎵 {lyrics_now}",
            )
            print(f"Updated status: {start_time}-{end_time}")
            time.sleep(0.7)
    except KeyboardInterrupt:
        print("Program terminated.")
        rpc.close()


if __name__ == "__main__":
    main()
