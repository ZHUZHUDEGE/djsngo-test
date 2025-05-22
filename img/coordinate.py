import cv2
import numpy as np


def crop_image(image_path, y_max, error_distance, output_path='cropped.png'):
    """
    裁剪图像（不缩放，直接截取指定区域）
    参数:
        image_path (str): 输入图像路径
        y_max (int): 图像最高点
        output_path (str, optional): 输出路径（若为None，则不保存）

    返回:
        numpy.ndarray: 裁剪后的图像（BGR格式）
    """
    # 读取图像
    y_max = y_max + error_distance
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"图像未找到: {image_path}")
    height, width, channels = img.shape
    if y_max > width:
        raise IndexError
    # 裁剪图像（numpy数组切片）
    cropped_img = img[y_max - 60:y_max + 10, 0:width]

    # 保存结果（如果指定了输出路径）
    if output_path:
        cv2.imwrite(output_path, cropped_img)
        print(f"图像已裁剪至{output_path}")
        return True
    else:
        return False


def get_bounding_rect(image_path):
    """
    获取不规则图形的最小包围矩形信息
    :param image_path: 输入图像路径（需为PNG等支持透明的格式）
    :return: 包含矩形坐标、宽高、最高点和最低点的字典
    """
    # 1. 加载图像并提取Alpha通道
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("图像加载失败，请检查路径或文件格式！")
    alpha = img[:, :, 3]  # Alpha通道
    # 2. 二值化处理
    _, binary = cv2.threshold(alpha, 1, 255, cv2.THRESH_BINARY)
    # 3. 查找轮廓
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None  # 无有效轮廓
    # 4. 合并所有轮廓（应对多连通区域）
    all_contours = np.vstack(contours)

    # 5. 计算最小直立矩形
    x, y, w, h = cv2.boundingRect(all_contours)
    print({
        "top_left": (x, y),  # 左上角坐标
        "bottom_right": (x + w, y + h),  # 右下角坐标
        "width": w,  # 矩形宽度
        "height": h,  # 矩形高度
        "top": y,  # 最高点Y坐标（最小Y值）
        "bottom": y + h  # 最低点Y坐标（最大Y值）
    })
    # 6. 返回结果
    return {
        "top_left": (x, y),  # 左上角坐标
        "bottom_right": (x + w, y + h),  # 右下角坐标
        "width": w,  # 矩形宽度
        "height": h,  # 矩形高度
        "top": y,  # 最高点Y坐标（最小Y值）
        "bottom": y + h  # 最低点Y坐标（最大Y值）
    }


def get_new_bigImg(s_img_path, b_img_path, output_png):
    # 获取包围矩形信息
    rect_info = get_bounding_rect(s_img_path)
    if not rect_info:
        print("图像无效或完全透明！")
    # 示例调用：从 (100, 50) 开始，裁剪 400x300 的区域
    cropped_img = crop_image(b_img_path, rect_info['bottom'], 0, output_png)
    return cropped_img
