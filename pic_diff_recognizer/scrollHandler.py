import time
import logging
import re
from selenium.webdriver.common.action_chains import ActionChains
logger = logging.getLogger('pyC')


class ScrollHandler:

    get_scroll_top_script = 'function getScrollTop() \
                                { \
                                　　var scrollTop = 0, bodyScrollTop = 0, documentScrollTop = 0; \
                                　　if(document.body){ \
                                　　　　bodyScrollTop = document.body.scrollTop; \
                                　　} \
                                　　if(document.documentElement){ \
                                　　　　documentScrollTop = document.documentElement.scrollTop; \
                                　　} \
                                    scrollTop = (bodyScrollTop - documentScrollTop > 0) ? bodyScrollTop : documentScrollTop; \
                                    return scrollTop; \
                                }; return getScrollTop()'

    get_window_height_script = 'function getWindowHeight(){ \
                                　　var windowHeight = 0; \
                                　　if(document.compatMode == "CSS1Compat"){ \
                                　　　　windowHeight = document.documentElement.clientHeight; \
                                　　}else{ \
                                　　　　windowHeight = document.body.clientHeight; \
                                　　} \
                                　　return windowHeight; \
                                }; return getWindowHeight()'

    get_total_height_script = 'function getScrollHeight(){ \
                            　　var scrollHeight = 0; \
                            　　if(document.body){ \
                            　　　　bSH = document.body.scrollHeight; \
                            　　} \
                            　　if(document.documentElement){ \
                            　　　　dSH = document.documentElement.scrollHeight; \
                            　　} \
                                scrollHeight = (bSH - dSH > 0) ? bSH : dSH ; \
                            　　return scrollHeight; \
                            }; return getScrollHeight()'

    set_scroll_top_script = 'document.documentElement.scrollTop = {}'

    get_imgs_status = "function imgsStatus(){ \
                                let emptyList = new Array(); \
                            　　let imgs = document.getElementsByTagName('img'); \
                            　　for (i=0; i<imgs.length; i++){ \
                                   if  (imgs[i].complete){ \
                                        emptyList.push(imgs[i].complete)\
                                    }; \
                                }; \
                                return emptyList; \
                            }; return imgsStatus()"

    def __init__(self, browser):
        self.browser = browser

    def get_total_scroll_height(self):
        return self.browser.execute_script(ScrollHandler.get_total_height_script)

    def get_window_height(self):
        return self.browser.execute_script(ScrollHandler.get_window_height_script)

    def get_scroll_top(self):
        return self.browser.execute_script(ScrollHandler.get_scroll_top_script)

    @staticmethod
    # deal with 1920 x 1080 ---> 1903 x 1096 for image recognition disaster event
    def whether_set_new_scroll_window_size_or_not(origin_window_size, new_window_size):
        origin_width = origin_window_size['width']
        origin_height = origin_window_size['height']
        new_width = new_window_size[0]
        new_height = new_window_size[1]

        if 0.991 < new_width / origin_width < 0.992 and 0.985 < origin_height / new_height < 0.986 or \
            0.991 < new_width / origin_width < 0.992 and origin_height == new_height or \
                0.985 < origin_height / new_height < 0.986 and new_width == origin_width:
            return False
        else:
            return True

    def save_screen_shot(self, save_screen_shots_dir, screen_shot_name_length_limit=150):
        prefix = self.browser.current_url[self.browser.current_url.index('//') + 2:].replace('/', '.')
        prefix = re.sub('[\/:*?"<>|]', '_', prefix)
        suffix = str(time.time()).replace('.', '')

        screen_shot_name = f'{prefix}_{suffix}'

        screen_shot_name = screen_shot_name[0: screen_shot_name_length_limit]\
            if len(screen_shot_name) > screen_shot_name_length_limit else screen_shot_name

        screen_shot_path = save_screen_shots_dir + '/{}.png'.format(screen_shot_name)
        self.browser.save_screenshot(screen_shot_path) \
            if save_screen_shots_dir else None

        logger.info(f'screen shot of {self.browser.current_url} named [{screen_shot_name}]'
                    f' has saved in {save_screen_shots_dir}')

        return screen_shot_name, screen_shot_path

    def get_current_page_prepare_hovered_elements(self, mouse_hover_css_locators):
        prepare_hovered_elements = []
        for locator in mouse_hover_css_locators:
            locator = locator.strip()
            elements = self.browser.find_elements('css selector', locator)
            logger.info(f'find {len(elements)} prepare_hovered elements with css-selector'
                        f' {locator} in {self.browser.current_url} ')
            [prepare_hovered_elements.append(ele) for ele in elements]
        return prepare_hovered_elements

    def scroll_to_bottom(
            self, picture_handler=None, scroll_step=10, scroll_limit=10000, save_screen_shots_dir=None, **kwargs):

        while True:
            new_scroll_top = self.scroll(y_displacement=scroll_step)
            if new_scroll_top + self.get_window_height() >= self.get_total_scroll_height()\
                    or new_scroll_top > scroll_limit:

                while True:
                    images_status = self.browser.execute_script(ScrollHandler.get_imgs_status)
                    if all(images_status):
                        logger.info(f'images are all completely loaded')
                        break
                    logger.warning(f'images are not all completely loaded, waiting for next check...')
                    time.sleep(0.5)

                origin_window_size = self.browser.get_window_size()

                scroll_width = self.browser.execute_script('return document.documentElement.scrollWidth')
                scroll_height = self.browser.execute_script('return document.documentElement.scrollHeight')

                self.browser.set_window_size(scroll_width, scroll_height)\
                    if ScrollHandler.whether_set_new_scroll_window_size_or_not(
                        origin_window_size, (scroll_width, scroll_height)) else None

                screen_shot_name, screen_shot_path = self.save_screen_shot(save_screen_shots_dir)

                picture_handler.compared_base_line_and_screen_shot(current_url=self.browser.current_url,
                                                                   screen_shot_name=screen_shot_name,
                                                                   screen_shot_path=screen_shot_path) \
                    if picture_handler else None

                if 'mouse_hover_css_locators' in kwargs:
                    prepare_hovered_elements = self.get_current_page_prepare_hovered_elements(
                        kwargs['mouse_hover_css_locators'])
                    for element in prepare_hovered_elements:
                        ActionChains(self.browser).move_to_element(element).perform()
                        self.save_screen_shot(save_screen_shots_dir)
                        picture_handler.compared_base_line_and_screen_shot(current_url=self.browser.current_url,
                                                                           screen_shot_name=screen_shot_name,
                                                                           screen_shot_path=screen_shot_path) \
                            if picture_handler else None

                self.browser.set_window_size(origin_window_size['width'], origin_window_size['height'])

                break

    def scroll(self, y_displacement=0):
        current_scroll_top = self.browser.execute_script(ScrollHandler.get_scroll_top_script)
        new_scroll_top = current_scroll_top + y_displacement
        self.set_scroll_top(new_scroll_top)
        return new_scroll_top

    def set_scroll_top(self, scroll_top):
        self.browser.execute_script(ScrollHandler.set_scroll_top_script.format(scroll_top))


if __name__ == '__main__':
    pass
