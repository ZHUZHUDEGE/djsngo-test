import cv2
import numpy as np
from matplotlib import pyplot as plt

def darken_image_linear(img, factor=0.5):
    """
    通过线性乘法降低亮度
    :param img_path: 图片路径
    :param factor: 变暗系数(0-1)，越小越暗
    :return: 变暗后的图片
    """
    darkened = np.clip(img.astype(np.float32) * factor, 0, 255).astype(np.uint8)
    return darkened


def apply_filters_and_compare(image_path):
    # 读取图片（保留Alpha通道如果存在）
    original = cv2.imread(image_path,cv2.IMREAD_UNCHANGED)
    b, g, r, a = None, None, None, None
    # 分离通道
    if original.shape[2] == 4:  # 如果有alpha通道
        # 分离通道
        b, g, r, a = cv2.split(original)

    original_NA = cv2.cvtColor(cv2.merge([b,g,r]), cv2.COLOR_BGR2RGB)

    # 提取0,0,0白色区域
    v = original[:,:,2] / 255.0  # 归一化到0-1
    bright_mask = v > 0.99

    original_Gauss = cv2.GaussianBlur(original_NA, (5, 5), 0) # 高斯滤波器
    original_Gauss_dark = darken_image_linear(original_Gauss)

    original_Gauss_dark[bright_mask] = original_NA[bright_mask]

    b_dark, g_dark, r_dark = cv2.split(original_Gauss_dark)

    final_img = cv2.merge([b_dark, g_dark, r_dark,a])
    final_img[bright_mask] = original[bright_mask]
    cv2.imwrite('final_img.png',final_img)
    # 创建滤波器处理结果
    filters = {
        "Original": original,
        "Gaussian Blur (3x3) + dark ": final_img,
    }

    # 设置显示布局
    plt.figure(figsize=(20, 15))
    plt.subplots_adjust(hspace=0.3, wspace=0.1)

    # 显示所有图片
    for i, (name, image) in enumerate(filters.items(), 1):
        plt.subplot(3, 3, i)
        # 确保图像是3通道的（处理边缘检测可能产生的单通道结果）
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        plt.imshow(image)
        plt.title(name, fontsize=10)
        plt.axis('off')

    plt.suptitle("OpenCV Filter Comparison (Transparent areas shown as white)", fontsize=16)
    plt.show()


def detect_and_visualize(bg_path, slider_path,roi_width = 200, show_steps=False):
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
        cv2.imwrite('slider_processed.png', img)
        return img

    bg_processed = bg_gray
    slider_processed = slider_gray

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
    if max_val < 0.2:  # 置信度阈值
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


# 使用示例
image_path = "smallImage_no_alpha.png"  # 替换为你的图片路径（支持PNG透明图片）
apply_filters_and_compare(image_path)

#　detect_and_visualize('new_bigImage.png','final_img.png')