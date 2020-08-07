# encoding = 'utf-8'

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import openpyxl
import time
import os
import datetime
import schedule

def scrollPage(driver):
    '''
    This fuction is designed to scroll down the webpage to the bottom to get information by "loading more"(ajax request)
    '''
    # Define a variable ‘temp_height’ to record the distance from the scrollbar to the top, initialized to 0
    temp_height = 0
    while True:
        # Scroll the page to the bottom
        driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
        # Set a 2-seconds interval to load more infor
        time.sleep(2)
        # Check the current distance from the scrollbar to the top of the page
        check_height = driver.execute_script("return document.documentElement.scrollTop || document.body.scrollTop;")
        # If the current distance is the same as it after the last scroll, it means that the bottom of the page has been reached
        if check_height == temp_height:
            break
        # Assign check_height to temp_height for the next comparison
        temp_height = check_height

def mkdir(path):
    '''
    Create storage path
    '''
    # Check whether the storage path exists
    folder = os.path.exists(path)
    # create the path if not existed
    if not folder:
        os.makedirs(path)   
    else:
        pass
    return path

def getArticlelst(soup,articlelstpath):
    '''
    Crawl the content of the article title (title, article link)
    '''                
    # "num" is used to initialize the article storage path for each crawling iteration
    # "count" is used to label article titles and save them to leiphonetitle.txt in order
    global num
    open(articlelstpath,'a')
    # Get the current number of articles saved
    num = count = int(len(open(articlelstpath,'r').readlines()) / 2)
    # Take out all the contents from soup, the "class" attribute of which is "headTit"
    title_list = soup.find_all(attrs={"class": "headTit"})
    # Create an empty list "artitle_url_lst" for storing article links
    artitle_url_lst = []
    # Loop through the content of each title
    for title in title_list:
        # Get the content, title name, whose attribute is ‘title’
        title_name = title.get('title')
        if not title_name:
            continue
        # Get article links
        artitle_url = str(title.get('href'))
        # Check if the article already exists
        foo = open(articlelstpath, 'r')
        isInrecord = False
        for line in foo.readlines():
            if artitle_url in line:
                isInrecord = True
                break
        # If it's a new piece of data
        if not isInrecord:
            count+=1
            # Save the article link to artitle_url_lst
            artitle_url_lst.append(artitle_url)
            # Save article title text and link
            with open(articlelstpath,'a',encoding='utf-8') as fp:
                title_text =  str(count) + ". " + str(title_name)    # Generate ordered titles
                fp.write(title_text)
                fp.write('\n')
                fp.write(artitle_url)
                fp.write('\n')
            print(title_text)   # Print article titles (in order) as output log
    # Return to the list of article links that need to be crawled this time
    return artitle_url_lst

def getData(soup,num,article_folder,sh1,wb,excelpath):
    '''
    Get the text content of each article
    '''
    # Prompt the article being downloaded in log
    print('\n------------------------------------------------------')
    print('Article %d is downloading......' %num)
    # Specify the save path of each article(using "num" to distinguish)
    txtfilename = article_folder + '/article' + str(num) + '.txt'
    # Separate the layer of the article content in the web page
    divs = soup.select('body > div.lphArticle-detail > div.article-template')
    # Get the article title, author name, release time, abstract and text 
    header = divs[0].select('div.article-title > div > h1')[0].get_text().strip()
    name_str = divs[0].select('div.article-title > div > div.msg > table > tr > td.aut')[0].get_text().strip()
    time_str = divs[0].select('div.article-title > div > div.msg > table > tr > td.time')[0].get_text().strip()
    abstract = divs[0].select('div.article-title > div > div.article-lead')[0].get_text().strip()
    text = divs[0].select('div.info > div > div.article-left > div.lph-article-comView')[0].get_text().strip().replace('\n', '').replace('\r', '')
    # Save articles to corresponding folders
    with open(txtfilename, 'a', encoding='utf-8') as fp:
        fp.write(header)
        fp.write('\n')
        fp.write(name_str)
        fp.write('\t')
        fp.write(time_str)
        fp.write('\n')
        fp.write(abstract)
        fp.write('\n')
        fp.write(text)
    fp.close()
    # Combine article information into a list to save to .xlsx chart
    data = [header, name_str, time_str, abstract, text]
    sh1.append(data)
    wb.save(filename= excelpath)
    print('Article text has been downloaded.')

