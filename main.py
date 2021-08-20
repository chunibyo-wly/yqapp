import io
import pytesseract
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait


class yqapp:
    def __init__(self):
        # 第三方登录页面
        self.login_url = r"http://rsfw.cug.edu.cn/amp-auth-adapter/login?service=http://yqapp.cug.edu.cn/xsfw/sys/swmxsyqxxsjapp/*default/index.do"
        self.captcha_url = r"http://sfrz.cug.edu.cn/tpass/code"

        # 创建chrome启动选项
        self.chrome_options = webdriver.ChromeOptions()
        # 指定chrome启动类型为headless 并且禁用gpu
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=self.chrome_options)

        self.cookies = ""

    def login(self):
        wait = WebDriverWait(self.driver, timeout=10)
        self.driver.get(self.login_url)

        self.cookies = self.driver.get_cookies()
        captcha = self._get_captcha()
        print(captcha)

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
    yq = yqapp()
    yq.login()


if __name__ == "__main__":
    main()
