#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""部署最终修复到服务器"""

import paramiko
import os
import sys

# 服务器配置
HOST = '45.78.5.184'
PORT = 22
USER = 'root'
PASSWORD = 'FYCZWP2uPLjR'

def filter_output(text):
    """过滤特殊字符，避免编码错误"""
    if not text:
        return ''
    return ''.join(c for c in text if ord(c) < 0x10000)

def upload_file(sftp, local_path, remote_path):
    """上传单个文件"""
    try:
        remote_dir = os.path.dirname(remote_path)
        try:
            sftp.stat(remote_dir)
        except IOError:
            dirs = []
            while remote_dir and remote_dir != '/':
                dirs.append(remote_dir)
                remote_dir = os.path.dirname(remote_dir)
            dirs.reverse()
            for d in dirs:
                try:
                    sftp.stat(d)
                except IOError:
                    sftp.mkdir(d)

        sftp.put(local_path, remote_path)
        print(f'[OK] {local_path} -> {remote_path}')
        return True
    except Exception as e:
        print(f'[FAIL] {local_path}: {filter_output(str(e))}')
        return False

def main():
    print('=== 部署最终修复到服务器 ===\n')

    print(f'连接到 {HOST}...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, PORT, USER, PASSWORD)
        sftp = ssh.open_sftp()
        print('[OK] SSH连接成功\n')

        print('1. 上传Flutter源文件...')
        local_file = 'D:/work/ai-study-platform/mobile/lib/screens/student/student_home_screen.dart'
        remote_file = '/opt/ai-study-platform/mobile/lib/screens/student/student_home_screen.dart'
        upload_file(sftp, local_file, remote_file)

        print('\n2. 构建Flutter Web应用...')
        stdin, stdout, stderr = ssh.exec_command(
            'cd /opt/ai-study-platform/mobile && /root/flutter/bin/flutter build web --release'
        )

        for line in stdout:
            line = filter_output(line.strip())
            if line:
                print(f'  {line}')

        exit_code = stdout.channel.recv_exit_status()
        if exit_code == 0:
            print('[OK] Flutter构建成功')
        else:
            print(f'[FAIL] Flutter构建失败')
            return

        print('\n3. 复制到Nginx目录...')
        stdin, stdout, stderr = ssh.exec_command(
            'cp -r /opt/ai-study-platform/mobile/build/web/* /opt/ai-study-mobile/build/web/'
        )
        stdout.channel.recv_exit_status()
        print('[OK] 复制完成')

        print('\n4. 重启Nginx...')
        stdin, stdout, stderr = ssh.exec_command('systemctl restart nginx')
        stdout.channel.recv_exit_status()
        print('[OK] Nginx已重启')

        print('\n=== 部署完成 ===')

    except Exception as e:
        print(f'\n[ERROR] {filter_output(str(e))}')
        sys.exit(1)
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
