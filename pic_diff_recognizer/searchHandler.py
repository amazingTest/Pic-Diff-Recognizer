import logging
from pathlib import Path
from pic_diff_recognizer.pictureHandler import PictureHandler
from pic_diff_recognizer.scrollHandler import ScrollHandler
import pic_diff_recognizer.utils as utils
from selenium.common import exceptions
logger = logging.getLogger('pyC')


class SearchHandler:

    def __init__(self, browser):
        self.browser = browser
        self.scroll_handler = ScrollHandler(self.browser)
        self.picture_handler = PictureHandler()
        self.url_histories = []

    def get_current_page_elements_hrefs(self, reject_list=None):
        if reject_list is None:
            reject_list = [f'{self.browser.current_url}', f'{self.browser.current_url}#', '', '/', './',
                           'javascript:;', 'javascript: void(0);', 'javascript:void(0)']
        elements = self.browser.find_elements('css selector', 'a')
        hrefs = []
        for ele in elements:
            href = ele.get_attribute('href')
            hrefs.append(href) if href not in reject_list and href not in self.url_histories else None
        return list(set(hrefs))

    def traverse_href(self, origin_url,
                      save_screen_shots_dir='./baseline',
                      search_depth=1,
                      reject_list=None,
                      mouse_hover_css_locators=None,
                      compare_baseline_and_screen_shots=False,
                      **kwargs):

        if reject_list is None:
            reject_list = [f'{self.browser.current_url}', f'{self.browser.current_url}#', '', '/', './',
                           'javascript:;', 'javascript: void(0);', 'javascript:void(0)']

        if mouse_hover_css_locators is None:
            mouse_hover_css_locators = []

        logger.info(f'visiting {origin_url}')

        try:
            self.browser.get(origin_url)

            logger.info(f'page of {origin_url} has successfully loaded')

            Path(save_screen_shots_dir).mkdir(exist_ok=True)

            if mouse_hover_css_locators:
                kwargs['mouse_hover_css_locators'] = mouse_hover_css_locators

            self.scroll_handler.scroll_to_bottom(save_screen_shots_dir=save_screen_shots_dir, **kwargs) \
                if not compare_baseline_and_screen_shots else self.scroll_handler.scroll_to_bottom(
                picture_handler=self.picture_handler, save_screen_shots_dir=save_screen_shots_dir, **kwargs)

            if not origin_url or search_depth < 1:
                return

            logger.info(f'searching for sub-pages of {origin_url} ...')

            print(f'AI-testing brain is searching for images of {origin_url} ...')

            hrefs = self.get_current_page_elements_hrefs(reject_list=reject_list)

            logger.info(f'got {len(hrefs)} hrefs, they are {hrefs}')

            print(f'AI-testing brain got {len(hrefs)} images candidates')

            [self.url_histories.append(href) for href in hrefs]

            process_bar_message = f'Progress of testing baseline and images from {origin_url}: ' \
                if compare_baseline_and_screen_shots else f'Progress of making baseline of {origin_url}: '

            for index, href in enumerate(hrefs):
                utils.processBar(index, len(hrefs) - 1, process_bar_message)
                self.traverse_href(href, save_screen_shots_dir, search_depth - 1, reject_list,
                                   mouse_hover_css_locators, compare_baseline_and_screen_shots, **kwargs) \
                    if href else None

        except exceptions.TimeoutException:
            logger.error(f'\n page of {origin_url} fail to loaded due to timeout exception')
            logger.warning(f'skip {origin_url}')
        except exceptions.WebDriverException as e:
            logger.error(f'\n page of {origin_url} fail to loaded, because [{e}]')
            logger.warning(f'skip {origin_url}')


