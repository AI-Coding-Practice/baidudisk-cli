# 百度网盘 CLI 工具使用指南

## 快速开始

### 1. 查看帮助文档
```bash
# 查看所有命令
python main.py --help

# 查看具体命令帮助
python main.py login --help
python main.py upload --help
python main.py download --help
python main.py list --help
```

### 2. 首次登录
```bash
python main.py login --user your_username
```
首次使用时会自动打开浏览器进行百度网盘授权。

## 使用示例

### 列出文件
```bash
# 列出根目录
python main.py list --user your_username

# 列出指定目录
python main.py list --user your_username /your_folder

# 列出子目录
python main.py list --user your_username /your_folder/subfolder
```

### 上传文件
```bash
# 上传单个文件
python main.py upload --user your_username ./local_file.txt /remote_file.txt

# 上传到指定目录
python main.py upload --user your_username ./document.pdf /documents/report.pdf
```

### 下载文件
```bash
# 下载单个文件
python main.py download --user your_username /remote_file.txt ./local_file.txt

# 下载到指定目录
python main.py download --user your_username /documents/report.pdf ./downloads/report.pdf
```

## 输出格式说明

### 文件列表格式
```
📁 目录: /your_folder
================================================================================
文件名                                          类型     大小         修改时间
--------------------------------------------------------------------------------
📄 example.pdf                                  文件     1.2 MB      2025-07-19 09:34
📁 documents                                    目录     0 B         2025-07-19 09:30
📄 long_filename_that_gets_truncated.pdf       文件     15.7 MB     2025-07-19 09:25
================================================================================
```

### 状态图标说明
- ✅ 成功
- ❌ 失败
- 📤 上传中
- 📥 下载中
- 📁 目录
- 📄 文件

## 依赖

- `bypy>=1.8.0` - 百度网盘 Python 客户端
- `cryptography>=3.4` - 加密功能
- `click>=7.0` - 命令行界面
- `wcwidth>=0.2.5` - 表格对齐（支持中英文混排对齐）

## 功能特性

### 参数验证
- **文件存在性检查**: 上传命令会自动验证本地文件是否存在且可读
- **路径类型检查**: 所有路径参数都经过类型验证
- **用户友好错误**: 参数错误时提供清晰的错误提示

### 表格对齐
- **中英文混排**: 使用 `wcwidth` 库实现完美对齐
- **智能截断**: 文件名过长时自动截断并显示省略号
- **单位转换**: 文件大小自动转换为合适的单位（B/KB/MB/GB）
- **时间格式化**: 统一的时间显示格式（YYYY-MM-DD HH:MM:SS）

### 错误处理
- **详细错误信息**: 所有操作都有详细的错误提示
- **异常捕获**: 异常情况下的友好错误信息
- **状态反馈**: 操作过程中的实时状态反馈

## 注意事项

1. **首次使用**: 需要浏览器授权，确保网络连接正常
2. **文件路径**: 支持相对路径和绝对路径
3. **文件名**: 长文件名会自动截断显示
4. **多用户**: 每个用户的认证信息独立存储
5. **错误处理**: 所有操作都有详细的错误提示
6. **参数验证**: 上传文件时会自动检查文件是否存在

## 故障排除

### 常见问题

1. **授权失败**
   - 检查网络连接
   - 确保浏览器能正常打开
   - 重新运行登录命令

2. **文件上传/下载失败**
   - 检查文件路径是否正确
   - 确认有足够的存储空间
   - 检查网络连接
   - 确认本地文件存在且可读（上传时）

3. **列表显示异常**
   - 检查目录路径是否存在
   - 确认有访问权限

4. **参数错误**
   - 使用 `--help` 查看详细的参数说明
   - 检查文件路径是否正确
   - 确认参数顺序是否正确

### 获取帮助
```bash
# 查看所有命令
python main.py --help

# 查看特定命令帮助
python main.py upload --help
python main.py download --help
python main.py list --help
```

### 调试技巧
```bash
# 检查文件是否存在
ls -la your_file.txt

# 检查目录权限
ls -la your_directory/

# 查看详细错误信息
python main.py your_command --user username 2>&1
``` 