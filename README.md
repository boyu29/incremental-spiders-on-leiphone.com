# Incremental Spiders on leiphone.com

## Backgrounds

Since my major is EE and I do power system analysis during my undergraduate study, I'm a green hand in python programming. Thus, I'm taking online courses to obtain fundemantal language syntax.

My advisor suggests I get down to do a project to improve my programming skills. This is the first project I've been assigned by my team leader during my intership here in iFlytek.

## Instructions

In this project, I utilized several modules and functions for operating web browser, seperating essential information, downloading and saving data locally, and running the project automatically in specific time point.

You can download and run the spider_leiphoneupdates_github.py on your computer directly as long as you've installed the required modules. Remember to revise the saving path in the project to make sure you can save the record on you computer.

## Functions Implemented

- Open web browser via ChromeDriver, scroll the page down to the bottom to load more.
- Get the title and link of each article. Save the information to 'leiphonetitle.txt'.
- Read the 'leiphonetitle.txt' file and use the file data as a reference to achieve **incremental storage**.
- Create a separate folder for each article to save data.
- Get the text content of the article. Save it to the 'article.txt' file in the corresponding folder.
- Format and store the data in an table to improve readability.
- Download the pictures included in the article：
  - Store the images in the corresponding folder;
  - Labele in the order;
  - For pictures that failed to download, record their serial number and download address in the 'imgerror.txt' file.
- Start the crawler regularly:
  - The test case uses a 1-hour cycle. And the web content is crawled every hour;
  - Check whether the specified time is reached every 30 minutes.
