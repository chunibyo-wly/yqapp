from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait

if __name__ == "__main__":
    # 创建chrome启动选项
    chrome_options = webdriver.ChromeOptions()

    # 指定chrome启动类型为headless 并且禁用gpu
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=chrome_options)

    wait = WebDriverWait(driver, timeout=10)
    driver.get(
        r'http://rsfw.cug.edu.cn/amp-auth-adapter/login?service=http://yqapp.cug.edu.cn/xsfw/sys/swmxsyqxxsjapp/*default/index.do')
    driver.quit()
