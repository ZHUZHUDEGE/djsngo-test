import time

import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import correlate2d
from matplotlib.patches import Rectangle


def get_255_matrix(image_path):
    '''
    获取 图片 纯白区域矩阵 放弃其他特征 r g b a
        纯白 255,255,255
    :param image_path:
    :return:
    '''
    # 读取图片（保留Alpha通道如果存在）
    original = cv2.imread(image_path,cv2.IMREAD_UNCHANGED)
    b, g, r, a = None, None, None, None
    # 分离通道
    if original.shape[2] == 4:  # 如果有alpha通道
        # 分离通道
        b, g, r, a = cv2.split(original)

    # 提取0,0,0白色区域
    v = original[:,:,2] / 255.0  # 归一化到0-1
    bright_mask = v > 0.99
    print(original.shape)
    print(bright_mask.shape)
    return bright_mask


def convolution_based_matching(large_mat, small_mat, threshold=0.8):
    # 计算归一化互相关
    corr = correlate2d(large_mat.astype(float), small_mat.astype(float), mode='valid')
    max_possible = np.sum(small_mat)  # 完全匹配时的最大值
    normalized_corr = corr / max_possible  # 归一化到 [0, 1]

    # 找到所有超过阈值的位置
    match_positions = np.where(normalized_corr >= threshold)
    matches = [
        ((i, j), normalized_corr[i, j])
        for i, j in zip(match_positions[0], match_positions[1])
    ]
    return matches


def visualize_matches(large_mat, small_mat, matches, output_path="matches.png"):
    """
    可视化大矩阵中所有匹配小矩阵的位置

    参数:
        large_mat: 大矩阵 (2D numpy数组)
        small_mat: 小矩阵 (2D numpy数组)
        matches: 匹配结果列表 [((y,x,h,w), similarity), ...]
        output_path: 输出图片路径
    """
    plt.figure(figsize=(10, 10))

    # 显示大矩阵
    plt.imshow(large_mat, cmap='gray', interpolation='nearest')
    plt.title(f"Found {len(matches)} matches (small matrix size: {small_mat.shape})")

    h = small_mat.shape[0]
    w = small_mat.shape[1]

    # 为每个匹配位置绘制矩形框
    for (y, x), similarity in matches:
        rect = Rectangle((x - 0.5, y - 0.5), w, h,
                         linewidth=2, edgecolor='r', facecolor='none',
                         label=f'sim={similarity:.2f}')
        plt.gca().add_patch(rect)

        # 在框中心显示相似度
        plt.text(x + w / 2, y + h / 2, f'{similarity:.2f}',
                 color='yellow', ha='center', va='center', fontsize=8)

    # 避免重复图例
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))

    plt.legend(by_label.values(), by_label.keys())
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    print(f"可视化结果已保存到 {output_path}")
    plt.show()
    time.sleep(3)
    plt.close()


# # 使用示例
# smallImage_255 = get_255_matrix("smallImage_no_alpha.png")
# bigImg_255 = get_255_matrix("new_bigImage.png")
# # 示例
# matches = convolution_based_matching(bigImg_255, smallImage_255, threshold=0.75)
# visualize_matches(bigImg_255, smallImage_255, matches)


def find_more_mode(smallImage="smallImage_no_alpha.png", bigImage="bigImage.png",visual=False):
    smallImage_255 = get_255_matrix(smallImage)
    bigImg_255 = get_255_matrix(bigImage)
    # 示例
    matches = convolution_based_matching(bigImg_255, smallImage_255, threshold=0.75)
    if visual:
        visualize_matches(bigImg_255, smallImage_255, matches)
    return matches[0],matches[1]



