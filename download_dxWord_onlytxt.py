import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service

# selenium.webdriver.edge.options.Options

'''
匹配方式：
    [1-9]+、  1、
    [一二三四五六七八九十百千]+、   一、
    第[一二三四五六七八九十百千]+部分：   第一部分：
    [1-9]+\.   1.
    \u2460-\u2468  ①-⑨
    [(（]+[1-9一二三四五六七八九十百千]+[）)]+[、.]?     （1）或（一）、（2）.
'''
def split_text(
        text,
        delete_font_list,
        save_path,
        parttern = '[1-9]+、|[一二三四五六七八九十百千]+、|第[1-9一二三四五六七八九十百千]+[条部分章]+[：、.]?|[1-9]+\.|[\u2460-\u2468][.、]?|[(（]+[1-9一二三四五六七八九十百千]+[）)]+[、.]?'
):
    # 串联文档文字，并替换掉空格和换行符
    for delete_font in delete_font_list: text = text.replace(delete_font, '')

    separator_list = re.findall(parttern,text)
    separator_list.append('')       # 使 符号列表 与 内容列表长度保持一致
    content_list = re.split(parttern,text)

    print(save_path)
    result_f = open(save_path,'w',encoding='utf8')

    print(text)
    print(separator_list)
    print(re.split(parttern,text))
    print(len(re.findall(parttern,text)),len(re.split(parttern,text)))

    for i in range(len(content_list)):
        result_f.write(str(content_list[i])+'\n\n')
        result_f.write(str(separator_list[i]))

    result_f.close()

'''
add_argument 用于向EdgeOptions对象添加 命令行参数,相当于在命令行后面的参数(会打开浏览器)
    options.add_argument('--headless')  浏览器不提供可视化页面
    options.add_argument('--hide-scrollbars') 隐藏滚动条, 应对一些特殊页面
        # 添加调试端口和用户数据目录参数
        # options.add_argument('--remote-debugging-port=9300')
add_experimental_option 用于向EdgeOptions对象添加 实验性选项 (直接连接已打开的浏览器)

'''
# options.add_argument('--user-data-dir="F:\PythonProject\爬虫\selenium学习\user_dir"')
options = webdriver.EdgeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9300")
driver = webdriver.Edge(service=Service(executable_path=r'msedgedriver.exe'),options=options)

# 变换标签页
driver.switch_to.window(driver.window_handles[0])
print(driver.title)
print(driver.current_url)
print(driver.window_handles,driver.current_window_handle)


dl_element = driver.find_element(By.CLASS_NAME,'section-arrow').find_element(By.XPATH,'./dl//div[@class="chapter-item"]/div[@class="text-overflow"]')
# \W是匹配所有的非字符非数字的字符，由于文件名中不能使用：，所以要用正则表达式替换掉
title = re.sub('\W+','_',dl_element.get_attribute('title'))

'''！！！！！！！！注意：find_element会与实际元素相绑定，所以后续实际元素变化时，page_elements也会变化！！！！！！！！'''
# 包含所有page元素
page_elements = driver.find_element(By.CLASS_NAME,'pdfViewer').find_elements(By.CLASS_NAME, 'page')

print('-'*30,'共有%d文档页'%len(page_elements),'-'*30)

'''
    注意，由于网页限制，所以在爬取时，务必打开网页！！！！
'''
paragraph_list = []
for i in range(len(page_elements)):
    print(page_elements[i].get_attribute('data-loaded'))
    if page_elements[i].get_attribute('data-loaded') == 'true':
        # 查找page下，textLayer里的所有div
        text_element_list = page_elements[i].find_elements(By.XPATH, './div[@class="textLayer"]/div')
        # 获取每页的所有文本列表的内部文字
        paragraph = [text_element.text.strip() for text_element in text_element_list]
        paragraph_list.append(''.join(paragraph))

        print('第%d页文档已获取完毕...' % int(page_elements[i].get_attribute('data-page-number')))
        # 必须重新获取到“下一页”的元素才可以，否则点击过期元素无效
        driver.find_element(By.XPATH, "//div[@class='pdf-view-toolbar']//div[@title='下一页']").click()
        time.sleep(0.3)

print('-'*30,'文档爬取结束','-'*30)
print(f'{title}.txt')

text = ''.join(paragraph_list)
# 对文本数据进行分割，并写入文档中
split_text(
    text,
    delete_font_list=[
        # 这是每页的 标题
        '担当是责任进取是要求团结是基石开放是动力云网运营部（大数据和AI中心）a安全团队2022年1月大数据和AI中心员工安全培训1云网运营部（大数据和AI中心）担当是责任进取是要求团结是基石开放是动力',
        '\n',
        ' '
    ],
    save_path = f'{title}.word'
)

# driver.execute_script('window.open("https://www.baidu.com")')

'''
pattern = r'(第\d+部分|^[一二三四五六七八九十]+、|^\d+、)'
- `.`：匹配任意单个字符，除了换行符。
- `*`：匹配前面的字符零次或多次。
- `+`：匹配前面的字符一次或多次。
- `?`：匹配前面的字符零次或一次。
- `^`：匹配字符串的开头。
- `$`：匹配字符串的结尾。
- `[]`：匹配方括号内的任意一个字符。
- `()`：捕获匹配的文本。
'''



