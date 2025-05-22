import cv2
import numpy as np
from PIL import Image
from typing import Union, Tuple


class TransparentCropper:
    """
    去除图片多余透明部分的 3 种方法：
    1. opencv_crop() - 适合简单单连通区域（最快）
    2. pil_crop()    - 通用方法（兼容性好）
    3. contour_crop()- 适合复杂多连通区域（最精确）
    """

    def __init__(self, image_path: str):
        """
        初始化加载图片
        :param image_path: 图片路径（支持 PNG 透明背景）
        """
        self.image_path = image_path
        self._check_image()

    def _check_image(self):
        """检查图片是否有效"""
        try:
            with Image.open(self.image_path) as img:
                if 'A' not in img.getbands():
                    print("⚠️ 警告：图片无 Alpha 通道，可能无法正确裁剪透明区域")
        except Exception as e:
            raise ValueError(f"图片加载失败: {str(e)}")

    def opencv_crop(self, save_path: str = None) -> Union[np.ndarray, None]:
        """
        OpenCV 快速裁剪（单连通区域）
        :param save_path: 保存路径（可选）
        :return: 裁剪后的 numpy 数组（BGR+Alpha）
        """
        img = cv2.imread(self.image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise ValueError("OpenCV 无法读取图片")

        alpha = img[:, :, 3]
        coords = cv2.findNonZero(alpha)
        if coords is None:
            print("⚠️ 图片完全透明")
            return None

        x, y, w, h = cv2.boundingRect(coords)
        cropped = img[y:y + h, x:x + w]

        if save_path:
            cv2.imwrite(save_path, cropped)
        return cropped



# # 使用示例
# if __name__ == "__main__":
#     # 单方法使用
#     cropper = TransparentCropper("input.png")
#     cropper.opencv_crop("output_opencv.png")  # 最快
#     cropper.pil_crop("output_pil.png")  # 通用
#     cropper.contour_crop("output_contour.png")  # 最精确
#
#     # 比较三种方法
#     TransparentCropper.compare_methods("input.png")