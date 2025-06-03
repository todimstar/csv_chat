# 后端 API 文档（Backend API Documentation）
版本：1.0
日期：2025-05-28
作者：后端团队
状态：草稿

## 1. 概述
本文档基于 OpenAPI 3.0 标准，描述磁盘空间分析助手后端提供的 RESTful 接口，供前端和第三方系统调用。所有请求和响应均使用 JSON 格式。

## 2. 认证与授权
- **认证方式**：Bearer Token（JWT）或 API Key
- **Headers**：
  - `Authorization: Bearer <token>` 或 `X-API-Key: <apikey>`
- **权限控制**：基于角色的访问控制（RBAC），普通用户仅能访问自身任务数据，运维角色可访问日志接口。

## 3. 接口列表

### 3.1 文件上传接口
- **URL**：POST `/api/v1/upload`
- **请求头**：
  - `Content-Type: multipart/form-data`
  - `Authorization: Bearer <token>` 或 `X-API-Key: <apikey>`
- **请求参数**：
  | 参数   | 类型       | 必填 | 说明       |
  | ------ | ---------- | ---- | ---------- |
  | file   | file       | 是   | WizTree 导出的 CSV 文件 |
- **响应示例**：
  - **成功 (200 OK)**
    ```json
    {
      "analysis_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "status": "pending"
    }
    ```
  - **失败 (4xx/5xx)**
    ```json
    {
      "code": "InvalidFileFormat",
      "message": "上传文件格式不支持，只接受 .csv 格式"
    }
    ```

### 3.2 查询分析状态与结果
- **URL**：GET `/api/v1/analysis/{analysis_id}`
- **请求头**：
  - `Authorization: Bearer <token>` 或 `X-API-Key: <apikey>`
- **路径参数**：
  | 参数         | 类型   | 必填 | 说明           |
  | ------------ | ------ | ---- | -------------- |
  | analysis_id  | UUID   | 是   | 分析任务唯一标识 |
- **响应示例**：
  - **处理中 (200 OK)**
    ```json
    {
      "analysis_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "status": "processing"
    }
    ```
  - **已完成 (200 OK)**
    ```json
    {
      "analysis_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "status": "completed",
      "summary": {
        "total_files": 1024,
        "total_size": "50GB",
        "largest_files": [
          {"path": "/path/to/file.mp4", "size": "5GB"},
          {"path": "/path/to/file.zip", "size": "3GB"}
        ],
        "type_summary": {"video": "60%", "image": "20%", "other": "20%"}
      }
    }
    ```
  - **失败 (500 Internal Server Error)**
    ```json
    {
      "code": "AnalysisError",
      "message": "分析过程中发生错误，请重试或联系管理员"
    }
    ```

### 3.3 文件夹内容 AI 问答
- **URL**：POST `/api/v1/analysis/{analysis_id}/query`
- **请求头**：
  - `Content-Type: application/json`
  - `Authorization: Bearer <token>` 或 `X-API-Key: <apikey>`
- **路径参数**：
  | 参数         | 类型   | 必填 | 说明           |
  | ------------ | ------ | ---- | -------------- |
  | analysis_id  | UUID   | 是   | 分析任务唯一标识 |
- **请求体**：
  ```json
  {
    "folder_path": "/path/to/folder",
    "user_query": "这个文件夹中的 .log 文件是做什么的？"
  }
  ```
- **响应示例**：
  - **成功 (200 OK)**
    ```json
    {
      "analysis_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "folder_path": "/path/to/folder",
      "query": "这个文件夹中的 .log 文件是做什么的？",
      "response": "这些 .log 文件通常是应用程序运行过程中的日志文件，记录了系统事件和错误信息。根据文件大小和时间戳，建议清理超过 30 天前的日志文件，以释放空间。"
    }
    ```
  - **失败 (400 Bad Request)**
    ```json
    {
      "code": "InvalidQuery",
      "message": "请求格式错误，请检查 folder_path 或 user_query 是否有效"
    }
    ```

### 3.4 日志查询接口
- **URL**：GET `/api/v1/logs`
- **请求头**：
  - `Authorization: Bearer <token>`（需运维角色）
- **查询参数**：
  | 参数      | 类型    | 必填 | 说明                          |
  | --------- | ------- | ---- | ----------------------------- |
  | start_date| string  | 否   | 起始日期，格式 YYYY-MM-DD     |
  | end_date  | string  | 否   | 结束日期，格式 YYYY-MM-DD     |
  | level     | string  | 否   | 日志级别 (INFO, WARN, ERROR)  |
- **响应示例** （200 OK）
  ```json
  [
    {"timestamp": "2025-05-28T10:00:00Z", "level": "INFO", "message": "Upload task created: 3fa85f64 ..."},
    {"timestamp": "2025-05-28T10:05:00Z", "level": "ERROR", "message": "分析任务失败: 3fa85f64 ..."}
  ]
  ```

## 4. 错误码表
| 错误码               | HTTP 状态码 | 描述                          |
| -------------------- | ----------- | ----------------------------- |
| InvalidFileFormat    | 400         | 上传文件格式不支持            |
| AnalysisNotFound     | 404         | 未找到对应的分析任务          |
| AnalysisError        | 500         | 分析过程发生未知错误          |
| Unauthorized         | 401         | 认证失败或未提供凭证          |
| Forbidden            | 403         | 无权访问此资源                |
| InvalidQuery         | 400         | 请求参数（查询）校验失败      |

## 5. 数据模型
### 5.1 AnalysisSummary
```json
{
  "total_files": 1024,
  "total_size": "50GB",
  "largest_files": [ {"path": "...", "size": "..."} ],
  "type_summary": {"video": "...", "image": "..."}
}
```

### 5.2 AIQueryRequest
```json
{
  "folder_path": "/path/to/folder",
  "user_query": "..."
}
```

### 5.3 ErrorResponse
```json
{
  "code": "ErrorCode",
  "message": "错误描述"
}
```

---
*详细 OpenAPI YAML 规范见 `docs/backend/openapi.yaml`（可选）* 