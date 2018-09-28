# -*- coding: utf-8 -*-\
#搜索爬虫脚本#
import requests  
import re
import io
import sys
from bs4 import BeautifulSoup
import os

def desc():
    print("\n********************************************************************")
    print('''
        ███████╗██╗   ██╗ █████╗ ███╗   ██╗    ██████╗ 
        ██╔════╝██║   ██║██╔══██╗████╗  ██║   ██╔════╝ 
        █████╗  ██║   ██║███████║██╔██╗ ██║   ██║  ███╗
        ██╔══╝  ╚██╗ ██╔╝██╔══██║██║╚██╗██║   ██║   ██║
        ███████╗ ╚████╔╝ ██║  ██║██║ ╚████║██╗╚██████╔╝
        ╚══════╝  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝ ╚═════╝ 
                                                    
        ''')
    print("电影搜索器")
    print("\n********************************************************************")



# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gbk') #改变标准输出的默认编码 

def search(l_url):
    try:
        response = requests.get(l_url)
        response.encoding = 'utf-8' 
        # print(response.text)
        soup = BeautifulSoup(response.text,'html.parser')
        # print(soup)
        searchArr = soup.find_all('div',class_='bt_list')
    except TimeoutError:
        print("[列表]数据请求超时!!!!!")
    else:    
        mlist = []
        downItems = {}
        html = ""


        for item in searchArr:
            mUrl = item.find(class_='link').attrs["href"]
            mlist.append(mUrl)
        # print(searchArr)

        for url in mlist:
            try: 
                res = requests.get(url)
                res.encoding = 'utf-8' 
                soup = BeautifulSoup(res.text,'html.parser')
                title = soup.find('div',class_='main').find_next('div',class_='title').find_next("h2").text
                size= soup.find(text=re.compile("\u6587\u4ef6\u5927\u5c0f")).find_next("span").text 
                magnet = soup.find('a',href=re.compile('magnet.*')).attrs['href']
                print ("获取成功!!!****["+title+"]")
            except (AttributeError):
                print ("属性错误!!!")
            except UnicodeEncodeError:
                print ("编码错误!!!")
            except TimeoutError:
                print ("获取超时!!!")
            else:
                downItems[title]= [title,size,magnet]


        for item in downItems:  
            html +='<tr><td>%s</td><td style="text-align: center">%s</td><td style="text-align: center;"><a href="%s" style="color:blue">点击下载</a></td></tr>' % (downItems[item][0],downItems[item][1],downItems[item][2])

        return html





if __name__ == '__main__':
    try:
        desc();
        key = input('请输入关键词:')
        print(">=→")
        print("**正在获取中,请稍候...")

        result = '<html><head><meta http-equiv="Content-Type" content="text/html" /><style>table{border-collapse:collapse;}th,td{font-size:14px;border:1px solid #111;padding: 15px;}.highlight{color:red}a{color:#111;text-decoration: none;}</style></head><body><table><thead><tr><th style="width: 1000px;">资源名称</th><th style="width:20%">文件大小</th><th style="width:20%">磁力链接</th></tr></thead><tbody>'

        for pageNum in range(3):
            url = 'https://www.btavn.com/s/%s/%s.html' % (key,pageNum+1)
            result += search(url)

        result+='</tbody></table></body></html>'

        f = open("list.html",'w')
        f.write(result)  
    except UnicodeEncodeError as e:
        print("保存编码错误:",str(e).split(' ')[5])
    else:
        f.close()
        print(">=→")
        print("**搜索结果列表生成成功!")  
        # os.system("list.html")





