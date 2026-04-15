# FinalProject 初始化指令记录

## 1. 进入后端目录
如果项目在桌面：
```bash
cd ~/Desktop/FinalProject/backend
cd ~/Desktop/FinalProject/frontend
查看当前为止：pwd
查看当前目录文件：ls
```
## 2. 安装依赖
访问 Python 官网 macOS 下载页：https://www.python.org/downloads/macos/
```bash
/bin/zsh -c "$(curl -fsSL https://gitee.com/cunkai/HomebrewCN/raw/master/Homebrew.sh)"
选 1（清华大学）
y
1
5（阿里巴巴）
source /Users/celine/.zprofile
brew -v
python3 -m pip install -r requirements.txt
```
安装 node 的 mac 版：https://nodejs.org/en/download
在终端输入：npm install

## 3.  启动前后端
 python3 run.py
 npm run dev

## 5.  启动成功后访问
http://localhost:8000/docs
http://localhost:5173/projects

# FinalProject
基于 Python + FastAPI + SQLite 的等级保护测评辅助系统简化版后端原型。

## 一、项目结构
```text
FinalProject/
├─ frontend/
├─ backend/
└─ README.md
```

## 六、数据库说明
如果想重置测试数据，可删除该文件后重新启动后端：
```bash
rm finalproject.db
python3 run.py
```
如果想更改数据库
```bash
cd ~/Desktop/FinalProject/backend
sqlite3 finalproject.db
```
例如：
```bash
ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN lock_until DATETIME;
```