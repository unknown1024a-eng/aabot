from flask import Flask, render_template
import sqlite3
import datetime
from config import db_path

app = Flask(__name__)

# ========== 유효기간 체크 ========== #
def is_expired(time_str: str) -> bool:
    """만료 여부 체크"""
    server_time = datetime.datetime.now()
    expire_time = datetime.datetime.strptime(time_str, "%Y-%m-%d")
    return expire_time < server_time


# ========== 라우트: 코드(Query 또는 License) 기반 조회 ========== #
@app.route('/<code_str>')
def index(code_str):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # 1. 먼저 users 테이블의 query 필드에서 조회 (봇이 생성한 링크 대응)
        cur.execute("SELECT id, expiredate FROM users WHERE query = ?", (code_str,))
        user_row = cur.fetchone()
        
        if user_row:
            user_id, expire_date = user_row
        else:
            # 2. query로 없으면 licenses 테이블에서 license_key로 조회 (하위 호환성)
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

        # row = (name, ssn, address, issue_date, region, image_path, created_at)
        name, ssn, address, issue_date, region, image_path, created_at = row

        # 주민번호 앞자리 포맷 (선택사항)
        try:
            tmp = ssn.split("-")[0]
            date_fmt = f"{tmp[0:2]}.{tmp[2:4]}.{tmp[4:6]}"
        except:
            date_fmt = issue_date  # 포맷 실패 시 원본 유지

        return render_template("sex.html",
                               name=name,
                               num=ssn,
                               date=date_fmt,
                               juso=address,
                               make=issue_date,
                               jiname=region,
                               imgurl=image_path)

    except Exception as e:
        print("error:", e)
        return render_template("error.html", title="접속 실패", dese="예기치 못한 오류가 발생했습니다.")


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

