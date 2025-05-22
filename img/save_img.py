import base64
import os
import re

import requests
from undetected_chromedriver import webelement

from img.coordinate import get_new_bigImg
from img.cropper import TransparentCropper


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
def save_image(element_big:webelement, element_small:webelement,path1="smallImage.png", path2="smallImage_no_alpha.png", path3="bigImage.png", path4='new_bigImage.png'):
    '''
    完成图片保存和切割用于图标识别 保存4张图片
        保存考虑两种 url 或 base64
        切割图片具体查看 文件夹 img
    :param element_big: 大图的element
    :param element_small: 滑块的element
    :param path1: 小图保存的位置 #
    :param path2: 小图去除透明区域图片的位置 # 大图做切割的必要条件 识别的重要条件
    :param path3: 大图保存的位置
    :param path4: 大图根据小图切割后保存的位置 #加快识别速度
    :return: True or False
    '''
    bigImg = element_big.get_attribute("src")  # 获取图片的style属性
    if bigImg.startswith('http'):
        if download_image(bigImg, '.\\bigImage.png') == True:
            print('下载成功')
    # bs64模式
    elif bigImg.startswith('data:image/png;base64'):
        bigImg = bigImg + '结束了'
        bImg_base64 = re.findall('data:image/png;base64,(.*?)结束了', bigImg, re.S | re.I)[0]
        bImgdata = base64.b64decode(bImg_base64)

        # 将图片保存为文件
        with open(path3, 'wb') as f:
            f.write(bImgdata)

    smallImg = element_small.get_attribute("src")  # 获取图片的style属性
    if smallImg.startswith('http'):
        if download_image(smallImg, '.\\smallImage.png') == True:
            print('下载成功')
    elif smallImg.startswith('data:image/png;base64'):
        # bs64模式
        smallImg = smallImg + '结束了'
        sImg_base64 = re.findall('data:image/png;base64,(.*?)结束了', smallImg, re.S | re.I)[0]
        sImgdata = base64.b64decode(sImg_base64)
        # 将图片保存为文件
        with open(path1, 'wb') as f:
            f.write(sImgdata)

    cropper = TransparentCropper(path1)
    cropper.opencv_crop(path2)

    if get_new_bigImg(path1, path3, path4):
        return [path1, path2, path3, path4]
    else:
        return None
