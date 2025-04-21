import time
import logging
from selenium import webdriver
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

def setup_driver():
    """Khởi tạo trình duyệt Chrome headless"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')  # Màn hình lớn để dễ thao tác
    
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
        
        # Điền thông tin đăng nhập
        logger.info("Điền thông tin đăng nhập...")
        # Sử dụng ID chính xác cho các trường đăng nhập
        email_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')
        
        email_input.clear()
        email_input.send_keys(USERNAME)
        
        password_input.clear()
        password_input.send_keys(PASSWORD)
        
        # Click nút đăng nhập trong form
        logger.info("Click nút đăng nhập...")
        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Đợi đăng nhập hoàn tất
        time.sleep(3)
        
        # BƯỚC 2: Click vào nút "Bình chọn" đầu tiên
        logger.info("Đang tìm và click vào nút 'Bình chọn' đầu tiên...")
        first_vote_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.bg-support-primary.text-support-secondary'))
        )
        first_vote_button.click()
        
        # Đợi một chút để UI cập nhật
        time.sleep(2)
        
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
        
    except TimeoutException:
        logger.error("Timeout - không thể tìm thấy phần tử trong thời gian chờ")
    except NoSuchElementException as e:
        logger.error(f"Không tìm thấy phần tử yêu cầu: {str(e)}")
    except Exception as e:
        logger.error(f"Lỗi không mong muốn: {str(e)}")
    finally:
        if driver:
            driver.quit()
            logger.info("Đã đóng trình duyệt")

def main():
    """Hàm chính để chạy bot liên tục"""
    logger.info("Khởi động bot bình chọn tự động")
    
    try:
        while True:
            vote_process()
            
            # Tính toán thời gian chờ đến phút tiếp theo
            next_run = 60  # Một phút
            logger.info(f"Hoàn thành! Đợi {next_run} giây cho lần chạy tiếp theo...")
            time.sleep(next_run)
            
    except KeyboardInterrupt:
        logger.info("Bot đã dừng bởi người dùng")
    except Exception as e:
        logger.error(f"Lỗi không mong muốn trong vòng lặp chính: {str(e)}")

if __name__ == "__main__":
    main()