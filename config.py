# config.py
import os

# Render / 로컬 env에 설정된 DISCORD_TOKEN을 가져오거나, 없으면 기본값 사용
TOKEN = os.getenv("DISCORD_TOKEN", "MTUwNTA2MDQxMDcwODIwMTQ4Mg.GdPbuC.7oKNNHTXNF0AO1DyXENLH07nWx4YPXNbWbxsPI")
# OWNER_ID 환경변수를 가져오거나 기본값 사용
OWNER_ID = int(os.getenv("OWNER_ID", "1500854387822563398"))
# 테스트 서버 ID (슬래시 명령어를 즉시 확인하려면 여기에 서버 ID를 입력하세요)
TEST_GUILD_ID = int(os.getenv("TEST_GUILD_ID", "0")) if os.getenv("TEST_GUILD_ID") else None

db_path = os.getenv("DB_PATH", "DB/database.db")
domain = os.getenv("DOMAIN", "https://govr24.store")  # 당신 도메인