def getImg(soup,num,article_folder,headers):
    '''
    Download images of the article
    '''
    # Navigate to the layer where the pictures are
    divs_img = soup.find_all('div',class_ = 'lph-article-comView')
    # Image labeling
    cnt = 0
    # Get the set of the image download addresses
    imags = divs_img[0].find_all('img')
    if not imags:
        print('No image contained in this article.')
    else: 
        # Download each picture in turn
        for img in imags:
            cnt += 1
            # Get image download addresses
            img_url = img.get('src')
            img_name = str(num) + '_' + str(cnt) + '.jpg'
            # Sending picture url request
            try:
                img_request = requests.get(img_url,headers = headers)
            except:
                print(img_name + " failed to be downloaded")
                f = open(r'/Users/chenayu/Desktop/leiphone_4/imgerror.txt','a',encoding='utf-8')
                f.write(img_name)
                f.write('\n')
                f.write(img_url)
                f.write('\n')
                f.close()
                print(img_url)
                continue
            # Specify the save path
            imgfilename = article_folder + '/' + img_name
            # downloading...
            with open(imgfilename, 'wb') as fp:
                fp.write(img_request.content)
            fp.close()
            print('Image %d has been downloaded.'%cnt)
            print(img_url)
            # time.sleep(0.1)
        print('All images of this article have been downlaoded.')

def main():
    print('----------------------PROJ START----------------------\n')
    web_url = 'https://www.leiphone.com/'
    # Run Chromedriver for automatic control
    driver = webdriver.Chrome(executable_path=r"/Users/chenayu/Desktop/chromedriver")
    driver.get(web_url)
    scrollPage(driver)
    
    # define saving path
    projectfolder = r'/Users/chenayu/Desktop/leiphone_4/'
    excelname = 'record.xlsx'
    excelpath = os.path.join(projectfolder, excelname)
    articlelst = 'leiphonetitle.txt'
    articlelstpath = os.path.join(projectfolder,articlelst)

    # Parse web content
    soup1 = BeautifulSoup(driver.page_source, 'lxml')

    # Determine the list of article links that need to be crawled
    artitle_url_lst = getArticlelst(soup1,articlelstpath)

    # Check the saving path of the .xlsx file
    if not os.path.isfile(excelpath):
        row0 = ['Header', 'Auther', 'Time', 'Abstract', 'Text']
        wb = openpyxl.Workbook()
        sh1 = wb.active
        sh1.title = 'article'
        sh1.append(row0)
    else:
        wb = openpyxl.load_workbook(excelpath)
        sh1 = wb.active
    
    start = time.time()

    global num

    # If there be updated articles:
    if artitle_url_lst:
        for i in range(len(artitle_url_lst)):
            num+=1
            link = artitle_url_lst[i]
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36"}
            # Parse each article web page
            try:
                response = requests.get(link, headers = headers)
            except:
                print('Article %d failed to be downloaded.'%num)
                f = open(projectfolder + 'article_error.txt','a',encoding='utf-8')
                f.write(str(num))
                f.write('\n')
                f.write(link)
                f.write('\n')
                f.close()
                print(link)
                continue
            content = response.text
            soup = BeautifulSoup(content, 'lxml')               
            article_folder = os.path.join(projectfolder, 'Article ' + str(num))
            mkdir(article_folder)   
            getData(soup, num, article_folder,sh1,wb,excelpath)
            getImg(soup,num,article_folder,headers)
        wb.save(filename= excelpath)
    else:
        pass  
    # Close Chromedriver
    driver.close()
    # Calculate executing time
    end = time.time()
    print(end - start)

if __name__ == '__main__':
    '''
    timed run
    '''
    schedule.every(1).minutes.do(main)
    # schedule.every().day.at("16:49").do(main) 
    while True:
        schedule.run_pending()
        # check every 30 minutes
        time.sleep(10)
        print(datetime.datetime.now())