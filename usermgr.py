import os
import json
import shutil
import io
from contextlib import redirect_stdout
from bypy import ByPy
from cryptography.fernet import Fernet
import click
from datetime import datetime

BASE_DIR = os.path.expanduser("~/.baidudisk-cli")
KEY_FILE = os.path.join(BASE_DIR, "key.bin")

def get_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        os.makedirs(BASE_DIR, exist_ok=True)
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return key

def encrypt_token(token_data, user):
    key = get_key()
    f = Fernet(key)
    user_dir = os.path.join(BASE_DIR, user)
    os.makedirs(user_dir, exist_ok=True)
    token_json = json.dumps(token_data)
    with open(os.path.join(user_dir, "token.enc"), "wb") as ftoken:
        ftoken.write(f.encrypt(token_json.encode()))

def decrypt_token(user):
    key = get_key()
    f = Fernet(key)
    user_dir = os.path.join(BASE_DIR, user)
    with open(os.path.join(user_dir, "token.enc"), "rb") as ftoken:
        token_json = f.decrypt(ftoken.read()).decode()
        return json.loads(token_json)

def ensure_user(user):
    user_dir = os.path.join(BASE_DIR, user)
    os.makedirs(user_dir, exist_ok=True)

def is_user_authenticated(user):
    """检查用户是否已经认证"""
    user_dir = os.path.join(BASE_DIR, user)
    token_file = os.path.join(user_dir, "token.enc")
    return os.path.exists(token_file)

def clear_user_auth(user):
    """清除用户的认证信息
    
    Args:
        user: 用户名
        
    Returns:
        bool: 是否成功清除
    """
    user_dir = os.path.join(BASE_DIR, user)
    token_file = os.path.join(user_dir, "token.enc")
    
    if not os.path.exists(token_file):
        click.echo(f"ℹ️  用户 {user} 没有认证信息需要清除")
        return True
    
    try:
        # 删除认证文件
        os.remove(token_file)
        click.echo(f"✅ 已清除用户 {user} 的认证信息")
        
        # 如果用户目录为空，也删除目录
        if os.path.exists(user_dir) and not os.listdir(user_dir):
            os.rmdir(user_dir)
            #click.echo(f"🗑️  已删除空的用户目录: {user_dir}")
        
        return True
    except Exception as e:
        click.echo(f"❌ 清除用户 {user} 认证信息时发生错误: {e}")
        return False

def clear_bypy_tokens():
    """清除 bypy 的全局授权信息，强制重新授权"""
    try:
        # bypy 的授权文件通常存储在用户主目录下
        home_dir = os.path.expanduser("~")
        bypy_token_file = os.path.join(home_dir, ".bypy")
        
        if os.path.exists(bypy_token_file):
            shutil.rmtree(bypy_token_file)
            #click.echo("🗑️  已清除 bypy 全局授权信息")
        else:
            click.echo("ℹ️  没有找到 bypy 全局授权信息")
    except Exception as e:
        click.echo(f"⚠️  清除 bypy 授权信息时发生错误: {e}")

def get_pcs(user, login=False):
    """获取百度网盘客户端实例，确保用户隔离"""
    user_dir = os.path.join(BASE_DIR, user)
    token_file = os.path.join(user_dir, "token.enc")
    
    if not os.path.exists(token_file):
        if login:
            # 只有在明确要求登录时才创建新用户
            click.echo(f"🔐 正在为用户 {user} 进行百度网盘授权...")
            
            # 强制清除现有的 bypy 授权信息，确保需要重新授权
            clear_bypy_tokens()
            
            bp = ByPy()
            # 检查是否成功授权
            try:
                # 尝试获取用户信息来验证授权是否成功，但不显示输出
                output = io.StringIO()
                with redirect_stdout(output):
                    result = bp.list('/')
                if result == 0:
                    # 授权成功，保存用户信息
                    user_info = {
                        'user': user,
                        'authenticated': True,
                        'timestamp': datetime.now().isoformat()
                    }
                    encrypt_token(user_info, user)
                    click.echo(f"✅ 用户 {user} 授权成功")
                    return bp
                else:
                    click.echo(f"❌ 用户 {user} 授权失败")
                    return None
            except Exception as e:
                click.echo(f"❌ 用户 {user} 授权过程中发生错误: {e}")
                return None
        else:
            # 用户不存在且未要求登录
            click.echo(f"❌ 用户 {user} 未认证，请先使用 'login' 命令进行授权")
            return None
    else:
        # 用户已存在，尝试使用保存的认证信息
        try:
            user_info = decrypt_token(user)
            if user_info.get('authenticated', False):
                # 创建新的 ByPy 实例（bypy 会使用全局授权信息）
                bp = ByPy()
                # 验证授权是否仍然有效
                output = io.StringIO()
                with redirect_stdout(output):
                    result = bp.list('/')
                if result == 0:
                    return bp
                else:
                    click.echo(f"❌ 用户 {user} 的授权已过期，请重新登录")
                    # 删除过期的认证信息
                    os.remove(token_file)
                    return None
            else:
                click.echo(f"❌ 用户 {user} 认证信息无效")
                return None
        except Exception as e:
            click.echo(f"❌ 读取用户 {user} 认证信息时发生错误: {e}")
            return None 

def set_default_user(user):
    """设置默认用户"""
    os.makedirs(BASE_DIR, exist_ok=True)
    default_file = os.path.join(BASE_DIR, "default_user")
    with open(default_file, "w", encoding="utf-8") as f:
        f.write(user)

def get_default_user():
    """获取默认用户，如果没有则返回 None"""
    default_file = os.path.join(BASE_DIR, "default_user")
    if os.path.exists(default_file):
        with open(default_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None 