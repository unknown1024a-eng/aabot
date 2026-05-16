import os
import threading
import time
import traceback
import sqlite3
import datetime
from flask import Flask, render_template

# import your bot module
import bot
from config import db_path

# ---------- Flask app ----------
app = Flask(__name__, template_folder='templates', static_folder='static')

def is_expired(time_str: str) -> bool:
    if not time_str: return False
    try:
        server_time = datetime.datetime.now()
        expire_time = datetime.datetime.strptime(time_str, "%Y-%m-%d")
        return expire_time < server_time
    except:
        return False

@app.route("/")
def index_root():
    return "✅ Bot + Web Server is running!"

@app.route('/<code_str>')
def display_id(code_str):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # 1. 먼저 users 테이블의 query 필드에서 조회
        cur.execute("SELECT id, expiredate FROM users WHERE query = ?", (code_str,))
        user_row = cur.fetchone()
        
        if user_row:
            user_id, expire_date = user_row
        else:
            # 2. query로 없으면 licenses 테이블에서 license_key로 조회
            cur.execute("SELECT user_id, expire_date FROM licenses WHERE license_key = ?", (code_str,))
            lic = cur.fetchone()
            if not lic:
                conn.close()
                return render_template("error.html", title="접속 실패", dese="존재하지 않는 코드입니다.")
            user_id, expire_date = lic

        # 만료 체크
        if expire_date and is_expired(expire_date):
            conn.close()
            return render_template("error.html", title="접속 실패", dese="라이센스 유효기간이 만료되었습니다.")
        
        if not user_id:
            conn.close()
            return render_template("error.html", title="접속 실패", dese="해당 코드에 연결된 유저 정보가 없습니다.")

        # production_users에서 유저 정보 가져오기
        cur.execute("""SELECT name, ssn, address, issue_date, region, image_path, created_at
                       FROM production_users
                       WHERE discord_id = ?""", (user_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return render_template("error.html", title="접속 실패", dese="등록된 상세 정보가 없습니다.")

        name, ssn, address, issue_date, region, image_path, created_at = row

        try:
            tmp = ssn.split("-")[0]
            date_fmt = f"{tmp[0:2]}.{tmp[2:4]}.{tmp[4:6]}"
        except:
            date_fmt = issue_date

        return render_template("sex.html",
                               name=name,
                               num=ssn,
                               date=date_fmt,
                               juso=address,
                               make=issue_date,
                               jiname=region,
                               imgurl=image_path)

    except Exception as e:
        print("web error:", e)
        return render_template("error.html", title="접속 실패", dese=f"오류 발생: {e}")

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
                bot.bot.run(token)
            except Exception:
                print("Discord bot: 예외 발생")
                traceback.print_exc()

        t = threading.Thread(target=_run, name="discord-bot-thread", daemon=True)
        t.start()
        print("Discord bot: thread started.")
    except Exception:
        print("Discord bot: starter failed")
        traceback.print_exc()

if os.environ.get("RUN_DISCORD_AT_IMPORT", "1") == "1":
    _start_discord_bot_in_thread()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
