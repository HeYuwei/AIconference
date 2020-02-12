# import semanticscholar as sch
# paper = sch.paper('10.1109/CVPR.2019.00050')
# citations = paper['citations']

from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
import time

d = DesiredCapabilities.CHROME
d['loggingPrefs'] = {'performance': 'ALL'}
wd = webdriver.Chrome()
wd.get("https://www.semanticscholar.org/search?q=Fine-grained%20visual%20classification%20of%20aircraft&sort=relevance")    # 打开百度浏览器
browser = wd
# wd.find_element_by_id("search_form").send_keys("Agency Problems and Residual Claims")   # 定位输入框并输入关键字
# wd.find_element_by_id('kw').send_keys(Keys.ENTER)  #输入回车代替点击搜索按钮
# wd.find_element_by_id("su").click()
# time.sleep(3)   #等待3秒
# wd.quit()   #关闭浏览器

# 设置变量url，用于浏览器访问。
url = 'https://www.baidu.com/'




# 打开浏览器并访问网址
browser.get(url)

# 关键步骤2：获取 request 信息。
info = browser.get_log('performance')    # 这里的参数 'performance' 是步骤1中添加的。获取到的是一个列表。

# 用 for循环读取列表中的每一项元素。每个元素都是 json 格式。
for i in info:
    dic_info = json.loads(i["message"])    # 把json格式转成字典。
    info = dic_info["message"]['params']    # request 信息，在字典的 键 ["message"]['params'] 中。
    if 'request' in info:    				# 如果找到了 request 信息，就终断循环。
        print(info['request'])
        break
