"""综合部署脚本：上传后端、官网、配置，并重启服务"""
import sys
import os
import paramiko
import stat

SERVER = "101.201.244.150"
USER = "root"
PASSWORD = "Xuzi-xiao198964"
BACKEND_LOCAL = os.path.join(os.path.dirname(__file__), "..", "server")
WEBSITE_LOCAL = os.path.join(os.path.dirname(__file__), "..", "website")
DOC_LOCAL = os.path.join(os.path.dirname(__file__), "..", "doc")
DEPLOY_LOCAL = os.path.join(os.path.dirname(__file__), "..", "deploy")
BACKEND_REMOTE = "/opt/ai-study-platform"
WEBSITE_REMOTE = "/opt/ai-study-website"


def ssh_exec(ssh, cmd, timeout=120):
    print(f"[CMD] {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    if out.strip():
        print(out.strip())
    if err.strip():
        print(f"[STDERR] {err.strip()}")
    return code


def upload_dir(sftp, local_dir, remote_dir, exclude=None, skip_files=None):
    exclude = exclude or set()
    skip_files = skip_files or set()
    local_dir = os.path.abspath(local_dir)
    for root, dirs, files in os.walk(local_dir):
        dirs[:] = [d for d in dirs if d not in exclude]
        for f in files:
            if f in skip_files:
                continue
            local_path = os.path.join(root, f)
            rel = os.path.relpath(local_path, local_dir)
            remote_path = remote_dir + "/" + rel.replace("\\", "/")
            remote_parent = os.path.dirname(remote_path).replace("\\", "/")
            mkdir_p(sftp, remote_parent)
            print(f"  UPLOAD {rel}")
            sftp.put(local_path, remote_path)


def mkdir_p(sftp, path):
    parts = path.split("/")
    current = ""
    for p in parts:
        if not p:
            current = "/"
            continue
        current = current + "/" + p if current != "/" else "/" + p
        try:
            sftp.stat(current)
        except FileNotFoundError:
            sftp.mkdir(current)


def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {SERVER}...")
    ssh.connect(SERVER, 22, USER, PASSWORD, timeout=15)
    sftp = ssh.open_sftp()

    # 1. Upload backend (exclude .env to preserve server config)
    print("\n=== Uploading backend ===")
    upload_dir(
        sftp,
        BACKEND_LOCAL,
        BACKEND_REMOTE,
        exclude={"__pycache__", "venv", ".venv", "alembic", ".pytest_cache"},
        skip_files={".env"},
    )

    # 2. Upload website
    print("\n=== Uploading official website ===")
    upload_dir(sftp, WEBSITE_LOCAL, WEBSITE_REMOTE)

    # 2b. Upload project documentation (Markdown) for static access under /docs/
    print("\n=== Uploading doc/ to website/docs ===")
    upload_dir(sftp, DOC_LOCAL, WEBSITE_REMOTE + "/docs")

    # 3. Upload deploy configs
    print("\n=== Uploading deploy configs ===")
    sftp.put(os.path.join(DEPLOY_LOCAL, "nginx.conf"), "/etc/nginx/sites-available/ai-study")
    sftp.put(os.path.join(DEPLOY_LOCAL, "ai-study.service"), "/etc/systemd/system/ai-study.service")

    sftp.close()

    # 4. Update server .env (add new fields, preserve existing values)
    print("\n=== Updating server .env ===")
    ssh_exec(ssh, f"""cd {BACKEND_REMOTE} && {{
grep -q 'VOLCANO_APP_ID' .env || cat >> .env << 'ENVEOF'

VOLCANO_APP_ID=
VOLCANO_ACCESS_KEY=
VOLCANO_SECRET_KEY=

TENCENT_SECRET_ID=
TENCENT_SECRET_KEY=
ENVEOF
}}""")
    ssh_exec(ssh, f"cd {BACKEND_REMOTE} && sed -i 's/ACCESS_TOKEN_EXPIRE_MINUTES=1440/ACCESS_TOKEN_EXPIRE_MINUTES=2880/' .env")
    ssh_exec(ssh, f"""cd {BACKEND_REMOTE} && {{
grep -q 'ADMIN_USERNAME' .env || cat >> .env << 'ENVEOF'

ADMIN_USERNAME=admin
ADMIN_PASSWORD=AiStudy@2026
ENVEOF
}}""")

    # 5. Ensure symlink
    ssh_exec(ssh, "ln -sf /etc/nginx/sites-available/ai-study /etc/nginx/sites-enabled/ai-study")
    ssh_exec(ssh, "rm -f /etc/nginx/sites-enabled/default")

    # 6. Install/update Python deps
    print("\n=== Installing Python dependencies ===")
    ssh_exec(ssh, f"cd {BACKEND_REMOTE} && python3 -m venv venv 2>/dev/null; . venv/bin/activate && pip install -q -r requirements.txt && pip install -q pytest pytest-asyncio aiosqlite pytest-cov")

    # 6b. Backend unit tests (SQLite memory, no integration)
    print("\n=== Running backend unit tests ===")
    code_tests = ssh_exec(
        ssh,
        f"cd {BACKEND_REMOTE} && . venv/bin/activate && "
        f"export DATABASE_URL=sqlite+aiosqlite:///:memory: && "
        f"export SECRET_KEY=deploy-test-secret-key-32chars-minimum!! && "
        f"export ADMIN_USERNAME=admin && export ADMIN_PASSWORD=AiStudy@2026 && "
        f"export REDIS_URL=redis://127.0.0.1:6379/15 && "
        f"python -m pytest tests/ -v --tb=short -m 'not integration'",
        timeout=300,
    )
    if code_tests != 0:
        print("[ERROR] Unit tests failed — aborting before service restart")
        sftp.close()
        ssh.close()
        sys.exit(1)

    # 7. Init database tables (create new tables)
    print("\n=== Initializing database ===")
    ssh_exec(ssh, f"""cd {BACKEND_REMOTE} && . venv/bin/activate && python3 -c "
from sqlalchemy import create_engine
from app.core.database import Base
from app.models import *
from dotenv import load_dotenv
import os
load_dotenv()
db_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://aistudy:aistudy_db_2026@localhost:5432/ai_study').replace('+asyncpg', '')
engine = create_engine(db_url)
Base.metadata.create_all(bind=engine)
print('Tables created/updated successfully')
" """)

    # 8. Open port 8000 in firewall if needed
    print("\n=== Configuring firewall ===")
    ssh_exec(ssh, "ufw allow 8000/tcp 2>/dev/null || true")

    # 9. Reload systemd and restart services
    print("\n=== Restarting services ===")
    ssh_exec(ssh, "systemctl daemon-reload")
    ssh_exec(ssh, "systemctl restart ai-study")
    ssh_exec(ssh, "nginx -t && systemctl reload nginx")

    # 10. Verify
    print("\n=== Verifying deployment ===")
    ssh_exec(ssh, "sleep 2 && curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:80/ | xargs -I {} echo 'Website (port 80): HTTP {}'")
    ssh_exec(ssh, "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8001/health | xargs -I {} echo 'Backend (port 8001): HTTP {}'")
    ssh_exec(ssh, "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/health | xargs -I {} echo 'App via Nginx (port 8000): HTTP {}'")
    ssh_exec(ssh, "systemctl is-active ai-study | xargs -I {} echo 'Service status: {}'")
    ssh_exec(ssh, "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:80/admin.html | xargs -I {} echo 'Admin page (port 80): HTTP {}'")
    ssh_exec(ssh, """curl -s -o /dev/null -w '%{http_code}' -X POST http://127.0.0.1:8001/api/v1/admin/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"AiStudy@2026"}' | xargs -I {} echo 'Admin API login: HTTP {}'""")

    ssh.close()
    print("\n=== Deployment complete ===")


if __name__ == "__main__":
    main()
