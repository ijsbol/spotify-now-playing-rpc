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
            timestamp_now = time.time()
            start_timestamp = timestamp_now - (progress_ms/1000)
            end_timestamp = timestamp_now + ((duration_ms-progress_ms)/1000) - 1  # weird off-by-one-error
            rpc.update(
                activity_type=ActivityType.LISTENING,
                state=artist_names,
                details=f"{song_name}",
                large_image=album_image_url,
                large_text=f"🎵 {lyrics_now}",
                start=start_timestamp,
                end=end_timestamp,
            )
            print(f"Updated status: {format_ms(progress_ms)}-{format_ms(duration_ms)}")
            time.sleep(0.7)
    except KeyboardInterrupt:
        print("Program terminated.")
        rpc.close()
    except Exception:
        print("Discord unavailable to create RPC pipe.")
        time.sleep(30)
        main()


if __name__ == "__main__":
    main()
