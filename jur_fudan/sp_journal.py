import base64
import os
import random
import re
import cv2
import pyautogui
import pyperclip
import requests
from browsermobproxy import Server
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from seleniumwire.undetected_chromedriver import ChromeOptions, Chrome, webdriver
import time
import tool
import numpy as np
from cropper import TransparentCropper
from matplotlib import pyplot as plt

det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False )
plt.rcParams['font.sans-serif']=['SimHei']    # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False
data_look = []

def move_distance():
    picture_loc = driver.find_element(By.CSS_SELECTOR, '#aliyunCaptcha-puzzle').get_attribute('style')
    slider_loc = driver.find_element(By.CSS_SELECTOR, '#aliyunCaptcha-sliding-slider').get_attribute('style')

    picture_float = re.findall('left: (.*)px;',picture_loc)
    slider_int = re.findall('left: (.*)px;',slider_loc)
    p_f = 0.0
    s_i = 0
    if picture_float:
        p_f = float(picture_float[0])
    if slider_int:
        s_i = int(slider_int[0])
    return [p_f, s_i]

def sqrt_func(y):
    data = tool.read_json('..\\move.json')
    res = 261
    res1 = 0
    for i in data:
        if res > abs(i[0] - y):
            res = abs(i[0] - y)
            res1 = i[1]
    return res1

def download_image(image_url, save_path):
    """
    下载图片并保存到指定路径
    :param image_url: 图片的URL
    :param save_path: 图片保存的路径（包括文件名）
    :return: 如果下载成功返回 True，否则返回 False
    """
    try:
        # 发送 HTTP 请求下载图片
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            # 确保保存路径的目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            # 保存图片
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"图片已保存到：{save_path}")
            return True
        else:
            print(f"图片下载失败，状态码：{response.status_code}")
            return False
    except Exception as e:
        print(f"下载图片时发生错误：{e}")
        return False

# 保存滑块和背景到本地
def save_image():
    bigImage = driver.find_element(By.CSS_SELECTOR,'#aliyunCaptcha-img')
    bigImg = bigImage.get_attribute("src")  # 获取图片的style属性
    if bigImg.startswith('http'):
        if  download_image(bigImg,'.\\bigImage.png') == True:
            print('下载成功')
    # bs64模式
    elif bigImg.startswith('data:image/png;base64'):
        bigImg = bigImg + '结束了'
        bImg_base64 = re.findall('data:image/png;base64,(.*?)结束了', bigImg, re.S | re.I)[0]
        bImgdata = base64.b64decode(bImg_base64)

        # 将图片保存为文件
        with open("bigImage.png", 'wb') as f:
            f.write(bImgdata)
    smallImage = driver.find_element(By.CSS_SELECTOR,
                                     '#aliyunCaptcha-puzzle')

    smallImg = smallImage.get_attribute("src")  # 获取图片的style属性
    if smallImg.startswith('http'):
        if download_image(smallImg, '.\\smallImage.png') == True:
            print('下载成功')
    elif smallImg.startswith('data:image/png;base64'):
        # bs64模式
        smallImg = smallImg + '结束了'
        sImg_base64 = re.findall('data:image/png;base64,(.*?)结束了', smallImg, re.S | re.I)[0]
        sImgdata = base64.b64decode(sImg_base64)

        # 将图片保存为文件
        with open("smallImage.png", 'wb') as f:
            f.write(sImgdata)

    cropper = TransparentCropper("smallImage.png")
    cropper.opencv_crop("smallImage.png")

