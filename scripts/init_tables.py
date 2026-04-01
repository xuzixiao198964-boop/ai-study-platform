"""Create database tables on server"""
import sys
import paramiko

def run():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("101.201.244.150", 22, "root", "Xuzi-xiao198964", timeout=15)

    cmd = """cd /opt/ai-study-platform && . venv/bin/activate && python3 << 'PYEOF'
from sqlalchemy import create_engine
from app.core.database import Base
from app.models import *
import os
from dotenv import dotenv_values
config = dotenv_values("/opt/ai-study-platform/.env")
db_url = config.get("DATABASE_URL", "postgresql+asyncpg://aistudy:aistudy_db_2026@localhost:5432/ai_study").replace("+asyncpg", "")
engine = create_engine(db_url)
Base.metadata.create_all(bind=engine)
print("Tables created successfully")
PYEOF"""

    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    if out.strip():
        print(out.strip())
    if err.strip():
        print(f"[STDERR] {err.strip()}")
    print(f"[EXIT: {code}]")
    ssh.close()
    return code

if __name__ == "__main__":
    run()
