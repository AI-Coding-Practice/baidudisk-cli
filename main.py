import click
import sys
import io
import re
from contextlib import redirect_stdout
from usermgr import get_pcs, ensure_user, clear_user_auth
from datetime import datetime
from wcwidth import wcswidth

@click.group()
def cli():
    """百度网盘命令行工具 - 基于 bypy 实现
    
    支持文件上传、下载、目录列表等功能，支持多用户管理。
    首次使用需要浏览器授权登录百度网盘账号。
    """
    pass

@cli.command()
@click.option('--user', required=True, help='用户名，用于区分不同用户的认证信息')
def login(user):
    """登录百度网盘账号
    
    首次使用时会自动打开浏览器进行百度网盘授权。
    认证信息会加密存储在 ~/.baidudisk-cli/ 目录下。
    
    示例:
        python main.py login --user alice
    """
    try:
        ensure_user(user)
        bp = get_pcs(user, login=True)
        if bp is None:
            click.echo(f"❌ 用户 {user} 登录失败")
            return
        click.echo(f"✅ 用户 {user} 登录成功")
    except Exception as e:
        click.echo(f"❌ 登录失败: {e}")

@cli.command()
@click.option('--user', required=True, help='用户名，用于清除对应的认证信息')
def logout(user):
    """清除用户的百度网盘认证信息
    
    删除指定用户的认证信息，包括加密的 token 文件。
    如果用户目录为空，也会一并删除。
    
    示例:
        python main.py logout --user alice
    """
    try:
        success = clear_user_auth(user)
        if success:
            click.echo(f"✅ 用户 {user} 已成功登出")
        else:
            click.echo(f"❌ 用户 {user} 登出失败")
    except Exception as e:
        click.echo(f"❌ 登出失败: {e}")