def driver_start():
    print(1)
    server = Server(
        r'..\browsermob-proxy-2.1.4\bin\browsermob-proxy.bat')
    server.start()
    proxy = server.create_proxy(params={'trustAllServers': 'true'})
    seleniumwire_options = {
        'proxy': {
            'http': f'http://{proxy.proxy}',  # user:pass@ip:port
            'https': f'http://{proxy.proxy}',
            'no_proxy': 'localhost,127.0.0.1'
        }
    }
    download_dir = r'C:\Users\Administrator\Downloads\chrome'
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": True,  # 不弹出对话框
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False
    }
    print(2)
    options = {}
    chrome_options = ChromeOptions()
    chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_argument("--ignore-ssl-errors=yes")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--no-service-autorun')
    chrome_options.add_argument('--no-default-browser-check')
    chrome_options.add_argument('--password-store=basic')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-web-security')
    # chrome_options.add_experimental_option('detach', True)
    driver = Chrome(seleniumwire_options=seleniumwire_options, options=chrome_options)
    driver.implicitly_wait(150)
    driver.set_page_load_timeout(30)
    driver.maximize_window()
    driver.get(f'http://www.baidu.com/')
    time.sleep(1)
    driver.get('https://fsso.cnki.net/')

    element = driver.find_element(By.CSS_SELECTOR, '#o')
    element.send_keys('东华大学')
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR,
                        'body > div.main > div.submit_div > div.submit_input > div.submit_button').click()
    time.sleep(5)
    element = driver.find_element(By.CSS_SELECTOR, '#username')
    element.send_keys('1239703')
    time.sleep(1)
    print('输入账号')
    element = driver.find_element(By.CSS_SELECTOR, '#password')
    element.send_keys('Haodaoxin335')
    time.sleep(1)
    print('输入密码')
    driver.find_element(By.CSS_SELECTOR,
                        'body > div > div > div > div.column.one > form > div:nth-child(6) > button').click()
    time.sleep(3)
    driver.find_element(By.CSS_SELECTOR, '#generalConsentDiv > p:nth-child(1) > label').click()
    time.sleep(3)
    driver.find_element(By.CSS_SELECTOR,
                        'body > form > div > div:nth-child(5) > p:nth-child(3) > input:nth-child(2)').click()
    time.sleep(10)
    print('success log in')
    return driver

def mouse_move(driver: webdriver.Chrome):
    element = driver.find_element(By.CSS_SELECTOR,'#verify_pic > div.verify-bar-area > div > div > div')
    soup = BeautifulSoup(driver.page_source, 'lxml')
    move_size = soup.select('#verify_pic > div.verify-bar-area > div > div > div')[0].get('style')
    move_data = re.findall('background-position: -(.*)px -(.*)px;',move_size)
    size = 0.0
    if move_data:
        size = int(float(move_data[0][0])+random.uniform(-3,3))
    if size != 0:
        ActionChains(driver).click_and_hold(element).perform()
        ActionChains(driver).move_by_offset(xoffset=size, yoffset=random.randint(-2,2)).perform()
        ActionChains(driver).release().perform()

