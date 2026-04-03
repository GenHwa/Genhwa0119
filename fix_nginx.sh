#!/bin/bash
# 在服务器上运行此脚本配置 Nginx
# 用法: bash fix_nginx.sh

sudo tee /etc/nginx/sites-available/genhwa.conf << 'EOF'
server {
    listen 80;
    server_name genhwa.online;

    # 前端静态文件
    location / {
        root /home/ubuntu/Genhwa0119/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 代理到后端
    location /api/ {
        proxy_pass http://127.0.0.1:520;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 上传文件代理到后端
    location /uploads/ {
        proxy_pass http://127.0.0.1:520;
    }
}
EOF

# 启用配置
sudo ln -sf /etc/nginx/sites-available/genhwa.conf /etc/nginx/sites-enabled/genhwa.conf

# 删除默认配置避免冲突
sudo rm -f /etc/nginx/sites-enabled/default

# 测试并重启
sudo nginx -t && sudo systemctl restart nginx
echo "Nginx 配置完成！"
