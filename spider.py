# encoding = 'utf-8'

from bs4 import BeautifulSoup
from selenium import webdriver
import time
import os
import requests
import datetime
import schedule

def scrollPage(driver):
    '''定义页面滚动函数'''
    # 设定一个初始值
    temp_height = 0
    while True:
        # 将页面滚动至底端
        driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
        time.sleep(2)
        # 检查当前滚动条距离页面顶端的距离
        check_height = driver.execute_script("return document.documentElement.scrollTop || document.body.scrollTop;")
        if check_height == temp_height:
            break
        temp_height = check_height

def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
    else:
        pass
    return path

def getArticlelst(soup):
    '''获取文章标题内容（标题、文章链接）'''
    global count                   # 用于标记文章个数
    global num
    open(r"/Users/chenayu/Desktop/leiphone_3/leiphonetitle_1.txt",'a')
    num = count = int(len(open(r"/Users/chenayu/Desktop/leiphone_3/leiphonetitle_1.txt",'rU').readlines()) / 2)
    # 取出soup中所有class属性为headTit的内容，返回格式为bs4解析格式的resultset
    title_list = soup.find_all(attrs={"class": "headTit"})        
    artitle_url_lst = []    # 创建存放文章链接的空列表
    title_lst = []          # 创建存放文章标题的空列表
    for title in title_list:
        # 获取title中属性为‘title’的内容——标题名称
        title_name = title.get('title')
        if not title_name:
            continue
        artitle_url = str(title.get('href')) # 获取文章链接
        foo = open(r'/Users/chenayu/Desktop/leiphone_3/leiphonetitle_1.txt', 'r')
        isInrecord = False
        for line in foo.readlines():
            if artitle_url in line:
                isInrecord = True
                break
        if not isInrecord:
            title_lst.append(title_name)    # 把文章标题名称保存至列表中
            count+=1
            artitle_url_lst.append(artitle_url) # 把文章链接保存至列表中
            # article_url_record.append(artitle_url)
            with open(r'/Users/chenayu/Desktop/leiphone_3/leiphonetitle_1.txt','a',encoding='utf-8') as fp:
                title_text =  str(count) + ". " + str(title_name)    # 生成有序标题
                fp.write(title_text)
                fp.write('\n')
                fp.write(artitle_url)
                fp.write('\n')
            # title_lst.append(title_name)    # 把文章标题名称保存至列表中
            # artitle_url = title.get('href') # 获取文章链接
            # artitle_url_lst.append(artitle_url) # 把文章链接保存至列表中
            print(title_text)   # 打印文章标题（有序）
    return artitle_url_lst

def getArticleInfor(soup,num,folder_path):
    '''获取文章属性信息信息（标题、作者、导语）'''
    divs_infor = soup.select('body > div.lphArticle-detail > div.article-template > div.article-title')
    txtfilename = folder_path + '/article' + str(num) + '.txt'
    for info in divs_infor:
        # 分离h1标题文本
        header = '标题：'+info.div.h1.get_text().strip()
        # 分离作者信息
        name_str = info.div.tr.get_text().strip()
        # 获取导语，类型为resultset
        abstract = info.div(attrs ={'class': 'article-lead'})
        for item in abstract:
            msg = item.get_text()   # 分离导语文本
        with open(txtfilename, 'a', encoding='utf-8') as fp:
            fp.write(header)
            fp.write('\n')
            fp.write(name_str)
            fp.write(msg)
            fp.write('\n\n')
        fp.close()

def getText(soup,num,folder_path):
    '''获取文章文本内容'''
    print('\n------------------------------------------------------')
    print('正在爬取第%d篇文章内容' %(num))
    # 定位至正文段落，返回值为resultset类型
    divs_text = soup.select('div > div.article-left > div.lph-article-comView > p')
    # 指定文本保存路径
    txtfilename = folder_path + '/article' + str(num) + '.txt'
    for div in divs_text:
        text = div.get_text()   # 从set中获取文本内容
        with open(txtfilename, 'a', encoding='utf-8') as fp:
            fp.write(text)
            fp.write('\n')
    print('文本爬取完成。')

def getImg(soup,num,folder_path,headers):
    '''获取文章图片内容'''
    # import requests
    divs_img = soup.find_all('div',class_ = 'lph-article-comView')
    # 给图片标号
    cnt = 0
    for div_img in divs_img:
        imags = div_img.find_all('img') # 返回类型为resultset
        if not imags:
            print('本文没有图片素材')
            break
        else: 
            for img in imags:
                cnt += 1
                img_url = img.get('src')    # 获取图片下载地址
                img_name = str(num) + '_' + str(cnt) + '.jpg' # 图片命名
                try:
                    img_request = requests.get(img_url,headers = headers)   # 模拟图片url请求
                except:
                    print(img_name + "本张图片下载失败")
                    f = open(r'/Users/chenayu/Desktop/leiphone_3/imgerror.txt','a',encoding='utf-8')
                    f.write(img_name)
                    f.write('\n')
                    f.write(img_url)
                    f.write('\n')
                    f.close()
                    print(img_url)
                    continue
                imgfilename = folder_path + '/' + img_name              # 指定保存路径
                with open(imgfilename, 'wb') as fp:
                    fp.write(img_request.content)
                fp.close()
                print('第%d张图片下载完成。'%cnt)
                print(img_url)
                time.sleep(0.1)
            print('图片爬取完成。')

def main():
    print('----------------------PROJ START----------------------')
    web_url = 'https://www.leiphone.com/'
    driver = webdriver.Chrome(executable_path=r"/Users/chenayu/Desktop/chromedriver")
    driver.get(web_url)
    global num
    # while True:
    scrollPage(driver)
    soup1 = BeautifulSoup(driver.page_source, 'lxml')
    artitle_url_lst = getArticlelst(soup1)
    if artitle_url_lst:
        for i in range(len(artitle_url_lst)):
            num+=1
            link = artitle_url_lst[i]
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36"}
            try:
                responsne = requests.get(link, headers = headers)
            except:
                print('第%d篇文章爬取失败'%num)
                f = open(r'/Users/chenayu/Desktop/leiphone_3/article_error.txt','a',encoding='utf-8')
                f.write(num)
                f.write('\n')
                f.write(link)
                f.write('\n')
                f.close()
                print(link)
                continue
            content = responsne.text
            soup = BeautifulSoup(content, 'lxml')               
            folder_path = '/Users/chenayu/Desktop/leiphone_3/第' + str(num) + '篇文章'
            mkdir(folder_path)  # 为每篇文章创建一个文件夹
            getArticleInfor(soup,num,folder_path)
            getText(soup,num,folder_path)
            getImg(soup,num,folder_path,headers)
        # driver.find_element_by_xpath(r"/html/body/div[3]/div/div[1]/div[3]/div[2]/div[2]/a[2]").click()   # 控制网页翻页
    else:
        pass
    driver.close()
    # print(article_url_lst)

if __name__ == '__main__':
    schedule.every(5).minutes.do(main)
    while True:
        schedule.run_pending()
        time.sleep(60)
        print(datetime.datetime.now())