def detect_and_visualize(bg_path, slider_path, roi_width=200, show_steps=False):
    """
    改进的滑块验证码识别方法，带有可视化功能

    参数:
        bg_path: 背景图路径
        slider_path: 滑块图路径
        roi_width: 检测区域宽度
        show_steps: 是否显示处理过程的中间步骤

    返回:
        gap_x: 滑块应该移动到的x坐标
        visualization_img: 可视化结果图像
    """
    # 读取图像
    bg_color = cv2.imread(bg_path)
    bg_gray = cv2.cvtColor(bg_color, cv2.COLOR_BGR2GRAY)
    slider_color = cv2.imread(slider_path)
    slider_gray = cv2.cvtColor(slider_color, cv2.COLOR_BGR2GRAY)

    # 图像预处理
    def preprocess(img):
        img = cv2.GaussianBlur(img, (3, 3), 0)
        # img = cv2.Canny(img, 50, 150)
        return img

    bg_processed = preprocess(bg_gray)
    slider_processed = preprocess(slider_gray)

    # 可视化步骤1: 显示原始图像和预处理结果
    if show_steps:
        plt.figure(figsize=(12, 6))
        plt.subplot(2, 2, 1)
        plt.imshow(cv2.cvtColor(bg_color, cv2.COLOR_BGR2RGB))
        plt.title('原始背景图')

        plt.subplot(2, 2, 2)
        plt.imshow(bg_processed, cmap='gray')
        plt.title('预处理背景图')

        plt.subplot(2, 2, 3)
        plt.imshow(cv2.cvtColor(slider_color, cv2.COLOR_BGR2RGB))
        plt.title('原始滑块图')

        plt.subplot(2, 2, 4)
        plt.imshow(slider_processed, cmap='gray')
        plt.title('预处理滑块图')

        plt.show()

    # 裁剪ROI
    height, width = bg_processed.shape
    roi_x = max(0, width - roi_width)
    roi = bg_processed[:, roi_x:]
    roi_color = bg_color[:, roi_x:]  # 用于可视化

    # 多尺度匹配
    best_match = None
    scales = np.linspace(0.8, 1.2, 5)
    template_match_results = []

    for scale in scales:
        resized = cv2.resize(slider_processed, None, fx=scale, fy=scale)
        if resized.shape[0] > roi.shape[0] or resized.shape[1] > roi.shape[1]:
            continue
        res = cv2.matchTemplate(roi, resized, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        template_match_results.append((max_val, max_loc, scale))

        if best_match is None or max_val > best_match[0]:
            best_match = (max_val, max_loc, scale)

    if best_match is None:
        print("无法找到匹配位置")
        return -1, max_val

    max_val, max_loc, best_scale = best_match
    gap_x = roi_x + max_loc[0] - 5
    print(f"匹配置信度: {max_val}")
    # 验证匹配结果
    if max_val < 0.5:  # 置信度阈值
        print(f"匹配置信度过低: {max_val}")
        return -1, max_val

    # 创建可视化图像
    visualization_img = bg_color.copy()

    # 1. 绘制ROI区域
    cv2.rectangle(visualization_img, (roi_x, 0), (width, height), (0, 255, 255), 2)

    # 2. 绘制最佳匹配位置
    slider_h, slider_w = slider_processed.shape
    resized_w = int(slider_w * best_scale)
    resized_h = int(slider_h * best_scale)

    top_left = (gap_x, max_loc[1])
    bottom_right = (top_left[0] + resized_w, top_left[1] + resized_h)
    cv2.rectangle(visualization_img, top_left, bottom_right, (0, 0, 255), 2)

    # 3. 绘制滑块位置
    cv2.rectangle(visualization_img, (0, 0), (slider_w, slider_h), (255, 0, 0), 2)

    # 4. 绘制匹配线
    cv2.line(visualization_img, (slider_w // 2, slider_h // 2),
             (gap_x + resized_w // 2, max_loc[1] + resized_h // 2), (0, 255, 0), 2)

    # 5. 添加文本信息
    cv2.putText(visualization_img, f"Match Confidence: {max_val:.2f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    cv2.putText(visualization_img, f"Target X: {gap_x}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # 可视化步骤2: 显示匹配结果热力图
    if show_steps and template_match_results:
        best_val, best_loc, best_scale = max(template_match_results, key=lambda x: x[0])
        resized = cv2.resize(slider_processed, None, fx=best_scale, fy=best_scale)
        res = cv2.matchTemplate(roi, resized, cv2.TM_CCOEFF_NORMED)

        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.imshow(res, cmap='hot')
        plt.title('匹配热力图')
        plt.colorbar()

        plt.subplot(1, 2, 2)
        plt.imshow(cv2.cvtColor(roi_color, cv2.COLOR_BGR2RGB))
        plt.title('匹配位置')
        plt.scatter([best_loc[0]], [best_loc[1]], c='r', s=50)
        plt.show()

    plt.figure(figsize=(10, 6))
    plt.imshow(cv2.cvtColor(visualization_img, cv2.COLOR_BGR2RGB))
    plt.title(f"最终识别结果 - 滑块应移动到X坐标: {gap_x}")
    plt.axis('off')
    plt.show()
    print(f"滑块应该移动到的X坐标: {gap_x}")
    print(f"移动到的X坐标: {sqrt_func(gap_x)}")
    return gap_x, max_val

def split_number(N):
    if N <= 40:
        # Split into 2 numbers
        b = max(round(N / 2.5), 11) if N >= 20 else round(N / 2.5)
        a = N - b
        if a < b:
            a, b = b, a
        return [a, b]
    else:
        # Try splitting into 3 numbers
        c = max(round(N / 4.75), 11)
        best_split = None
        best_ratio_diff = float('inf')

        for delta in [-1, 0, 1]:  # Try nearby values of c
            current_c = c + delta
            if current_c < 11:
                continue
            b = round(1.5 * current_c)
            a = N - b - current_c
            if a >= b >= current_c:
                ratio1 = a / b
                ratio2 = b / current_c
                ratio_diff = abs(ratio1 - 1.5) + abs(ratio2 - 1.5)
                if ratio_diff < best_ratio_diff:
                    best_ratio_diff = ratio_diff
                    best_split = [a, b, current_c]

        if best_ratio_diff < 0.5:  # Accept if ratios are close enough
            return best_split
        else:
            # Fall back to 2 numbers
            b = max(round(N / 2.5), 11)
            a = N - b
            if a < b:
                a, b = b, a
            return [a, b]

def run_slider(target_dis):
    res = split_number(target_dis)
    start = [830, 620]
    if len(res) == 2:
        pyautogui.moveTo(start[0], start[1]+random.randint(-3,3),duration=0.5)
        time.sleep(random.uniform(0.01, 0.08))
        pyautogui.mouseDown()
        pyautogui.moveTo(start[0] + res[0], start[1]+random.randint(-3,3),duration=0.5)
        time.sleep(random.uniform(0.01, 0.08))
        pyautogui.moveTo(start[0] + res[0] + res[1], start[1]+random.randint(-3,3),duration=0.5)
        time.sleep(random.uniform(0.01, 0.08))
        pyautogui.mouseUp()
    if len(res) == 3:
        pyautogui.moveTo(start[0], start[1]+random.randint(-3,3),duration=0.5)
        time.sleep(random.uniform(0.01, 0.08))
        pyautogui.mouseDown()
        pyautogui.moveTo(start[0]+res[0], start[1]+random.randint(-3,3),duration=0.5)
        time.sleep(random.uniform(0.01, 0.08))
        pyautogui.moveTo(start[0]+res[0]+res[1], start[1]+random.randint(-3,3),duration=0.5)
        time.sleep(random.uniform(0.01, 0.08))
        pyautogui.moveTo(start[0]+res[0]+res[1]+res[2], start[1]+random.randint(-3,3),duration=0.5)
        time.sleep(random.uniform(0.01, 0.08))
        pyautogui.mouseUp()

def move_find():
    text = driver.find_element(By.CSS_SELECTOR,'#aliyunCaptcha-sliding-slider').get_attribute('style')
    res = int(re.findall(r'left: (.*)px;',text)[0])
    return res


def write_and_save(filename):
    pyautogui.moveTo(440,400)
    pyautogui.click()
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('backspace')
    pyperclip.copy(filename)
    print("filename:",filename)
    save_button = []
    f_save_button = []
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)
    pyautogui.moveTo(750, 500)
    pyautogui.click()
    pyautogui.moveTo(1000, 530)
    pyautogui.click()

def add_log(text):
    logs = tool.read_json('log.txt')
    logs.append(text)
    tool.write_json('log.txt', logs)


def read_log():
    logs = tool.read_json('log.txt')
    return logs


if __name__ == "__main__":
    path = [os.path.join('.\\',i) for i in os.listdir('.\\') if i.endswith('.json')]
    path.remove('.\\add_money.json')
    driver = None
    logs = read_log()
    for json_path in path:
        if json_path not in logs:
            while True:
                try:
                    file_name = [i.replace('.json', '').replace('.\\', '') for i in path]
                    pdf_dir = [os.path.join(r'C:\Users\Administrator\Downloads', i) for i in file_name]
                    path_pdf = [i for i in os.listdir(r'C:\Users\Administrator\Downloads') if i.endswith('.pdf')]
                    for i in pdf_dir:
                        if os.path.exists(i):
                            ff = [os.path.join(i, kk) for kk in os.listdir(i)]
                            path_pdf += ff
                    path_pdf = [i.split('\\')[-1] for i in path_pdf if i.endswith('.pdf')]
                    add_money = tool.read_json('add_money.json')

                    read_data = tool.read_json(json_path)
                    driver = driver_start()

                    main = driver.current_window_handle
                    for i in read_data:
                        if i['pdf_filename'] not in path_pdf and i['pdf_link'] not in add_money:
                            if i['pdf_link']!= '':
                                link = i['pdf_link']
                                print(i['title'])
                                driver.get(link)
                                time.sleep(random.uniform(2, 5))
                                soup = BeautifulSoup(driver.page_source, 'lxml')
                                while soup.select('body > div > div > div.title > p'):
                                    if soup.select('body > div > div > div.title > p')[0].text.find('系统检测到您的访问行为异常，请帮助我们完成 ') != -1:
                                        mouse_move(driver)
                                        time.sleep(3)
                                        soup = BeautifulSoup(driver.page_source, 'lxml')
                                time.sleep(random.uniform(3, 5))
                                if soup.select('#DownLoadParts > div > div > div.fl.replace > a'):
                                    if soup.select('#DownLoadParts > div > div > div.fl.replace > a')[0].text.find('撤回声明') != -1:
                                        continue
                                actions = ActionChains(driver)
                                actions.scroll_by_amount(0, 500).perform()
                                time.sleep(random.uniform(1, 2))
                                soup = BeautifulSoup(driver.page_source, 'lxml')
                                element = driver.find_element(By.CSS_SELECTOR,'#pdfDown')
                                soup_element = BeautifulSoup(driver.page_source, 'lxml').select('#pdfDown')
                                print(soup_element)
                                if soup_element:
                                    actions.move_to_element(element).click().perform()
                                    time.sleep(3)
                                    main = driver.current_window_handle
                                    print(i['pdf_filename'])
                                    write_and_save(i['pdf_filename'])

                                    if len(driver.window_handles) ==3:
                                        if i['pdf_link'] not in add_money:
                                            add_money.append(i['pdf_link'])
                                            tool.write_json('add_money.json',add_money)
                                        print('===============================================================')
                                        print(main)
                                        print(driver.window_handles)
                                        print('===============================================================')
                                        driver.switch_to.window(driver.window_handles[2])
                                        driver.close()
                                        print(main)
                                        print(driver.window_handles)
                                        print('===============================================================')
                                        time.sleep(0.5)
                                        driver.switch_to.window(driver.window_handles[1])
                                        driver.close()
                                        print(main)
                                        print(driver.window_handles)
                                        print('===============================================================')
                                        time.sleep(0.5)
                                        driver.switch_to.window(driver.window_handles[0])


                                    if len(driver.window_handles) ==2:
                                        driver.switch_to.window(driver.window_handles[1])
                                        soup = BeautifulSoup(driver.page_source, 'lxml')
                                        if soup.select('#flow_left > div:nth-child(2) > div'):
                                            if soup.select('#flow_left')[0].text.find('—— 知网会员服务 ——') != -1:
                                                if i['pdf_link'] not in add_money:
                                                    add_money.append(i['pdf_link'])
                                                    tool.write_json('add_money.json', add_money)
                                                driver.close()
                                                time.sleep(0.5)
                                                continue
                                        if soup.select('body > h3'):
                                            if soup.select('body > h3')[0].text.find('提示') != -1:
                                                Confidence = 0
                                                initial_gap = 0
                                                while Confidence < 0.8:
                                                    save_image()
                                                    initial_gap,Confidence = detect_and_visualize('bigImage.png','smallImage.png')
                                                    if Confidence > 0.8:
                                                        print(sqrt_func(initial_gap))
                                                        run_slider(sqrt_func(initial_gap))
                                                        time.sleep(random.uniform(2, 3))
                                                        break
                                                    driver.find_element(By.CSS_SELECTOR,'#aliyunCaptcha-btn-refresh').click()
                                                    time.sleep(random.uniform(2, 3))
                                                soup = BeautifulSoup(driver.page_source, 'lxml')
                                                if soup.select('#flow_left > div:nth-child(2) > div'):
                                                    if soup.select('#flow_left')[0].text.find('—— 知网会员服务 ——') != -1:
                                                        if i['pdf_link'] not in add_money:
                                                            add_money.append(i['pdf_link'])
                                                            tool.write_json('add_money.json', add_money)
                                                        driver.close()
                                                        time.sleep(0.5)
                                                else:
                                                    time.sleep(2)
                                                    print(i['pdf_filename'])
                                                    write_and_save(i['pdf_filename'])
                                                    time.sleep(random.uniform(3, 5))
                                                    driver.close()
                                        driver.switch_to.window(driver.window_handles[0])
                                    print("目前剩余页面：",driver.window_handles)
                    driver.quit()
                    tool.kill_all_java_processes()
                    add_log(json_path)
                    break
                except Exception as e:
                    print(e)
                    if driver is not None:
                        driver.quit()
                        tool.kill_all_java_processes()


