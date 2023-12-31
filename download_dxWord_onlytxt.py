import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait       #WebDriverWait注意大小

# selenium.webdriver.edge.options.Options

'''
匹配方式：
    [1-9]+、  1、
    [一二三四五六七八九十百千]+、   一、
    第[一二三四五六七八九十百千]+部分：   第一部分：
    [1-9]+\.   1.
    \u2460-\u2468  ①-⑨
    [(（]+[1-9一二三四五六七八九十百千]+[）)]+[、.]?     （1）或（一）、（2）.      有问题，万一是ip咋办
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
driver.switch_to.window(driver.window_handles[1])
print(driver.title)
print(driver.current_url)
print(driver.window_handles,driver.current_window_handle)

dl_elements = driver.find_elements(By.XPATH,'//div[@class="section-arrow"]/dl')

for i in range(len(dl_elements)):
    # 等待元素出现后，再执行后续操作
    dl_element = WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH,'//div[@class="section-arrow"]/dl[%d]//div[@class="text-overflow"]'%(i+1))))
    # \W是匹配所有的非字符非数字的字符，由于文件名中不能使用：，所以要用正则表达式替换掉
    title = re.sub('\W+','_',dl_element.get_attribute('title'))
    print('..................正在爬取《%s》........................'%title)

    # 点击章节，并加载页面
    driver.execute_script('arguments[0].click()',dl_element)
    '''！！！！！！！！注意：find_element会与实际元素相绑定，所以后续实际元素变化时，page_elements也会变化！！！！！！！！(但是好像有时延，可能会造成元素刷新了但是依旧操作旧元素的情况)'''
    # 包含所有page元素
    page_elements = WebDriverWait(driver,30).until(EC.visibility_of_all_elements_located((By.XPATH,'//div[@class="pdfViewer"]/div[@class="page"]')))

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

    text = ''.join(paragraph_list)
    # 对文本数据进行分割，并写入文档中
    split_text(
        text,
        delete_font_list=[
            # 这是每页的 标题
            '\n',
            ' '
        ],
        save_path = f'data/{title}.txt'
    )

    print('=' * 30, '文档爬取结束', '=' * 30)


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



