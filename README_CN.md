# Pic-Diff-Recognizer

![输入图片说明](https://images.gitee.com/uploads/images/2020/0709/231926_06a4fc19_5239689.png "屏幕截图.png")

基于图像差异识别与页面遍历探索的 Selenium UI 自动化测试插件库。

此库诞生的起源是为了让 UI 自动化测试不再需要与页面元素打交道, 而是直接使用真实的视觉差异来判断测试结果是否符合预期。

# 安装

    pip install -r requirements.txt
    
    pip install pic-diff-recognizer
    
# 最佳实践

    from pic_diff_recognizer.searchHandler import SearchHandler
    from violent_webdriver import Chrome
    from selenium.webdriver.chrome.options import Options
    
    
    # add some useful options :)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    
    # init driver , executable_path should be your own path!
    dr = Chrome.violent_chromedriver(chrome_options=chrome_options,
                                     executable_path='/usr/local/bin/chromedriver')
    
    # init searchHandler
    search_handler = SearchHandler(browser=dr)
    
    # search and saving baseline images in current directory named baseline
    search_handler.traverse_href(origin_url='https://gitbook.cn/gitchat/author/5cea0bfbb78cc870612d8bba')
    
    # -------------------- assuming after some iterations of current project -----------------------------
    
    search_handler.url_histories = []
    
    # load baseline images
    search_handler.picture_handler.load_base_line()
    
    # search and comparing screen shots and baseline images
    search_handler.traverse_href(origin_url='https://gitbook.cn/gitchat/author/5cea0bfbb78cc870612d8bba',
                                 compare_baseline_and_screen_shots=True)
    
    # generate_diff_between_base_line_and_screen_shot and output diffResults to current directory
    search_handler.picture_handler.generate_diff_between_base_line_and_screen_shot()
    
    # output testReport.txt to current directory
    search_handler.picture_handler.export_picture_comparison_result()
    
# 联系我

![输入图片说明](https://images.gitee.com/uploads/images/2020/0311/174608_8a272cf2_5239689.png "屏幕截图.png")
