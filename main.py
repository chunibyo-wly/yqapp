from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait


class yqapp:
    def __init__(self):
        # 第三方登录页面
        self.login_url = r"http://rsfw.cug.edu.cn/amp-auth-adapter/login?service=http://yqapp.cug.edu.cn/xsfw/sys/swmxsyqxxsjapp/*default/index.do"

        # 创建chrome启动选项
        self.chrome_options = webdriver.ChromeOptions()
        # 指定chrome启动类型为headless 并且禁用gpu
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=self.chrome_options)

    def login(self):
        wait = WebDriverWait(self.driver, timeout=10)
        self.driver.get(self.login_url)

        print(self.driver.get_cookies())

    def close(self):
        self.driver.quit()


def main():
    yq = yqapp()
    yq.login()


if __name__ == "__main__":
    main()
