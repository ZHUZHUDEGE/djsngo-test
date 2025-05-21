import cv2
import numpy as np
from matplotlib import pyplot as plt


def process_image_with_alpha(image_path, darken_factor=0.5):
    """
    处理带透明通道的图像，处理后恢复原始透明度
    :param image_path: 图片路径
    :param darken_factor: 变暗系数(0-1)
    :return: 处理后的图像(带透明通道)
    """
    # 读取图像(包含Alpha通道)
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    # 分离通道
    if img.shape[2] == 4:  # 如果有Alpha通道
        b, g, r, a = cv2.split(img)
        rgb = cv2.merge([b, g, r])
    else:  # 如果没有Alpha通道
        rgb = img.copy()
        a = None

    # 将RGB变暗(这里使用线性变暗作为示例)
    darkened = np.clip(rgb.astype(np.float32) * darken_factor, 0, 255).astype(np.uint8)

    # 如果有Alpha通道，重新合并
    if a is not None:
        # 分离处理后的RGB
        b_dark, g_dark, r_dark = cv2.split(darkened)
        # 重新合并RGBA
        result = cv2.merge([b_dark, g_dark, r_dark, a])
    else:
        result = darkened

    return result


def compare_images(original_path, processed_img):
    """
    对比显示原始图像和处理后的图像
    """
    # 读取原始图像(带透明通道)
    original = cv2.imread(original_path, cv2.IMREAD_UNCHANGED)

    # 创建白色背景用于显示透明区域
    def add_white_bg(img):
        if img.shape[2] == 4:
            b, g, r, a = cv2.split(img)
            white_bg = np.ones_like(b) * 255
            result = cv2.merge([
                np.where(a == 0, white_bg, b),
                np.where(a == 0, white_bg, g),
                np.where(a == 0, white_bg, r)
            ])
            return result
        return img

    # 准备显示图像
    original_display = add_white_bg(original)
    processed_display = add_white_bg(processed_img)

    # 转换为RGB格式显示
    original_display = cv2.cvtColor(original_display, cv2.COLOR_BGR2RGB)
    processed_display = cv2.cvtColor(processed_display, cv2.COLOR_BGR2RGB)

    # 显示对比
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(original_display)
    plt.title("Original Image")
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(processed_display)
    plt.title("Processed Image (Darkened)")
    plt.axis('off')

    plt.tight_layout()
    plt.show()


# 使用示例
image_path = "image_with_alpha.png"  # 替换为你的带透明通道的图片

# 处理图像(保留透明通道)
processed_img = process_image_with_alpha(image_path, darken_factor=0.6)

# 显示对比
compare_images(image_path, processed_img)

# 保存结果(保留透明通道)
cv2.imwrite("darkened_with_alpha.png", processed_img)