# 配置 MinIO 公开访问

## 问题说明

生产环境通过 Nginx 代理访问 MinIO 时，不使用签名验证，需要设置 bucket 为公开读取。

## 解决方案

### 方法 1：使用 mc（MinIO Client）配置

```bash
# 1. 进入 MinIO 容器
docker exec -it reader_minio sh

# 2. 配置 mc 别名
mc alias set myminio http://localhost:9000 reader reader_dev_password

# 3. 设置 bucket 为公开读取
mc anonymous set download myminio/reader-uploads

# 或者设置为完全公开
mc anonymous set public myminio/reader-uploads

# 4. 验证策略
mc anonymous get myminio/reader-uploads

# 5. 退出容器
exit
```

### 方法 2：通过 MinIO Console

1. 访问 MinIO Console：`http://10.0.169.144:9002`
2. 登录：
   - 用户名：`reader`
   - 密码：`reader_dev_password`
3. 进入 `reader-uploads` bucket
4. 点击 "Access Policy"
5. 选择 "Public" 或 "Download"

### 方法 3：使用 Python 脚本

创建文件 `set_minio_policy.py`：

```python
from minio import Minio
from minio.commonconfig import ENABLED
from minio.versioningconfig import VersioningConfig

# 初始化客户端
client = Minio(
    "10.0.169.144:8999",
    access_key="reader",
    secret_key="reader_dev_password",
    secure=False
)

# 设置 bucket 策略为公开读取
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::reader-uploads/*"]
        }
    ]
}

import json
client.set_bucket_policy("reader-uploads", json.dumps(policy))
print("Bucket policy set successfully!")
```

运行：
```bash
cd /data/ht/workspace/Reader_QAQ
python set_minio_policy.py
```

## 验证

设置完成后，测试访问：

```bash
# 测试直接访问（应该返回图片）
curl -I http://10.0.169.144:8999/reader-uploads/kb_avatars/xxx/xxx.png

# 测试通过 Nginx 代理访问
curl -I http://localhost:3003/minio/reader-uploads/kb_avatars/xxx/xxx.png
```

应该返回 `200 OK` 而不是 `403 Forbidden`。

## 安全建议

### 生产环境

如果担心安全问题，可以：

1. **只公开特定目录**：
   ```json
   {
     "Resource": ["arn:aws:s3:::reader-uploads/kb_avatars/*"]
   }
   ```

2. **添加 Nginx 访问控制**：
   ```nginx
   location /minio/ {
       # 只允许特定 IP
       allow 10.0.0.0/8;
       deny all;
       
       proxy_pass http://reader_minio:9000;
   }
   ```

3. **使用带认证的代理**：
   在 Nginx 中添加 MinIO 认证头，但这会更复杂。

## 快速执行

```bash
# 一键设置公开访问
docker exec reader_minio sh -c '
mc alias set myminio http://localhost:9000 reader reader_dev_password && \
mc anonymous set download myminio/reader-uploads && \
echo "✅ MinIO bucket 已设置为公开读取"
'
```


