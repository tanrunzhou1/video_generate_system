# UC001 健康检查

## 1. 基本信息

- 用例 ID：UC001
- 用例名称：健康检查
- 类型：HTTP API
- 路径：`GET /health`

## 2. 目标

提供快速存活检查与基础环境标识，便于本地/部署诊断。

## 3. 输入

- Path 参数：无
- Query 参数：无
- Body：无

## 4. 输出

```json
{
  "status": "ok",
  "env": "dev",
  "storage_dir": "./storage"
}
```

## 5. 主流程

1. 客户端调用 `/health`。
2. 路由从缓存的 `get_settings()` 读取配置。
3. 返回服务状态和关键配置字段。

## 6. 异常处理

- 当前实现只要进程存活即返回 `200`。
- TODO：补充 DB/Redis/模型服务依赖检查，支持分级健康状态。

## 7. 代码参考

- `app/api/health.py`
