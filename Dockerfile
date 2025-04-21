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
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn
COPY . .

# Thêm script để tự động tải ChromeDriver phù hợp
RUN echo '#!/bin/bash \n\
CHROME_VERSION=$(google-chrome --version | cut -d " " -f 3 | cut -d "." -f 1) \n\
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION") \n\
wget -q -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" \n\
unzip -o /tmp/chromedriver.zip -d /usr/local/bin/ \n\
rm /tmp/chromedriver.zip \n\
chmod +x /usr/local/bin/chromedriver \n\
python app.py' > /app/start.sh && chmod +x /app/start.sh

# Sử dụng webdriver-manager để tự động tải ChromeDriver phù hợp
RUN pip install webdriver-manager

# Chạy script khởi động
CMD ["/bin/bash", "/app/start.sh"]