@cli.command()
@click.option('--user', required=True, help='用户名，用于获取对应的认证信息')
@click.argument('localfile', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.argument('remotefile', type=click.Path())
def upload(user, localfile, remotefile):
    """上传文件到百度网盘
    
    将本地文件上传到百度网盘的指定路径。
    
    LOCALFILE: 本地文件路径，必须是存在的文件
    REMOTEFILE: 远程文件路径，如 /documents/file.pdf
    
    示例:
        python main.py upload --user alice ./report.pdf /documents/report.pdf
        python main.py upload --user alice ./image.jpg /photos/vacation/image.jpg
    """
    try:
        bp = get_pcs(user)
        if bp is None:
            return  # 错误信息已在 get_pcs 中显示
        click.echo(f"📤 正在上传 {localfile} 到 {remotefile}...")
        result = bp.upload(localfile, remotefile)
        if result == 0:
            click.echo(f"✅ 上传成功: {localfile} → {remotefile}")
        else:
            click.echo(f"❌ 上传失败，错误代码: {result}")
    except Exception as e:
        click.echo(f"❌ 上传时发生错误: {e}")

@cli.command()
@click.option('--user', required=True, help='用户名，用于获取对应的认证信息')
@click.argument('remotefile', type=click.Path())
@click.argument('localfile', type=click.Path())
def download(user, remotefile, localfile):
    """从百度网盘下载文件
    
    将百度网盘中的文件下载到本地指定路径。
    
    REMOTEFILE: 远程文件路径，如 /documents/file.pdf
    LOCALFILE: 本地文件路径，下载后的保存位置
    
    示例:
        python main.py download --user alice /documents/report.pdf ./downloads/report.pdf
        python main.py download --user alice /photos/vacation/image.jpg ./image.jpg
    """
    try:
        bp = get_pcs(user)
        if bp is None:
            return  # 错误信息已在 get_pcs 中显示
        click.echo(f"📥 正在下载 {remotefile} 到 {localfile}...")
        result = bp.download(remotefile, localfile)
        if result == 0:
            click.echo(f"✅ 下载成功: {remotefile} → {localfile}")
        else:
            click.echo(f"❌ 下载失败，错误代码: {result}")
    except Exception as e:
        click.echo(f"❌ 下载时发生错误: {e}")

@cli.command()
@click.option('--user', required=True, help='用户名，用于获取对应的认证信息')
@click.argument('remotedir', default='/', required=False, type=click.Path())
def list(user, remotedir):
    """列出百度网盘目录内容
    
    显示指定目录下的文件和子目录列表。
    支持中英文混排的表格对齐显示。
    
    REMOTEDIR: 远程目录路径，默认为根目录 /
    
    输出格式:
        - 文件名: 支持中英文，过长会自动截断
        - 类型: 文件或目录
        - 大小: 自动转换为 B/KB/MB/GB 单位
        - 修改时间: YYYY-MM-DD HH:MM:SS 格式
    
    示例:
        python main.py list --user alice
        python main.py list --user alice /documents
        python main.py list --user alice /photos/vacation
    """
    bp = get_pcs(user)
    if bp is None:
        return  # 错误信息已在 get_pcs 中显示
    
    try:
        output = io.StringIO()
        with redirect_stdout(output):
            result = bp.list(remotedir)
        if result == 0:
            output_text = output.getvalue()
            lines = output_text.strip().split('\n')
            
            if len(lines) > 1:
                click.echo(f"\n📁 目录: {remotedir}")
                click.echo("=" * 90)
                # 列宽设置（按显示宽度）
                name_width = 45
                type_width = 6
                size_width = 12
                time_width = 20
                # 表头
                def pad(s, width):
                    padlen = width - wcswidth(s)
                    return s + ' ' * max(0, padlen)
                click.echo(f"{pad('文件名', name_width)} {pad('类型', type_width)} {pad('大小', size_width)} {pad('修改时间', time_width)}")
                click.echo("-" * 90)
                
                for line in lines[1:]:
                    if line.strip():
                        parts = line.strip().split()
                        
                        if len(parts) >= 5:
                            file_type = parts[0]
                            
                            if file_type == 'D':  # 目录
                                # 格式: D 目录名 0 日期, 时间
                                if len(parts) >= 5:
                                    name = parts[1]
                                    size_part = parts[2]
                                    date_part = parts[3].replace(',', '')
                                    time_part = parts[4]
                                else:
                                    continue
                            else:  # 文件
                                # 格式: F 文件名 大小 日期, 时间 hash
                                if len(parts) >= 6:
                                    name = parts[1]
                                    size_part = parts[2]
                                    date_part = parts[3].replace(',', '')
                                    time_part = parts[4]
                                    # hash = parts[5]  # 不需要显示
                                else:
                                    continue
                            
                            # 类型
                            type_str = "目录" if file_type == 'D' else "文件"
                            
                            # 文件大小格式化
                            try:
                                size_int = int(size_part)
                                if size_int >= 1024**3:
                                    size_str = f"{size_int/(1024**3):.2f} GB"
                                elif size_int >= 1024**2:
                                    size_str = f"{size_int/(1024**2):.2f} MB"
                                elif size_int >= 1024:
                                    size_str = f"{size_int/1024:.2f} KB"
                                else:
                                    size_str = f"{size_int} B"
                            except:
                                size_str = "0 B"
                            
                            # 时间格式化
                            try:
                                dt_str = f"{date_part} {time_part}"
                                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                date_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                            except:
                                date_time = f"{date_part} {time_part}"
                            
                            # 文件名截断（按宽度）
                            max_name = name
                            while wcswidth(max_name) > name_width:
                                max_name = max_name[:-1]
                            if max_name != name:
                                max_name = max_name[:-3] + '...'
                            
                            click.echo(f"{pad(max_name, name_width)} {pad(type_str, type_width)} {pad(size_str, size_width)} {pad(date_time, time_width)}")
                
                click.echo("=" * 90)
            else:
                click.echo(f"📁 目录 {remotedir} 为空")
        else:
            click.echo(f"❌ 列出目录失败，错误代码: {result}")
    except Exception as e:
        click.echo(f"❌ 列出目录时发生错误: {e}")

if __name__ == '__main__':
    cli() 