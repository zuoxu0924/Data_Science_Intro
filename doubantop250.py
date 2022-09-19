from bs4 import BeautifulSoup
import requests
import re
import os
import csv
import pandas
import matplotlib.pyplot as plt

header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
}
# 存储图片链接
links = []
# 获取书名
findTitle = re.compile(r'title="(.*?)"', re.S)
# 获取作者、出版社、年份
findInfo = re.compile(r'<p class="pl">(.*?)</p>', re.S)
# 获取评分
findScore = re.compile(r'span class="rating_nums">(.*?)</span>')
# 获取评价人数
findpcount = re.compile(r'<span class="pl">(.*?)</span>', re.S)
# 获取一句话评语
findLine = re.compile(r'<span class="inq">(.*)</span>', re.S)


# 获取有效的html
def get_validhtml(url):
    try:
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(e)


# 保存每一本书的图片
def save_images():
    if os.path.exists("images") is not True:
        print(os.getcwd())
        os.mkdir(os.getcwd()+'/images')

    for i in range(len(links)):
        path = './images/{}.jpg'.format(i + 1)
        source = requests.get(links[i])
        with open(path, 'wb') as f:
           f.write(source.content)


# 爬每一页的基本信息
def getInfoList(base):
    # 存储爬到的信息
    infoList = []
    for i in range(0, 10):
        url = base + str(i * 25)
        vHtml = get_validhtml(url)

        soup = BeautifulSoup(vHtml, "html.parser")
        for item in soup.find_all("tr", class_="item"):
            data = []
            item = str(item)

            title = re.findall(findTitle, item)[0]
            data.append(title)

            info = re.findall(findInfo, item)[0]
            wpylist = info.split('/')

            if len(wpylist) > 5:
                wpylist = wpylist[:5]
                if len(wpylist[-1]) > 7:
                    pub = wpylist[-2]
                    year = wpylist[-1]
                else:
                    pub = wpylist[-3]
                    year = wpylist[-2]
            else:
                pub = wpylist[-3]
                year = wpylist[-2]

            writer = wpylist[0]
            data.append(writer)
            data.append(pub)
            data.append(year)

            score = re.findall(findScore, item)[0]
            data.append(score)

            pcount = re.findall(findpcount, item)[0]
            pcount = re.sub('((\\s+)?)(\\s+)?', "", pcount)
            pcount = pcount.replace("(", "")
            pcount = pcount.replace("人评价)", "")
            data.append(pcount)

            line = re.findall(findLine, item)
            if len(line) != 0:
                line = line[0]
                data.append(line)
            else:
                data.append(" ")

            infoList.append(data)

        pictures = soup.find_all("a", class_="nbg")
        for picture in pictures:
            links.append(picture.find("img").attrs["src"])

    return infoList


# 将信息写入csv文件
def save_data(datalist):
    f = open("./top250.csv", "a", newline="", encoding="utf-8-sig")
    writer = csv.writer(f)
    writer.writerow(("书名", "作者", "出版社", "年份", "评分", "评价人数", "一句话评语"))
    for data in datalist:
        writer.writerow((data[0], data[1], data[2], data[3], data[4], data[5], data[6]))
    f.close()


def clean_data():
    df = pandas.read_csv("top250.csv")
    df.head()

    df['年份'] = df['年份'].str[:5]
    df_clean = df[["书名", "作者", "出版社", "年份", "评分", "评价人数", "一句话评语"]]
    data = pandas.DataFrame(df_clean.groupby(['年份']).agg({'书名': 'count'}))
    #print(data)
    data.plot(kind="bar")
    plt.show()

def main():
    baseurl = "https://book.douban.com/top250?start="
    infolist = getInfoList(baseurl)
    save_images()
    save_data(infolist)
    clean_data()


if __name__ == "__main__":
    main()
