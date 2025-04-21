import os
import time
import threading
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from flask import Flask, jsonify

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Thông tin đăng nhập cố định
USERNAME = "ngocanhvu8903@gmail.com"
PASSWORD = "Izone@2025"

# URL cơ bản
BASE_URL = "https://momentum.izone.edu.vn"

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
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')  # Màn hình lớn để dễ thao tác
    options.add_argument('--disable-blink-features=AutomationControlled')  # Giảm khả năng phát hiện automation
    
    # Sử dụng Chrome có sẵn trong hệ thống
    options.binary_location = "/usr/bin/google-chrome"
    
    return webdriver.Chrome(options=options)

def wait_and_click(driver, selector, by=By.CSS_SELECTOR, timeout=30, description="element"):
    """Đợi element xuất hiện và click vào nó, với xử lý lỗi tốt hơn"""
    try:
        logger.info(f"Đang tìm và click vào {description}...")
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        # Cuộn đến element trước khi click
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)  # Đợi để cuộn xong
        element.click()
        logger.info(f"Đã click vào {description}")
        return True
    except TimeoutException:
        logger.error(f"Timeout - không thể tìm thấy {description} trong {timeout} giây")
        return False
    except Exception as e:
        logger.error(f"Lỗi khi tìm/click vào {description}: {str(e)}")
        return False

