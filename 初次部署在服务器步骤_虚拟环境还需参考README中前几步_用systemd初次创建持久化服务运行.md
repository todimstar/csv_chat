# 初次创建持久化服务

## 创建系统服务(更好更简单的方式)

相比screen，使用systemd（系统守护程序）创建服务更加可靠：

```bash
# 创建服务文件
nano /etc/systemd/system/csv-chat.service
```

将以下内容复制到文件中：(注意`WorkingDirectory`和`ExecStart`中的路径是否符合项目文件夹路径)

```
[Unit]
Description=CSV Chat Streamlit App
After=network.target

[Service]
User=root
WorkingDirectory=/root/csv_chat
ExecStart=/root/csv_chat/.venv/bin/streamlit run src/app.py --server.address=0.0.0.0
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

然后启用并启动服务：

```bash
systemctl enable csv-chat
systemctl start csv-chat
```

## 4. 查看服务状态

```bash
systemctl status csv-chat
```

## 5. 访问您的应用

现在，您可以通过以下地址访问您的应用：

```
http://您服务器的IP地址:8501
```

## 6. 可能遗漏的步骤
1. 服务器防火墙规则没放过8501端口
答：从服务器厂商控制台调整端口规则
2. config.py文件未创建
答：创建文件并配置aiapi的Key