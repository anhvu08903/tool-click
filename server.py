import os
import time
import threading
import logging
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Thông tin đăng nhập cố định
USERNAME = "ngocanhvu8903@gmail.com"
PASSWORD = "Izone@2025"

# Cổng cho Flask app
PORT = int(os.environ.get("PORT", 10000))

# Tạo Flask app
app = Flask(__name__)

# Biến toàn cục để lưu trạng thái
vote_status = {
    "running": False,
    "last_vote_time": None,
    "vote_count": 0,
    "errors": []
}

def setup_driver():
    """Khởi tạo trình duyệt Chrome headless"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    # Sử dụng Chrome có sẵn trên hệ thống
    options.binary_location = "/usr/bin/google-chrome"
    
    return webdriver.Chrome(options=options)

def vote_process():
    """Thực hiện quy trình bình chọn đầy đủ"""
    driver = None
    try:
        logger.info("Bắt đầu phiên bình chọn mới")
        driver = setup_driver()
        
        # Truy cập trang web bình chọn
        logger.info("Đang truy cập trang web...")
        driver.get("https://momentum.izone.edu.vn/#vote-gallery")
        
        # Đợi trang web tải xong
        logger.info("Đợi trang web tải xong...")
        wait = WebDriverWait(driver, 30)
        
        # BƯỚC 1: Click vào nút "Đăng nhập"
        logger.info("Đang tìm và click vào nút 'Đăng nhập'...")
        login_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.text-support-primary.bg-support-secondary'))
        )
        login_button.click()
        
        # Đợi form đăng nhập xuất hiện
        logger.info("Đợi form đăng nhập xuất hiện...")
        wait.until(EC.presence_of_element_located((By.ID, 'username')))
        
        # Lấy screenshot để debug
        driver.save_screenshot('/tmp/form_login.png')
        logger.info("Đã lưu screenshot tại /tmp/form_login.png")
        
        # Điền thông tin đăng nhập
        logger.info("Điền thông tin đăng nhập...")
        email_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')
        
        email_input.clear()
        email_input.send_keys(USERNAME)
        
        password_input.clear()
        password_input.send_keys(PASSWORD)
        
        # Click nút đăng nhập trong form
        logger.info("Click nút đăng nhập...")
        # Thử nhiều cách khác nhau để tìm nút đăng nhập
        try:
            # Cách 1: Tìm theo type
            submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            logger.info("Đã tìm và click nút đăng nhập bằng selector button[type='submit']")
        except:
            try:
                # Cách 2: Tìm theo text
                submit_button = driver.find_element(By.XPATH, '//button[contains(text(), "Đăng nhập")]')
                submit_button.click()
                logger.info("Đã tìm và click nút đăng nhập bằng text 'Đăng nhập'")
            except:
                try:
                    # Cách 3: Tìm theo vị trí tương đối
                    submit_button = driver.find_element(By.XPATH, '//form//button')
                    submit_button.click()
                    logger.info("Đã tìm và click nút đăng nhập bằng vị trí //form//button")
                except:
                    # Cách 4: Tìm tất cả các button và click button cuối cùng trong form
                    buttons = driver.find_elements(By.TAG_NAME, 'button')
                    if buttons:
                        buttons[-1].click()
                        logger.info("Đã tìm và click button cuối cùng trong danh sách buttons")
                    else:
                        logger.error("Không thể tìm thấy nút đăng nhập nào!")
        
        # Đợi đăng nhập hoàn tất
        time.sleep(3)
        
        # BƯỚC 2: Click vào nút "Bình chọn" đầu tiên
        logger.info("Đang tìm và click vào nút 'Bình chọn' đầu tiên...")
        first_vote_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.bg-support-primary.text-support-secondary'))
        )
        first_vote_button.click()
        
        # Đợi một chút để UI cập nhật
        time.sleep(5)  # Tăng thời gian chờ lên 5 giây
        
        # BƯỚC 3: Tìm và click vào ảnh mục tiêu
        logger.info("Tìm ảnh mục tiêu, đang click...")
        target_image = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'img[src="/storage/IC1713.JPG"]'))
        )
        target_image.click()
        
        # Đợi một chút để UI cập nhật
        time.sleep(2)
        
        # BƯỚC 4: Click vào nút "Bình chọn ngay"
        logger.info("Đang click vào nút bình chọn ngay...")
        final_vote_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.bg-support-secondary'))
        )
        final_vote_button.click()
        
        # Đợi để đảm bảo request hoàn thành
        time.sleep(3)
        
        logger.info("Bình chọn thành công!")
        
        # Cập nhật trạng thái
        vote_status["last_vote_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        vote_status["vote_count"] += 1
        
        return True
        
    except TimeoutException as e:
        error_msg = f"Timeout - không thể tìm thấy phần tử trong thời gian chờ: {str(e)}"
        logger.error(error_msg)
        vote_status["errors"].append(error_msg)
        return False
    except NoSuchElementException as e:
        error_msg = f"Không tìm thấy phần tử yêu cầu: {str(e)}"
        logger.error(error_msg)
        vote_status["errors"].append(error_msg)
        return False
    except Exception as e:
        error_msg = f"Lỗi không mong muốn: {str(e)}"
        logger.error(error_msg)
        vote_status["errors"].append(error_msg)
        return False
    finally:
        if driver:
            driver.quit()
            logger.info("Đã đóng trình duyệt")

def vote_scheduler():
    """Hàm lập lịch cho quá trình bình chọn"""
    vote_status["running"] = True
    
    while vote_status["running"]:
        try:
            vote_process()
            logger.info(f"Đợi 60 giây cho lần chạy tiếp theo...")
            time.sleep(60)  # Đợi 1 phút
        except Exception as e:
            logger.error(f"Lỗi trong vòng lặp lập lịch: {str(e)}")
            vote_status["errors"].append(f"Scheduler error: {str(e)}")
            time.sleep(10)  # Đợi một chút nếu có lỗi

# API endpoints
@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "message": "Auto Vote Bot is running"
    })

@app.route('/status')
def status():
    return jsonify(vote_status)

@app.route('/start')
def start():
    if not vote_status["running"]:
        # Khởi động thread mới nếu chưa chạy
        vote_thread = threading.Thread(target=vote_scheduler)
        vote_thread.daemon = True
        vote_thread.start()
        return jsonify({"status": "started"})
    return jsonify({"status": "already running"})

@app.route('/stop')
def stop():
    vote_status["running"] = False
    return jsonify({"status": "stopped"})

if __name__ == "__main__":
    # Khởi động thread bình chọn
    vote_thread = threading.Thread(target=vote_scheduler)
    vote_thread.daemon = True
    vote_thread.start()
    
    # Khởi động server Flask
    app.run(host='0.0.0.0', port=PORT)