def vote_process():
    """Thực hiện quy trình bình chọn đầy đủ"""
    driver = None
    try:
        logger.info("Bắt đầu phiên bình chọn mới")
        driver = setup_driver()
        driver.get(BASE_URL)
        
        # BƯỚC 1: Click vào nút "Đăng nhập"
        login_button_found = wait_and_click(
            driver, 
            "button.text-support-primary.bg-support-secondary", 
            description="nút Đăng nhập"
        )
        
        if not login_button_found:
            # Thử cách khác nếu không tìm thấy theo class
            buttons = driver.find_elements(By.TAG_NAME, "button")
            login_clicked = False
            for button in buttons:
                if "Đăng nhập" in button.text:
                    button.click()
                    login_clicked = True
                    logger.info("Đã click vào nút Đăng nhập bằng text")
                    break
            
            if not login_clicked:
                logger.error("Không thể tìm thấy nút Đăng nhập!")
                driver.save_screenshot('/tmp/login_button_not_found.png')
                logger.info("Đã lưu screenshot tại /tmp/login_button_not_found.png")
                vote_status["errors"].append("Không tìm thấy nút Đăng nhập")
                return False
        
        # BƯỚC 2: Đợi form đăng nhập hiện ra
        logger.info("Đợi form đăng nhập hiện ra...")
        username_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        
        # Lưu screenshot để debug
        driver.save_screenshot('/tmp/login_form.png')
        logger.info("Đã lưu screenshot form đăng nhập tại /tmp/login_form.png")
        
        # BƯỚC 3: Điền thông tin đăng nhập
        logger.info("Điền thông tin đăng nhập...")
        
        # Tìm trường username và password
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        
        # Xóa nội dung cũ (nếu có) và điền thông tin mới
        username_input.clear()
        username_input.send_keys(USERNAME)
        
        password_input.clear()
        password_input.send_keys(PASSWORD)
        
        # BƯỚC 4: Click nút đăng nhập
        logger.info("Click nút đăng nhập trong form...")
        
        # Tìm nút submit bằng nhiều cách
        try:
            # Cách 1: Tìm theo ID
            submit_button = driver.find_element(By.ID, "kc-login")
            submit_button.click()
            logger.info("Đã click nút đăng nhập bằng ID")
        except NoSuchElementException:
            try:
                # Cách 2: Tìm theo tag input[type="submit"]
                submit_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
                submit_button.click()
                logger.info("Đã click nút đăng nhập bằng input[type='submit']")
            except NoSuchElementException:
                try:
                    # Cách 3: Tìm theo text
                    submit_button = driver.find_element(By.XPATH, '//button[contains(text(), "Đăng nhập")]')
                    submit_button.click()
                    logger.info("Đã click nút đăng nhập bằng text 'Đăng nhập'")
                except NoSuchElementException:
                    # Cách 4: Submit form trực tiếp
                    form = driver.find_element(By.ID, "kc-form-login")
                    form.submit()
                    logger.info("Đã submit form đăng nhập trực tiếp")
        
        # Đợi đăng nhập hoàn tất và chuyển về trang chủ
        logger.info("Đợi đăng nhập hoàn tất...")
        time.sleep(5)
        
        # Kiểm tra đăng nhập thành công hay không
        if "Sai tên người dùng hoặc mật khẩu" in driver.page_source:
            logger.error("Đăng nhập thất bại: Sai tên người dùng hoặc mật khẩu")
            vote_status["errors"].append("Sai thông tin đăng nhập")
            return False
        
        # BƯỚC 5: Chuyển đến trang bình chọn
        logger.info("Truy cập trang bình chọn...")
        driver.get(f"{BASE_URL}/#vote-gallery")
        time.sleep(3)  # Đợi trang load xong
        
        # BƯỚC 6: Click vào nút "Bình chọn" đầu tiên
        bình_chọn_button_found = wait_and_click(
            driver,
            "button.text-support-secondary.bg-support-primary",
            description="nút Bình chọn đầu tiên"
        )
        
        if not bình_chọn_button_found:
            # Thử tìm nút bằng text
            buttons = driver.find_elements(By.TAG_NAME, "button")
            bình_chọn_clicked = False
            for button in buttons:
                if "Bình chọn" in button.text and "ngay" not in button.text.lower():
                    button.click()
                    bình_chọn_clicked = True
                    logger.info("Đã click vào nút Bình chọn đầu tiên bằng text")
                    break
            
            if not bình_chọn_clicked:
                logger.error("Không thể tìm thấy nút Bình chọn đầu tiên!")
                driver.save_screenshot('/tmp/vote_button_not_found.png')
                logger.info("Đã lưu screenshot tại /tmp/vote_button_not_found.png")
                vote_status["errors"].append("Không tìm thấy nút Bình chọn đầu tiên")
                return False
        
        # Đợi để trang cập nhật sau khi click
        time.sleep(3)
        
        # BƯỚC 7: Tìm và click vào ảnh mục tiêu
        logger.info("Tìm ảnh mục tiêu (IC1713.JPG)...")
        
        # Lưu screenshot trước khi tìm ảnh
        driver.save_screenshot('/tmp/before_image_click.png')
        
        # Tìm ảnh bằng nhiều cách
        try:
            target_image = driver.find_element(By.CSS_SELECTOR, 'img[src="/storage/IC1713.JPG"]')
            # Cuộn đến ảnh
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_image)
            time.sleep(1)  # Đợi cuộn xong
            
            # Click vào ảnh
            target_image.click()
            logger.info("Đã click vào ảnh mục tiêu")
        except NoSuchElementException:
            # Thử tìm bằng partial match
            try:
                target_image = driver.find_element(By.XPATH, '//img[contains(@src, "IC1713.JPG")]')
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_image)
                time.sleep(1)
                target_image.click()
                logger.info("Đã click vào ảnh mục tiêu (partial match)")
            except NoSuchElementException:
                logger.error("Không tìm thấy ảnh mục tiêu!")
                driver.save_screenshot('/tmp/image_not_found.png')
                logger.info("Đã lưu screenshot tại /tmp/image_not_found.png")
                vote_status["errors"].append("Không tìm thấy ảnh mục tiêu")
                return False
        
        # Đợi sau khi click vào ảnh
        time.sleep(2)
        
        # BƯỚC 8: Tìm và click vào nút "Bình chọn ngay"
        logger.info("Tìm nút Bình chọn ngay...")
        
        # Lưu screenshot trước khi tìm nút Bình chọn ngay
        driver.save_screenshot('/tmp/before_final_vote.png')
        
        # Cuộn xuống để tìm nút
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(1)
        
        bình_chọn_ngay_found = wait_and_click(
            driver,
            "button.text-support-primary.bg-support-secondary",
            description="nút Bình chọn ngay",
            timeout=10
        )
        
        if not bình_chọn_ngay_found:
            # Thử tìm nút bằng text
            buttons = driver.find_elements(By.TAG_NAME, "button")
            final_clicked = False
            
            for button in buttons:
                text = button.text.lower()
                if "bình" in text and "chọn" in text and "ngay" in text:
                    # Cuộn đến nút
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(1)
                    button.click()
                    final_clicked = True
                    logger.info("Đã click vào nút Bình chọn ngay bằng text")
                    break
            
            if not final_clicked:
                logger.error("Không thể tìm thấy nút Bình chọn ngay!")
                driver.save_screenshot('/tmp/final_button_not_found.png')
                logger.info("Đã lưu screenshot tại /tmp/final_button_not_found.png")
                vote_status["errors"].append("Không tìm thấy nút Bình chọn ngay")
                return False
        
        # Đợi để gửi request hoàn tất
        time.sleep(5)
        
        # Lưu screenshot kết quả
        driver.save_screenshot('/tmp/vote_result.png')
        
        logger.info("Bình chọn thành công!")
        vote_status["last_vote_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        vote_status["vote_count"] += 1
        return True
        
    except Exception as e:
        error_msg = f"Lỗi không mong muốn: {str(e)}"
        logger.error(error_msg)
        if driver:
            driver.save_screenshot('/tmp/error_screenshot.png')
            logger.info("Đã lưu screenshot lỗi tại /tmp/error_screenshot.png")
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
            result = vote_process()
            if result:
                logger.info(f"Bình chọn thành công. Đợi 60 giây cho lần chạy tiếp theo...")
            else:
                logger.warning(f"Bình chọn thất bại. Đợi 60 giây và thử lại...")
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
        "message": "Auto Vote Bot is running",
        "vote_count": vote_status["vote_count"],
        "last_vote": vote_status["last_vote_time"]
    })

@app.route('/status')
def status():
    # Chỉ giữ 10 lỗi gần nhất
    vote_status["errors"] = vote_status["errors"][-10:] if len(vote_status["errors"]) > 10 else vote_status["errors"]
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

@app.route('/test')
def test_vote():
    """Endpoint để test quá trình vote một lần"""
    result = vote_process()
    return jsonify({
        "success": result,
        "status": vote_status
    })

if __name__ == "__main__":
    # Khởi động thread bình chọn
    vote_thread = threading.Thread(target=vote_scheduler)
    vote_thread.daemon = True
    vote_thread.start()
    
    # Khởi động server Flask
    app.run(host='0.0.0.0', port=PORT)