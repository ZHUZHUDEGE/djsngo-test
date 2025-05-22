import base64
import os
import random
import re

import cv2
import numpy as np
import requests
from browsermobproxy import Server
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
from selenium.webdriver import ActionChains
import pyautogui
from selenium.webdriver.common.by import By
from seleniumwire.undetected_chromedriver import ChromeOptions, Chrome, webdriver
import time
import tool
import simplejson

from img.cropper import TransparentCropper
from img.coordinate import get_new_bigImg
from img.multi_slider_dir import find_more_mode
from img.save_img import save_image

ppp= {
        "title": "",
        "keywords": [],
        "authors": [],
        "institution": [],
        "authorsDetail": [
            {
                "name": "",
                "address": ""
            }
        ],
        "abstract": "",
        "publication_date": "",
        "journal_name": "",
        "volume_number": "",
        "issue_number": "",

        "doi": "",

        "pdf_link": "",
        "pdf_filename": "",
        "pdf_storage_path": "",

        "core_collections": ""
    }


def detect_and_visualize(bg_path, slider_path,roi_width = 200, show_steps=False):
    """
    改进的滑块验证码识别方法，带有可视化功能
    破解下载PDF使用
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
        #　img = cv2.GaussianBlur(img, (3, 3), 0)
        img = cv2.Canny(img, 50, 150)
        cv2.imwrite('slider_processed.png', img)
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
        return -1, 0

    max_val, max_loc, best_scale = best_match
    gap_x = max_loc[0] - 5
    print(f"匹配置信度: {max_val}")
    # 验证匹配结果
    if max_val < 0.5:  # 置信度阈值
        print(f"匹配置信度过低: {max_val}")
        return -1, max_val

    # 创建可视化图像
    visualization_img = bg_color.copy()

    # 1. 绘制ROI区域
    cv2.rectangle(visualization_img, (0, 0), (width, height), (0, 255, 255), 2)

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
    print(f"移动到的X坐标: {gap_x}")
    return gap_x, max_val


def human_like_drag_advanced(driver, element, target_distance, duration=2.0):
    action = ActionChains(driver)
    location = element.location
    start_x = location['x'] + element.size['width'] // 2
    start_y = location['y'] + element.size['height'] // 2

    # 生成贝塞尔曲线轨迹
    points = generate_bezier_trajectory(
        start_x, start_y,
        target_distance,
        steps=30
    )

    action.click_and_hold(element).perform()

    total_moved = 0
    for i in range(1, len(points)):
        x, y = points[i]
        dx = x - points[i - 1][0]
        dy = y - points[i - 1][1]

        # 动态速度控制（开始和结束慢）
        progress = total_moved / target_distance
        speed_factor = 0.3 + 0.7 * np.sin(progress * np.pi)
        move_time = max(0.05, duration / len(points) * speed_factor)

        action.move_by_offset(dx, dy).pause(move_time).perform()
        total_moved += dx

        # 随机停顿
        if random.random() < 0.1:
            time.sleep(random.uniform(0.05, 0.1))

        action.release().perform()


def generate_bezier_trajectory(start_x, start_y, distance, steps=30):
    """生成贝塞尔曲线轨迹"""
    end_x = start_x + distance
    ctrl1 = start_x + distance * 0.3
    ctrl2 = start_x + distance * 0.7

    points = []
    for t in np.linspace(0, 1, steps):
        # 贝塞尔曲线公式
        x = (1 - t) ** 3 * start_x + 3 * (1 - t) ** 2 * t * ctrl1 + 3 * (1 - t) * t ** 2 * ctrl2 + t ** 3 * end_x
        y = start_y + random.uniform(-3, 3)
        points.append((x, y))
    return points


# def split_number(N):
#     '''
#     :param N: 需要移动
#     :return: 将移动长度分段结果
#     '''
#     if N <= 40:
#         # Split into 2 numbers
#         b = max(round(N / 2.5), 11) if N >= 20 else round(N / 2.5)
#         a = N - b
#         if a < b:
#             a, b = b, a
#         return [a, b]
#     else:
#         # Try splitting into 3 numbers
#         c = max(round(N / 4.75), 11)
#         best_split = None
#         best_ratio_diff = float('inf')
#
#         for delta in [-1, 0, 1]:  # Try nearby values of c
#             current_c = c + delta
#             if current_c < 11:
#                 continue
#             b = round(1.5 * current_c)
#             a = N - b - current_c
#             if a >= b >= current_c:
#                 ratio1 = a / b
#                 ratio2 = b / current_c
#                 ratio_diff = abs(ratio1 - 1.5) + abs(ratio2 - 1.5)
#                 if ratio_diff < best_ratio_diff:
#                     best_ratio_diff = ratio_diff
#                     best_split = [a, b, current_c]
#
#         if best_ratio_diff < 0.5:  # Accept if ratios are close enough
#             return best_split
#         else:
#             # Fall back to 2 numbers
#             b = max(round(N / 2.5), 11)
#             a = N - b
#             if a < b:
#                 a, b = b, a
#             return [a, b]
#
#
# def run_slider(target_dis):
#     res = split_number(target_dis)
#     start = [830, 620]
#     if len(res) == 2:
#         pyautogui.moveTo(start[0], start[1] + random.randint(-3, 3), duration=0.5)
#         time.sleep(random.uniform(0.01, 0.08))
#         pyautogui.mouseDown()
#         pyautogui.moveTo(start[0] + res[0], start[1] + random.randint(-3, 3), duration=0.5)
#         time.sleep(random.uniform(0.01, 0.08))
#         pyautogui.moveTo(start[0] + res[0] + res[1], start[1] + random.randint(-3, 3), duration=0.5)
#         time.sleep(random.uniform(0.01, 0.08))
#         pyautogui.mouseUp()
#     if len(res) == 3:
#         pyautogui.moveTo(start[0], start[1] + random.randint(-3, 3), duration=0.5)
#         time.sleep(random.uniform(0.01, 0.08))
#         pyautogui.mouseDown()
#         pyautogui.moveTo(start[0] + res[0], start[1] + random.randint(-3, 3), duration=0.5)
#         time.sleep(random.uniform(0.01, 0.08))
#         pyautogui.moveTo(start[0] + res[0] + res[1], start[1] + random.randint(-3, 3), duration=0.5)
#         time.sleep(random.uniform(0.01, 0.08))
#         pyautogui.moveTo(start[0] + res[0] + res[1] + res[2], start[1] + random.randint(-3, 3), duration=0.5)
#         time.sleep(random.uniform(0.01, 0.08))
#         pyautogui.mouseUp()




def contains_digit(s):
    return  any(char.isdigit() for char in s)


def get_journal():
    time.sleep(5)
    res_data = ppp.copy()
    title=''
    keywords=[]
    authors=[]
    institution=[]
    authorsDetail=[]
    abstract=""
    publication_date=""
    volume_number=""
    issue_number=""

    source_page = driver.page_source.replace('<sup>','\n<sup>').replace('<p class="authortip">','\n<p class="authortip">')

    with open('html.html', 'w', encoding='utf-8') as f:
        print('网页保存')
        f.write(driver.page_source)
    soup = BeautifulSoup(source_page, 'lxml')
    print(soup.prettify())
    title = soup.select('head > title')[0].text.strip().replace(' - 中国知网', '')
    print(title)
    if title.find('总目次') != -1:
        return None
    if title.find('征稿简则') != -1:
        return None
    if title.find('部分文章预告') != -1:
        return None
    if title.find('申请指南') != -1:
        return None
    if title.find('卷首语') != -1:
        return None
    if title.find('期刊第一') != -1:
        return None
    if title.find('欢迎订阅') != -1:
        return None
    if title.find('大会在上海召开') != -1:
        return None
    if title.find('总目录') != -1:
        return None
    if title.find('新年寄语') != -1:
        return None
    if title.find('热烈祝贺') != -1:
        return None
    if title.find('SCI影响因子') != -1:
        return None
    if title.find('征文启事') != -1:
        return None
    if title.find('选题指引') != -1:
        return None
    if title.find('人工智能国际组稿推进石油工业大数据应用发展') != -1:
        return None
    if title.find('中国石油2021年度十大科技创新成果') != -1:
        return None
    if title.find('中国石油天然气集团有限公司油气储层重点实验室') != -1:
        return None
    if title.find('第四届氮素生物地球化学循环学术论坛举办') != -1:
        return None
    if title.find('《地理学报》简介') != -1:
        return None
    if title.find('《地理学报》创刊 90周年历程及贺词') != -1:
        return None
    if title.find('国际研讨会') != -1:
        return None
    if title.find('中国地理学会') != -1:
        return None
    if title.find('首届世界地理大会') != -1:
        return None
    if title.find('中国科学院“全球城市土地覆盖和热环境”观测平台在全球应用') != -1:
        return None
    if title.find('办刊进展') != -1:
        return None
    if title.find('国际地理联合会百年庆典特别大会在巴黎召开') != -1:
        return None
    if title.find('人文地理学大会') != -1:
        return None
    if title.find('自立自强,为美丽中国贡献地理巾帼力量') != -1:
        return None
    if title.find('首届全国女地理学家大会在长沙召开') != -1:
        return None
    if title.find('论坛举办') != -1:
        return None
    if title.find('年会召开') != -1:
        return None
    if title.find('本期导读') != -1:
        return None
    if title.find('征文通知') != -1:
        return None
    if title.find('专栏征文启事') != -1:
        return None
    if title.find('成功举办') != -1:
        return None
    if title.find('投稿指南') != -1:
        return None
    if title.find('目录索引') != -1:
        return None
    if title.find('杂志简介') != -1:
        return None
    if title.find('会议纪要') != -1:
        return None
    if title.find('深切缅怀') != -1:
        return None
    if title.find('主编寄语') != -1:
        return None
    if title.find('征稿启事') != -1:
        return None
    if title.find('投稿须知') != -1:
        return None
    if title.find('PROTEIN & CELL') != -1:
        return None
    if title.find('油气资源空间分布预测技术') != -1:
        return None
    authors = [i.text.strip() for i in soup.select('#authorpart > span')]
    print(authors)
    institution = [i.text.strip() for i in soup.select('body > div.wrapper > div.main > div.container > div > div:nth-child(3) > div.brief > div > h3:nth-child(3) > span')]
    if len(institution) == 0:
        institution = [i.text.strip() for i in soup.select(
            'body > div.wrapper > div.main > div.container > div > div.doc-top > div:nth-child(3) > div.brief > div.wx-tit > h3:nth-child(3) > span')]
    print(institution)
    if authors== []:
        return None
    if contains_digit(authors[0]):
        if len(authors) > 1 and len(institution) > 1:
            for i in authors:
                ids = re.findall('\d+', i)

                info_address = {
                    'name': i.replace(',', ''),
                    'institution': []
                }
                for j in institution:
                    address_i = j[0]
                    print(address_i)
                    if address_i in ids:
                        info_address['institution'].append(j)
                authorsDetail.append(info_address)
        elif len(authors) > 1 and len(institution) == 1:
            for i in authors:

                info_address = {
                    'name': i.split(',')[0],
                    'institution': [institution[0]]
                }
                authorsDetail.append(info_address)
        elif len(authors) == 1 and len(institution) > 1:
            info_address = {
                'name': authors[0],
                'institution': []
            }
            for j in institution:
                info_address['institution'].append(j)
            authorsDetail.append(info_address)

    abs_kw = soup.select('body > div.wrapper > div.main > div.container > div > div:nth-child(3) > div.row')
    if len(abs_kw) == 0:
        abs_kw = soup.select('body > div.wrapper > div.main > div.container > div > div.doc-top > div:nth-child(3) > div.brief > div.row')
    '''body > div.wrapper > div.main > div.container > div > div.doc-top > div:nth-child(3) > div.brief > div.row'''
    abstract = ''
    keywords = ''
    for i in abs_kw:
        text = i.text.strip()
        print('---------------------------------------------')
        if text.find('摘要：') != -1:
            abstract = text.replace('摘要：','').strip()
        if text.find('关键词：') != -1:
            keywords = text.replace('关键词：','').strip()
    doi_data = soup.select('body > div.wrapper > div.main > div.container > div > div:nth-child(3) > div > ul > li')
    if len(abs_kw) == 0:
        doi_data = soup.select('body > div.wrapper > div.main > div.container > div > div.doc-top > div:nth-child(3) > div > ul > li')
    print(abstract)
    print(keywords)
    doi = ''
    publication_date = ''
    for i in doi_data:
        text = i.text.strip()
        print(text)
        print('---------------------------------------------')
        if text.find('DOI：') != -1:
            doi = text.replace('DOI：','').strip()
        if text.find('在线公开时间：') != -1:
            publication_date = text.replace('在线公开时间：','').strip()
    print(doi)
    print(publication_date)
    v_i = ''

    if soup.select('body > div.wrapper > div.main > div.container > div > div.doc-top > div > div.top-tip'):
        v_i = soup.select('body > div.wrapper > div.main > div.container > div > div.doc-top > div > div.top-tip')[0].text.strip()
    if soup.select('#func609 > div'):
        v_i = soup.select('#func609 > div')[0].text.strip()


    data_p = re.findall(r'(.*)\.\s+\d+\s+,(\d+)\s+\((\d+)\)\s+查看该刊数据库收录来源', v_i)
    if data_p:
        res_data['journal_name'] = data_p[0][0]
        res_data['volume_number'] = data_p[0][1]
        res_data['issue_number'] = data_p[0][2]
        filename = (title.replace('*', '-').replace(':', '-').replace('/', '-')
                    .replace('\\', '-').replace(' ', '').replace('\n', '')
                    .replace(' ', '-') + data_p[0][0] + data_p[0][1] + '.pdf')
    else:
        res_data['journal_name'] = v_i.replace(' ', '')
        res_data['volume_number'] = ''
        res_data['issue_number'] = ''
        filename = (title.replace('*', '-').replace(':', '-').replace('/', '-')
                    .replace('\\', '-').replace(' ', '').replace('\n', '')
                    .replace(' ', '-') + str(random.randint(0,99999)) + '.pdf')



    res_data['title'] = title
    res_data['keywords'] = keywords
    res_data['authors'] = [i.split('\n')[0] for i in authors]
    res_data['institution'] = institution
    res_data['authorsDetail'] = authorsDetail
    res_data['abstract'] = abstract
    res_data['doi'] = doi
    res_data['publication_date'] = publication_date



    res_data['pdf_link'] = driver.current_url

    time.sleep(3)


    res_data['pdf_filename'] = filename
    res_data['pdf_storage_path'] = f'tjpdf/{filename}'

    print(simplejson.dumps(res_data, ensure_ascii=False, indent=4))
    return res_data


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
    print(2)
    options = {}
    chrome_options = ChromeOptions()
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
    driver.maximize_window()
    driver.get(f'http://www.baidu.com/')
    time.sleep(3)
    driver.get(f'https://www.cnki.net/')


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


def add_log(text):
    logs = tool.read_json('log.txt')
    logs.append(text)
    tool.write_json('log.txt', logs)


def read_log():
    logs = tool.read_json('log.txt')
    return logs


if __name__ == "__main__":
    first_page= {
        'big':    '#app > div > div > div > div.verifybox-bottom > div > div.verify-img-out > div > img',
        'small':  '#app > div > div > div > div.verifybox-bottom > div > div.verify-bar-area > div > div > div > img',
        'slider': '#app > div > div > div > div.verifybox-bottom > div > div.verify-bar-area > div > div > i',
        'refresh':'#app > div > div > div > div.verifybox-bottom > div > div.verify-img-out > div > div > i',
    }
    # target ='复旦大学'
    # list_404 =[]
    # for index in range(6,7):
    #     print(index)
    #     driver = driver_start()
    #     driver.get(f'https://kns.cnki.net/kns8s/search?classid=WD0FTY92')
    #     time.sleep(random.uniform(2,3))
    #     driver.find_element(By.CSS_SELECTOR, '#ModuleSearch > div:nth-child(1) > div > div > div.search-main > div > div.sort.reopt > div.sort-default > span').click()
    #     driver.find_element(By.CSS_SELECTOR,'#ModuleSearch > div:nth-child(1) > div > div > div.search-main > div > div.sort.reopt > div.sort-list > ul > li:nth-child(9) > a').click()
    #     driver.find_element(By.CSS_SELECTOR,'#ModuleSearch > div:nth-child(1) > div > div > div.search-main > div > input.search-input').send_keys(target)
    #     driver.find_element(By.CSS_SELECTOR,'#ModuleSearch > div:nth-child(1) > div > div > div.search-main > div > input.search-btn').click()
    #     driver.find_element(By.CSS_SELECTOR,
    #                         '#divGroup > dl:nth-child(4) > dt > i.icon.icon-arrow').click()
    #     # 2 3 4 5 6
    #     driver.find_element(By.CSS_SELECTOR,
    #                         f'#divGroup > dl:nth-child(4) > dd > div > ul > li:nth-child({index}) > a').click()
    #
    #     driver.find_element(By.CSS_SELECTOR,
    #                         '#perPageDiv > div > i').click()
    #     driver.find_element(By.CSS_SELECTOR,
    #                         '#perPageDiv > ul > li:nth-child(3) > a').click()
    #     time.sleep(random.uniform(2, 3))
    #     #
    #     name_link = []
    #     #
    #     while True:
    #         time.sleep(random.uniform(2,3))
    #         soup = BeautifulSoup(driver.page_source, 'lxml')
    #         title_list = soup.select('#gridTable > div > div > div > table > tbody > tr')
    #         for title in title_list:
    #             link = title.find('td',attrs={'class':'name'}).find('a').get('href')
    #             name = title.find('td',attrs={'class':'name'}).find('a').text.strip()
    #             source = title.find('td',attrs={'class':'source'}).text.strip()
    #             data = title.find('td',attrs={'class':'data'}).text.strip()
    #             print({
    #                 'name': name,
    #                 'link': link,
    #                 'data': data,
    #                 'source': source,
    #             })
    #             name_link.append({
    #                 'name': name,
    #                 'link': link,
    #                 'data': data,
    #                 'source':source,
    #             })
    #         tool.write_json(f'.\\{target}_pdf_link_{index}.json',name_link)
    #
    #         if soup.select('#PageNext'):
    #             driver.find_element(By.CSS_SELECTOR, '#PageNext').click()
    #         else:
    #             print('END')
    #             break
    #     driver.quit()
    #     tool.kill_all_java_processes()

    path = [i for i in os.listdir('.\\') if i.endswith('.json') and i.find('_pdf_') != -1]
    logs = read_log()
    for json_path in path:
        if json_path not in logs:
            pdf_detail = []
            print(json_path)
            json_data = tool.read_json(json_path)
            if os.path.exists(json_path.replace('_pdf','_detail')):
                pdf_detail = tool.read_json(json_path.replace('_pdf','_detail'))
            else:
                tool.write_json(json_path.replace('_pdf','_detail'), [])
            pdf_detail_link = [i['title'].replace('<sub>','').replace('</sub>','') for i in pdf_detail]
            print(pdf_detail_link)
            driver = driver_start()
            for i in json_data:
                if i['name'] not in pdf_detail_link and i['data']!='硕士' and i['data']!='博士' and i['data']!='国家标准' and i['data']!='科技成果':
                    print(i['link'])
                    driver.get(i['link'])

                    time.sleep(random.uniform(2, 3))
                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    if soup.select('#app > div > div > div > div.verifybox-top') != -1:
                        Confidence = 0
                        initial_gap = 0
                        while Confidence < 0.8:
                            big_img_e = driver.find_element(By.CSS_SELECTOR,first_page['big'])
                            small_img_e = driver.find_element(By.CSS_SELECTOR,first_page['small'])

                            if save_image(big_img_e,small_img_e):
                                initial_gap, Confidence = find_more_mode(
                                    'new_bigImage.png',
                                    'smallImage_no_alpha.png')
                                print(Confidence)
                            else:
                                driver.find_element(By.CSS_SELECTOR,first_page['refresh']).click()
                            if Confidence > 0.8:
                                slider_e = driver.find_element(By.CSS_SELECTOR, first_page['slider'])
                                print(initial_gap)
                                human_like_drag_advanced(driver,slider_e,initial_gap)
                                time.sleep(random.uniform(2, 3))
                                break

                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    while True:
                        if soup.select('body > div > div > div.title > p'):
                            if soup.select('body > div > div > div.title > p')[0].text.find(
                                    '系统检测到您的访问行为异常，请帮助我们完成 ') != -1:
                                mouse_move(driver)
                                time.sleep(random.uniform(2, 3))
                                soup = BeautifulSoup(driver.page_source, 'lxml')
                        else:
                            break

                    time.sleep(random.uniform(3, 5))
                    if soup.select('#DownLoadParts > div > div > div.fl.replace > a'):
                        if soup.select('#DownLoadParts > div > div > div.fl.replace > a')[0].text.find(
                                '撤回声明') != -1:
                            continue

                    detail = get_journal()
                    if detail != None and detail not in pdf_detail:
                        pdf_detail.append(detail)
                    tool.write_json(json_path.replace('_pdf', '_detail'), pdf_detail)
            driver.quit()
            tool.kill_all_java_processes()
            add_log(json_path)