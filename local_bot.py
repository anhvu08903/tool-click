import time
import logging
from selenium import webdriver
import undetected_chromedriver as uc
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

# URL cơ bản
BASE_URL = "https://momentum.izone.edu.vn"

def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument('--start-maximized')
    return uc.Chrome(options=options)

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
                return False
        
        # BƯỚC 2: Đợi form đăng nhập hiện ra
        logger.info("Đợi form đăng nhập hiện ra...")
        username_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        
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
                return False
        
        # Đợi để trang cập nhật sau khi click
        time.sleep(3)
        
        # BƯỚC 7: Tìm và click vào ảnh mục tiêu
        logger.info("Tìm ảnh mục tiêu (IC1713.JPG)...")
        
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
                return False
        
        # Đợi sau khi click vào ảnh
        time.sleep(2)
        
        # BƯỚC 8: Tìm và click vào nút "Bình chọn ngay"
        logger.info("Tìm nút Bình chọn ngay...")
        import pyautogui

        # Click thủ công bằng pyautogui nếu Selenium không bấm được nút
        logger.info("Click nút Bình chọn ngay bằng pyautogui...")
        time.sleep(1)  # Đợi trang load

        # Di chuyển chuột đến nút và click
    

        
        # Cuộn xuống để tìm nút
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(1)
        
        bình_chọn_ngay_found = wait_and_click(
            driver,
            "button.text-support-primary.bg-support-secondary",
            description="Bình chọn ngay",
            timeout=10
        )
        
        if not bình_chọn_ngay_found:
            # Thử tìm nút bằng text
            buttons = driver.find_elements(By.TAG_NAME, "button")
            final_clicked = False
            
            for button in buttons:
                text = button.text.strip().lower()
                # Ghép lại text nếu bị xuống dòng và kiểm tra bằng regex
                clean_text = re.sub(r'\s+', ' ', text)
                if re.search(r'bình chọn ngay', clean_text):
                    try:
                       driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                       time.sleep(1)
                       driver.execute_script("arguments[0].click();", button)
                       logger.info(f"Đã click vào nút Bình chọn ngay bằng JS: '{clean_text}'")
                       final_clicked = True
                       break
                    except Exception as e:
                       logger.error(f"Lỗi khi click nút Bình chọn ngay: {e}")
            
            if not final_clicked:
                logger.error("Không thể tìm thấy nút Bình chọn ngay!")
                return False
        
        pyautogui.moveTo(950, 900, duration=1)
        pyautogui.click()
        logger.info("Đã click vào nút Bình chọn ngay bằng pyautogui")
        # Đợi để gửi request hoàn tất
        time.sleep(5)
        
        logger.info("Bình chọn thành công!")
        return True
        
    except Exception as e:
        error_msg = f"Lỗi không mong muốn: {str(e)}"
        logger.error(error_msg)
        return False
        
    finally:
        if driver:
            # Không đóng trình duyệt để bạn có thể xem kết quả
            # Nếu muốn tự động đóng trình duyệt sau khi hoàn thành, hãy bỏ comment dòng dưới
            driver.quit()
            pass

def main():
    """Hàm chính để chạy bot liên tục"""
    logger.info("Khởi động bot bình chọn tự động")
    
    try:
        while True:
            result = vote_process()
            if result:
                logger.info(f"Bình chọn thành công. Đợi 60 giây cho lần chạy tiếp theo...")
            else:
                logger.warning(f"Bình chọn thất bại. Đợi 60 giây và thử lại...")
            time.sleep(40)  # Đợi 1 phút
            
    except KeyboardInterrupt:
        logger.info("Bot đã dừng bởi người dùng")
    except Exception as e:
        logger.error(f"Lỗi không mong muốn trong vòng lặp chính: {str(e)}")

if __name__ == "__main__":
    main()