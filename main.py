import io
import sys
import time

import pytesseract
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class yqapp:
    def __init__(self, username, password):
        self.username = username
        self.password = password

        # 第三方登录页面
        self.login_url = r"http://rsfw.cug.edu.cn/amp-auth-adapter/login?service=http://yqapp.cug.edu.cn/xsfw/sys/swmxsyqxxsjapp/*default/index.do"
        self.captcha_url = r"http://sfrz.cug.edu.cn/tpass/code"

        # 创建chrome启动选项
        self.chrome_options = webdriver.ChromeOptions()
        # 指定chrome启动类型为headless 并且禁用gpu
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--incognito')
        self.driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, timeout=10)

        self.cookies = ""
        self.screenshot_number = 0

    def screenshot(self):
        self.screenshot_number = self.screenshot_number + 1
        self.driver.save_screenshot('screenshot{}.png'.format(self.screenshot_number))

    def login(self):
        self.driver.get(self.login_url)
        self.driver.maximize_window()
        self.screenshot()

        self.cookies = self.driver.get_cookies()
        captcha = self._get_captcha()
        print(captcha)

        self.driver.find_element_by_id('un').send_keys(self.username)
        self.driver.find_element_by_id('pd').send_keys(self.password)
        # send keys 默认具有回车事件，网页自动提交了表单，所以寻找按钮是永远找不到的
        self.driver.find_element_by_id('code').send_keys(captcha)
        # self.driver.find_element_by_id('index_login_btn').click()

    def check_login(self):
        self.driver.implicitly_wait(60)
        try:
            element = self.driver.find_element_by_id('errormsg')
        except Exception:
            return True

        if element.is_displayed():
            return False
        else:
            return True

    def clock_in(self):
        self.driver.implicitly_wait(60)
        self.wait.until(
            EC.text_to_be_present_in_element((By.ID, 'app'), '每日打卡')
        )
        self.screenshot()

        # 早上
        self.driver.find_element(By.CSS_SELECTOR, ".sdys_div:nth-child(2)").click()

        # Step 1: 本人健康状态
        element = (By.XPATH, "//a[contains(.,'本人健康状态')]")
        self.wait.until(EC.presence_of_element_located(element))
        self.driver.find_element(*element).click()

        element = (By.XPATH, "//div[@class='emapm-item'][2]//label[contains(.,'正常')]")
        self.wait.until(EC.presence_of_element_located(element))
        self.driver.find_element(*element).click()

        element = (By.XPATH, "//div[@class='emapm-item'][2]//button[contains(.,'返回')]")
        try:
            self.driver.find_element(*element).click()
        except Exception:
            pass
        # Step 1: 本人健康状态

        # Step 2: 体温
        element = (By.XPATH, "//a[contains(.,'体温')]")
        self.wait.until(EC.presence_of_element_located(element))
        self.driver.find_element(*element).click()

        element = (By.XPATH, "//div[@class='emapm-item'][3]//label[contains(.,'否')]")
        self.wait.until(EC.presence_of_element_located(element))
        self.driver.find_element(*element).click()

        element = (By.XPATH, "//div[@class='emapm-item'][3]//button[contains(.,'返回')]")
        try:
            self.driver.find_element(*element).click()
        except Exception:
            pass
        # Step 2: 体温

        # Step 3: 家庭成员
        element = (By.XPATH, "//a[contains(.,'家庭成员')]")
        self.wait.until(EC.presence_of_element_located(element))
        self.driver.find_element(*element).click()

        element = (By.XPATH, "//div[@class='emapm-item'][6]//label[contains(.,'正常')]")
        self.wait.until(EC.presence_of_element_located(element))
        self.driver.find_element(*element).click()

        element = (By.XPATH, "//div[@class='emapm-item'][6]//button[contains(.,'返回')]")
        try:
            self.driver.find_element(*element).click()
        except Exception:
            pass
        # Step 3: 家庭成员

        # Step 4: 心理状况
        element = (By.XPATH, "//a[contains(.,'心理状况')]")
        self.wait.until(EC.presence_of_element_located(element))
        self.driver.find_element(*element).click()

        element = (By.XPATH, "//div[@class='emapm-item'][7]//label[contains(.,'无')]")
        self.wait.until(EC.presence_of_element_located(element))
        self.driver.find_element(*element).click()

        element = (By.XPATH, "//div[@class='emapm-item'][7]//button[contains(.,'返回')]")
        try:
            self.driver.find_element(*element).click()
        except Exception:
            pass
        # Step 4: 心理状况

        time.sleep(60)

    def _get_captcha(self):
        # 在同一个session内刷新验证码，使其可以被request捕获
        session_id = ""

        for cookie in self.cookies:
            if 'name' in cookie and cookie['name'] == 'JSESSIONID':
                session_id = cookie['value']
                break

        print(session_id)
        headers = {
            'Cookie': 'JSESSIONID={};'.format(session_id)
        }
        sess = requests.Session()
        sess.headers.update(headers)
        content = sess.get(url=self.captcha_url).content
        sess.close()
        return self._ocr(content)

    def _add_margin(self, pil_img, top, right, bottom, left, color):
        width, height = pil_img.size
        new_width = width + right + left
        new_height = height + top + bottom
        result = Image.new('RGBA', (new_width, new_height), color)
        result.paste(pil_img, (left, top))
        return result

    def _ocr(self, content):
        """
        OCR Engine modes:
        　　　　0 Legacy engine only.
        　　　　1 Neural nets LSTM engine only.
        　　　　2 Legacy + LSTM engines.
        　　　　3 Default, based on what is available.

        Page segmentation modes:
        　　　　0 Orientation and script detection (OSD) only.
        　　　　1 Automatic page segmentation with OSD.
        　　　　2 Automatic page segmentation, but no OSD, or OCR.
        　　　　3 Fully automatic page segmentation, but no OSD. (Default)
        　　　　4 Assume a single column of text of variable sizes.
        　　　　5 Assume a single uniform block of vertically aligned text.
        　　　　6 Assume a single uniform block of text.
        　　　　7 Treat the image as a single text line.
        　　　　8 Treat the image as a single word.
        　　　　9 Treat the image as a single word in a circle.
        　　　　10 Treat the image as a single character.
        　　　　11 Sparse text. Find as much text as possible in no particular order.
        　　　　12 Sparse text with OSD.
        　　　　13 Raw line. Treat the image as a single text line,
        　　　　 bypassing hacks that are Tesseract-specific.
        """

        im = Image.open(io.BytesIO(content))
        threshold = 230
        # gif 验证码，第一张具有所有信息
        im.seek(im.tell() + 1)
        # 二值化并且增加 padding 使识别更准确
        bi_im = im.convert("L").point(lambda p: p > threshold and 255)
        bi_im = self._add_margin(bi_im, 0, 0, 0, int(bi_im.size[0] * 0.1), (255, 255, 255))
        bi_im.save("temp.png")
        result = pytesseract.image_to_string(bi_im,
                                             config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')

        return result

    def close(self):
        self.driver.quit()


def main():
    yq = yqapp(sys.argv[1], sys.argv[2])

    yq.login()
    if not yq.check_login():
        yq.login()
        if not yq.check_login():
            exit(-1)

    yq.clock_in()
    yq.close()


if __name__ == "__main__":
    main()