if __name__ == '__main__':
    import datetime

    import difflib
    from violent_webdriver import Chrome
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
    import os
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("disable-infobars")
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    dr = Chrome.violent_chromedriver(chrome_options=chrome_options,
                                     executable_path='../../chromedriver.exe')

    dr.set_window_size(1920, 1080)
    origin_url = 'https://www.famaomao.com/'
    dr.get(origin_url)
    dr.implicitly_wait(10)

    t = './&which=&client_id=100410602&redirect_uri=http%3A%2F%2Fwww.jianshu.com%2Fusers%2Fauth%2Fqq_connect%2Fcallback&response_type=code&state=%257B%257D_1586954364204138'

    dr.save_screenshot(f'{t}.png')
    dr.quit()
    # find_script = "function imgsStatus(){ \
    #                         let emptyList = new Array(); \
    #                     　　let imgs = document.getElementsByTagName('img'); \
    #                     　　for (i=0; i<imgs.length; i++){ \
    #                            if  (imgs[i].complete){ \
    #                                 emptyList.push(imgs[i].complete)\
    #                             }; \
    #                         }; \
    #                         return emptyList; \
    #                     }; return imgsStatus()"
    #
    # e = dr.execute_script(find_script)
    # print(e)
    # print(list(e))
    #
    # find_script = "function getNoChildElements(){ \
    #                     let emptyList = new Array(); \
    #                 　　let elements = jQuery.find('body *'); \
    #                 　　for (i=0; i<elements.length; i++){ \
    #                        if  (elements[i].children.length == 0){ \
    #                             emptyList.push(elements[i])\
    #                         }; \
    #                     }; \
    #                     return emptyList; \
    #                 }; return getNoChildElements()"
    #
    # #els = dr.find_elements_by_css_selector('body *')
    # locator = "li[name=\'关注公众号\']"
    # els = dr.find_element_by_css_selector(locator)
    # ActionChains(dr).move_to_element(els).perform()
    # print(datetime.datetime.utcnow())
    # # els = dr.execute_script(find_script)
    # print(datetime.datetime.utcnow())
    # print(len(els))
    # text_list = []
    #
    # j = 0
    # origin_pg  = dr.page_source
    # d = difflib.Differ()
    # for i,e in enumerate(els):
    #     text = e.text
    #     if 0 < len(text) < 1000:
    #         print(f'开始{i+1}: {text}')
    #         # dr.save_screenshot('./t1.png')
    #         els1 = len(list(dr.find_elements_by_css_selector('li')))
    #         ActionChains(dr).move_to_element(e).perform()
    #         ps1 = dr.page_source
    #         els2 = len(list(dr.find_elements_by_css_selector('li')))
    #         # dr.save_screenshot('./t2.png')
    #         print(f'结果{i+1}: {els2==els1}')
    #         j+=1
    # print(f'total: {j}')
    # dr.quit()




    # search_handler = SearchHandler(dr)
    # el = dr.find_element_by_xpath('//*[@id="explores-index"]/div[2]/div[2]/div[3]/div/div/div[1]/div/div/ul/li[3]/a')
    #
    # dr.save_screenshot('./t1.png')
    # sc = dr.get_screenshot_as_base64()
    # re1 = len(search_handler.get_current_page_elements_hrefs())
    # ActionChains(dr).move_to_element(el).perform()
    # dr.save_screenshot('./t2.png')
    # sc1 = dr.get_screenshot_as_base64()
    #
    # re2 = len(search_handler.get_current_page_elements_hrefs())
    # # 直接查元素悬停后 pagesource有没有改变！ 哈哈哈我真实天才
    #
    # result = search_handler.picture_handler.compared_two_base64_image(sc, sc1,method='ssim')[0]
    # print(result)
    # print(re1)
    # print(re2)
    # dr.quit()
    # search_handler.traverse_href(origin_url)
    #
    # search_handler.url_histories = []
    # search_handler.picture_handler.load_base_line()
    # dr.get(origin_url)
    # save_screen_shots_dir = os.getcwd() + '/screenshots'
    # search_handler.traverse_href(origin_url, save_screen_shots_dir=save_screen_shots_dir,
    #                              compare_baseline_and_screen_shots=True)
    # search_handler.picture_handler.generate_diff_between_base_line_and_screen_shot()
    # search_handler.picture_handler.export_picture_comparison_result()
    # dr.quit()
