from skimage.metrics import mean_squared_error, structural_similarity
import numpy as np
import cv2
import base64
import glob
from pathlib import Path
import copy
import os
import logging


logger = logging.getLogger('pyC')


class PictureHandler:
    
    SHAPE_BOUNDARY = 2000
    
    def __init__(self, base_line_dir=None):

        self.base_line = []

        current_path = os.getcwd()

        self.base_line_dir = Path(current_path).joinpath('baseline/*.png')\
            if base_line_dir is None else base_line_dir + r'/*.png'

        self.compared_result = []  # list of dict

    def generate_diff_between_base_line_and_screen_shot(self, save_diff_dir=None):

        '''

        use after compared_base_line_and_screen_shot, make more accurate
        comparison ( ssim ) and generate diff image for each draft

        :return: None
        '''

        if save_diff_dir is None:
            save_diff_dir = os.getcwd() + '/diffResults'

        Path(save_diff_dir).mkdir(exist_ok=True)

        logger.info(f"generating diff images in {save_diff_dir}")

        for index, result in enumerate(self.compared_result):
            base_line = cv2.imread(result['baseline'])
            screen_shot = cv2.imread(result['screenShot'])
            if base_line.shape[0] > PictureHandler.SHAPE_BOUNDARY or \
                    base_line.shape[1] > PictureHandler.SHAPE_BOUNDARY:
                base_line = PictureHandler.compress_image_shape(base_line, PictureHandler.SHAPE_BOUNDARY)

            base_line_size = (base_line.shape[1], base_line.shape[0])
            screen_shot_size = (screen_shot.shape[1], screen_shot.shape[0])
            screen_shot = cv2.resize(screen_shot, base_line_size, interpolation=cv2.INTER_CUBIC) if not \
                screen_shot_size == base_line_size else screen_shot

            ssim_compared_result = structural_similarity(
                cv2.cvtColor(base_line, cv2.COLOR_BGR2GRAY),
                cv2.cvtColor(screen_shot, cv2.COLOR_BGR2GRAY),
                full=True)

            result['ssimScore'] = ssim_compared_result[0]
            ssim_diff_image = ssim_compared_result[1]

            base_line_diff, screen_shot_diff = PictureHandler.get_diff_images(ssim_diff_image, base_line, screen_shot)

            base_line_name = result['baseLineName']
            screen_shot_name = result['screenShotName']

            base_line_diff_path = save_diff_dir + f"/baseLineDiff_{base_line_name}_{index}.png"
            screen_shot_diff_path = save_diff_dir + f"/screenShotDiff_{screen_shot_name}_{index}.png"

            cv2.imwrite(base_line_diff_path, base_line_diff)
            cv2.imwrite(screen_shot_diff_path, screen_shot_diff)

            result['baseLineDiff'] = base_line_diff_path
            result['screenShotDiff'] = screen_shot_diff_path

        logger.info(f"diff images are all successfully generated in {save_diff_dir}")

    def export_picture_comparison_result(self):

        with open(f'{os.getcwd()}/testReport.txt', 'w') as f:
            for index, result in enumerate(self.compared_result):
                f.write(f" ---------------------------------------------------------------------------------------- \n")
                f.write(f" | Test case {index + 1}:\n")
                f.write(f" | Expected image address: {result['baseline']} | \n")
                f.write(f" | Most similar image address: {result['screenShot']} | \n")
                f.write(f" | Similarity score: {result['ssimScore']} \n")
                f.write(f" | Expected image diff address: {result['baseLineDiff']} | \n")
                f.write(f" | Most similar image diff address: {result['screenShotDiff']} |  \n")
                f.write(f" ---------------------------------------------------------------------------------------- \n")

    @staticmethod
    def compress_image_shape(img, shape_boundary=2000):
        if img.shape[0] > img.shape[1]:
            new_size = (int(img.shape[1] / img.shape[0] * shape_boundary), int(shape_boundary))
        else:
            new_size = (int(shape_boundary), int(img.shape[0] / img.shape[1] * shape_boundary))
        img = cv2.resize(copy.deepcopy(img), new_size, interpolation=cv2.INTER_CUBIC)
        return img

    @staticmethod
    def get_diff_images(ssim_diff_image, first_image, second_image):
        first_image_copy = copy.deepcopy(first_image)
        second_image_copy = copy.deepcopy(second_image)
        ssim_diff_image = (ssim_diff_image * 255).astype("uint8")
        thresh = cv2.threshold(ssim_diff_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0]

        for c in cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(first_image_copy, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.rectangle(second_image_copy, (x, y), (x + w, y + h), (0, 0, 255), 2)

        return first_image_copy, second_image_copy

    def compared_base_line_and_screen_shot(self, current_url, screen_shot_name, screen_shot_path):

        '''

         first comparison for huge amount of screen shot for efficiency
        ( mse method is less accurate but efficient )

        :param screen_shot_path: screen shot from browser ( path )
        :return: None

        '''

        logger.info(f"comparing screen shot of {current_url} with baseline by using mean square error method")

        screen_shot_cv2 = cv2.imread(screen_shot_path)

        mse_compared_results = []

        for bl in self.base_line:
            bl = cv2.imread(bl)
            if bl.shape[0] > PictureHandler.SHAPE_BOUNDARY or \
                    bl.shape[1] > PictureHandler.SHAPE_BOUNDARY:
                bl = PictureHandler.compress_image_shape(bl, PictureHandler.SHAPE_BOUNDARY)
            base_line_size = (bl.shape[1], bl.shape[0])
            screen_shot_cv2_size = (screen_shot_cv2.shape[1], screen_shot_cv2.shape[0])
            screen_shot_cv2_copy = cv2.resize(copy.deepcopy(screen_shot_cv2),
                                              base_line_size, interpolation=cv2.INTER_CUBIC) if not \
                screen_shot_cv2_size == base_line_size else screen_shot_cv2
            mean_squared_error_result = mean_squared_error(bl, screen_shot_cv2_copy)
            mse_compared_results.append(mean_squared_error_result)

        mse_compared_results_for_logger = [{self.compared_result[i]['baseLineName']: v}
                                           for i, v in enumerate(mse_compared_results)]

        logger.info(f"compared result is {mse_compared_results_for_logger}")

        del mse_compared_results_for_logger

        for index, result in enumerate(self.compared_result):
            if 'mseScore' not in result or mse_compared_results[index] < result['mseScore']:
                self.compared_result[index]['screenShotName'] = screen_shot_name
                self.compared_result[index]['screenShot'] = screen_shot_path
                self.compared_result[index]['mseScore'] = mse_compared_results[index]

        del screen_shot_cv2

    def load_base_line(self):
        current_path = os.getcwd()
        default_base_line_path = Path(current_path).joinpath('baseline/*.png') \
            if self.base_line_dir is None else str(self.base_line_dir)
        logger.info(f'loading base line images from {default_base_line_path}')
        print(f'loading base line images from {default_base_line_path}')
        self.base_line = glob.glob(str(default_base_line_path))
        file_names = [pic_path[pic_path.rindex("\\") + 1:] if "\\" in pic_path else pic_path
                      for pic_path in self.base_line]
        self.base_line = [pic_path for pic_path in self.base_line]
        # init compared_result with baseline
        self.compared_result = [{'baseLineName': file_names[i], 'baseline': bl} for i, bl in enumerate(self.base_line)]

    @staticmethod
    def convert_base64_image_to_cv2(input_image):
        screen_shot_byte = base64.b64decode(input_image)
        np_arr = np.fromstring(screen_shot_byte, np.uint8)
        input_image_cv2 = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return input_image_cv2

    @staticmethod
    def compared_two_base64_image(first_img, second_img, method='mse'):
        first_img_cv2 = PictureHandler.convert_base64_image_to_cv2(first_img)
        second_img_cv2 = PictureHandler.convert_base64_image_to_cv2(second_img)
        if not first_img_cv2.shape == second_img_cv2.shape:
            second_img_cv2 = cv2.resize(second_img_cv2, (first_img_cv2.shape[1], first_img_cv2.shape[0]),
                                        interpolation=cv2.INTER_CUBIC)
        if method == 'mse':
            return mean_squared_error(first_img_cv2, second_img_cv2)
        elif method == 'ssim':
            return structural_similarity(cv2.cvtColor(first_img_cv2, cv2.COLOR_BGR2GRAY),
                                         cv2.cvtColor(second_img_cv2, cv2.COLOR_BGR2GRAY),
                                         full=True)


if __name__ == '__main__':
    pass
