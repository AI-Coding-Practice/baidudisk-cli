# 百度网盘 CLI 工具

一个基于 Python 的百度网盘命令行工具，使用 `bypy` 库实现。

## 功能特性

- 🔐 安全的用户认证和 token 管理
- 📤 文件上传到百度网盘（支持参数验证）
- 📥 从百度网盘下载文件
- 📋 列出网盘目录内容（支持中英文严格对齐美观表格）
- 👥 支持多用户管理
- 📖 详细的命令行帮助文档

## 安装

1. 克隆项目：
```bash
git clone <repository-url>
cd baidudisk-cli
```

2. 创建虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 查看帮助
```bash
# 查看所有命令
python main.py --help

# 查看具体命令帮助
python main.py login --help
python main.py upload --help
python main.py download --help
python main.py list --help
```

### 登录
```bash
python main.py login --user <用户名>
```

### 上传文件
```bash
python main.py upload --user <用户名> <本地文件路径> <远程文件路径>
```

### 下载文件
```bash
python main.py download --user <用户名> <远程文件路径> <本地文件路径>
```

### 列出目录
```bash
python main.py list --user <用户名> [远程目录路径]
```

## 依赖

- `bypy>=1.8.0` - 百度网盘 Python 客户端
- `cryptography>=3.4` - 加密功能
- `click>=7.0` - 命令行界面
- `wcwidth>=0.2.5` - 表格对齐（支持中英文混排对齐）

## 特性说明

### 参数验证
- 上传命令会自动验证本地文件是否存在且可读
- 所有路径参数都经过类型检查

### 表格对齐
- 使用 `wcwidth` 库实现中英文混排的完美对齐
- 文件名过长时自动截断并显示省略号
- 文件大小自动转换为合适的单位（B/KB/MB/GB）

### 错误处理
- 所有操作都有详细的错误提示
- 异常情况下的友好错误信息

## 注意事项

- 首次使用需要授权，`bypy` 会自动打开浏览器进行授权
- 用户数据存储在 `~/.baidudisk-cli/` 目录下
- Token 使用 Fernet 加密存储，确保安全性

## 故障排除

如果遇到 `baidupcs-py` 安装问题，项目已迁移到使用 `bypy` 库，这是一个更稳定的百度网盘 Python 客户端。

## 许可证

MIT License 