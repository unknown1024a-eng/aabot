# main.py
import os
import threading
import time
import traceback
from flask import Flask

# import your bot module (must be in same repo)
import bot    # bot.py 파일이 동일 레포에 있어야 함

# ---------- Flask app (gunicorn이 찾는 app) ----------
app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Bot + Web Server is running!"

# ---------- Discord bot background starter ----------
def _start_discord_bot_in_thread():
    try:
        token = getattr(bot, "TOKEN", None)
        if not token:
            print("ERROR: DISCORD_TOKEN 환경변수가 설정되어 있지 않습니다. 봇을 시작하지 않습니다.")
            return

        def _run():
            try:
                print("Discord bot: starting bot.run() ...")
                # bot.bot은 bot.py에서 생성된 commands.Bot 인스턴스여야 합니다.
                bot.bot.run(token)
            except Exception:
                print("Discord bot: 예외 발생(스택트레이스 출력)")
                traceback.print_exc()

        t = threading.Thread(target=_run, name="discord-bot-thread", daemon=True)
        t.start()
        print("Discord bot: thread started.")
    except Exception:
        print("Discord bot: starter failed")
        traceback.print_exc()

# 환경변수로 자동 시작 여부 제어 (기본: 자동 시작)
# Render에서 gunicorn으로 import될 때 모듈 레벨 코드가 실행되므로 여기서 봇을 시작합니다.
if os.environ.get("RUN_DISCORD_AT_IMPORT", "1") == "1":
    # Gunicorn이 여러 워커로 띄워지면 봇이 중복 실행될 수 있으니 Render 설정에서 workers=1 로 지정하세요.
    _start_discord_bot_in_thread()

# if you want to run locally with `python main.py`, also allow direct run
if __name__ == "__main__":
    # (이미 위에서 import 시에 시작되었을 수 있으므로 중복 시작을 피하려면 RUN_DISCORD_AT_IMPORT 를 조정)
    # 간단히 Flask 개발 서버 실행
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
