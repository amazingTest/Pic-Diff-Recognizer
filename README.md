# Pic-Diff-Recognizer

+ [Pic-Diff-Recognizer 中文文档](https://github.com/amazingTest/Pic-Diff-Recognizer/blob/master/README_CN.md)

Selenium plugin library based on image difference recognition and page intelligent exploration.

The origin of this library is to make UI automatic testing no longer need to deal with page elements, but directly use real visual differences to judge whether the test results meet the expectations.

# installation
    
    pip install -r requirements.txt
    
    pip install pic-diff-recognizer
    
    
# best practice

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
    
    
# contact me

email address：523314409@qq.com
