FROM python:3.10-slim

# Cài đặt Chrome và các gói phụ thuộc
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /app

# Sao chép requirements trước để tận dụng cache
COPY requirements.txt .

# Cài đặt các gói Python
RUN pip install --no-cache-dir -r requirements.txt flask

# Sao chép mã nguồn
COPY . .

# Expose port 10000 để Render có thể phát hiện
EXPOSE 10000

# Chạy server Flask
CMD ["python", "server.py"]