# FinalProject 初始化指令记录

## 1. 项目结构
项目根目录：
FinalProject/
- frontend/
- backend/

## 2. 进入后端目录
如果项目在桌面：
```bash
cd ~/Desktop/FinalProject/backend

查看当前为止：pwd
查看当前目录文件：ls
```
## 3. 安装依赖
python3 -m pip install -r requirements.txt

## 4.  启动前后端
 python3 run.py
npm install
 npm run dev

## 5.  启动成功后访问
http://127.0.0.1:8000

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

本项目当前使用 SQLite，不需要额外安装 MySQL。

如果想重置测试数据，可删除该文件后重新启动后端：
```bash
rm finalproject.db
python3 run.py
```

## 七、首次运行建议顺序

### 1. 导入模板
在 `/docs` 中使用：
- `POST /templates/import`

先导入两个模板文件：
- `RedhatLinux模板.xlsx`
- `达梦模板.xlsx`

### 2. 新建项目
在 `/docs` 中使用：
- `POST /projects/`
示例：
```json
{
  "project_code": "20260324A",
  "project_name": "测试项目A",
  "system_name": "测评辅助平台",
  "organization_name": "测试单位",
  "level": "三级",
  "standard_system": "等保2.0"
}
```

### 3. 新增资产
在 `/docs` 中使用：
- `POST /assets/`
Redhat 服务器示例：
```json
{
  "project_id": 1,
  "asset_type": "server_storage",
  "asset_name": "srv-redhat-01",
  "ip_address": "192.168.1.10",
  "os_or_db_type": "Redhat Linux",
  "remark": "测试服务器"
}
```

达梦数据库示例：
```json
{
  "project_id": 1,
  "asset_type": "database",
  "asset_name": "db-dm-01",
  "ip_address": "192.168.1.20",
  "os_or_db_type": "达梦",
  "remark": "测试数据库"
}
```

### 4. 查询资产对应核查记录
在 `/docs` 中使用：
- `GET /records/asset/{asset_id}`

### 5. 更新核查记录
在 `/docs` 中使用：
- `PUT /records/{record_id}`
示例：
```json
{
  "result_record": "已检查系统账户与口令配置，未发现明显异常",
  "compliance_status": "compliant",
  "record_remark": "现场检查正常"
}
```

## 八、符合情况字段说明
数据库中存储的值为：
- `compliant`：符合
- `partial`：部分符合
- `non_compliant`：不符合
注意：接口测试时请填写英文值，不要直接填中文。

## 九、模板导入规则（当前版本）

当前第一版模板导入规则：
- 仅支持：
  - `RedhatLinux模板.xlsx`
  - `达梦模板.xlsx`
- 第 7 行为表头
- 第 8 行跳过
- 第 9 行开始读取检查项数据

模板列包括：
- 序号
- 控制点
- 控制项
- 备注
- 重要程度
- 检查内容
- 判断标准

不作为模板列导入：
- 结果记录
- 符合情况
---


## 十、常见问题

### 1. `python: command not found`
请使用：
```bash
python3 run.py
```
### 2. `cd backend` 提示没有这个目录
说明当前目录不对，请使用完整路径：
```bash
cd ~/Desktop/FinalProject/backend
```
### 3. 项目编号已存在
说明数据库里已经有相同测试数据。可：
- 换一个新的 `project_code`
- 或删除 `finalproject.db` 后重建数据库
