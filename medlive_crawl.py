# encoding: UTF-8
import re
import cookielib,urllib2
from bs4 import BeautifulSoup
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#获取一级页面的所有url
def getClassUrl():

    urls = []
    print ">>>>>>>>>>>>>>>>>>>>>>>>"
    #获取初始页面所有标签内容
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    #url = "http://disease.medlive.cn/wiki/entry/10001228_101_0"
    url = "http://disease.medlive.cn/wiki/list/171"
    headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0'}
    request = urllib2.Request(url, headers = headers)
    response = opener.open(request)
    html = response.read()
    #print response.read()
    soup = BeautifulSoup(html, "lxml")
    #print soup

    #解析标签，获取第一层分类的url列表
    classUrls = soup.find_all(href=re.compile("/wiki/list/"))
    #print classUrls
    for classUrl in classUrls:
        #print classUrl.get('href')
        urls.append("http://disease.medlive.cn"+classUrl.get('href'))
    del urls[0]
    #print urls
    return urls

#获取二级页面的所有url
def getDetailUrl(urls):
    detailUrls = []

    for url in urls:
        #print url
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        #url = "http://disease.medlive.cn/wiki/list/171"
        headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0'}
        request = urllib2.Request(url, headers = headers)
        response = opener.open(request)
        html = response.read()
        #print response.read()
        soup = BeautifulSoup(html, "lxml")
        #print soup

        #解析标签，获取第二层分类的url列表
        classUrls = soup.find_all(href=re.compile("/gather/"))
        #print classUrls
        for classUrl in classUrls:
            #print classUrl.get('href')
            #print classUrl
            detailUrls.append("http://disease.medlive.cn"+classUrl.get('href'))
            #print detailUrls
        #print detailUrls
    return detailUrls

#获取所有“查看知识库词条”的url
def knowBaseUrl(detailUrls):
    knowBaseUrls = []
    diseases = []
    #先取前五个url做实验
    for detailUrl in detailUrls[0:4]:
        print detailUrl
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        #url = "http://disease.medlive.cn/wiki/list/171"
        headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0'}
        request = urllib2.Request(detailUrl, headers = headers)
        response = opener.open(request)
        html = response.read()
        #print response.read()
        soup = BeautifulSoup(html, "lxml")
        #获取疾病名称，并作为返回值
        disease = soup.label.get_text()
        diseases.append(disease)
        #获取“查看知识库词条”的url _blank
        knowBaseUrl = soup.find_all(href=re.compile("http://disease.medlive.cn/wiki/essentials_"))
        #print knowBaseUrl
        for knowBaseUrl in knowBaseUrl:
            knowBaseUrls.append(knowBaseUrl.get('href'))
        #print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    #print knowBaseUrls
    return knowBaseUrls,diseases

#解析每个知识库的内容
def parseKnowBase(knowBaseUrls):
    knowBaseElementUrls = []
    #先取前1个url做实验
    for knowBaseUrl in knowBaseUrls[0:1]:
        print knowBaseUrl
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        #url = "http://disease.medlive.cn/wiki/list/171"
        headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0'}
        request = urllib2.Request(knowBaseUrl, headers = headers)
        response = opener.open(request)
        html = response.read()
        #print response.read()
        soup = BeautifulSoup(html, "lxml")
        #print soup

        #!!!!获取知识库中各元素对应url列表!!!!
        knowBaseElements = soup.find_all(href=re.compile("/wiki/entry/"))
        print knowBaseElements
        for knowBaseElement in knowBaseElements:
            knowBaseElementUrls.append("http://disease.medlive.cn" + knowBaseElement.get('href'))
        #输出知识库中各元素对应url列表
        print knowBaseElementUrls

        #简介、定义、流行病学、病因、病例解剖、病理生理、预防、筛选，
        # 以上网页格式相同，解析方法相同，将以上URL单独列出
        knowBaseElementUrlsParts = []
        knowBaseElementUrlsParts.append(knowBaseElementUrls[0])
        knowBaseElementUrlsParts.append(knowBaseElementUrls[4])
        knowBaseElementUrlsParts.append(knowBaseElementUrls[5])
        knowBaseElementUrlsParts.append(knowBaseElementUrls[6])
        knowBaseElementUrlsParts.append(knowBaseElementUrls[7])
        knowBaseElementUrlsParts.append(knowBaseElementUrls[8])
        knowBaseElementUrlsParts.append(knowBaseElementUrls[10])
        knowBaseElementUrlsParts.append(knowBaseElementUrls[11])
        print knowBaseElementUrlsParts


        #获取以上列表中各元素URL对应的内容
        contents = []
        for knowBaseElementUrlsPart in knowBaseElementUrlsParts:
            print knowBaseElementUrlsPart
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            #url = "http://disease.medlive.cn/wiki/list/171"
            headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0'}
            request = urllib2.Request(knowBaseElementUrlsPart, headers = headers)
            response = opener.open(request)
            html = response.read()
            #print response.read()
            soup = BeautifulSoup(html, "lxml")
            #disease = soup.find.h3.get_text()
            #print disease
            try:
                content = soup.find(attrs={"class":"editor_mirror editor_mirror_del"}).get_text().encode("utf-8")
                contents.append(content)
            #如果该项未被编辑，该项输出"未编辑"
            except:
                content = "未编辑"
                contents.append(content)
            print content
        print contents[0:5]

    #return knowBaseElementUrls
    return contents

#将contents内容导入数据库
def contentsToMySQL(diseases,knowBaseUrls,contents):
    # 打开数据库连接
    db = MySQLdb.connect("localhost","root","root","test", charset = 'utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()  #disease,url,  '%s','%s',
    print contents[0]
    sql = "insert into medlive ( disease, url, summary, defination, epidemiology, pathogeny, pathoanatomy, pathophysiology, precaution, screening ) \
    values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " % (diseases[0],knowBaseUrls[0],contents[0],contents[1],contents[2],contents[3],contents[4],contents[5],contents[6],contents[7])
    cursor.execute(sql)
    db.commit()
    db.close()


if __name__ == '__main__':
    urls = getClassUrl()
    print urls
    detailUrls = getDetailUrl(urls)
    print detailUrls
    print len(detailUrls)
    knowBaseUrls,diseases = knowBaseUrl(detailUrls)
    print knowBaseUrls
    contents = parseKnowBase(knowBaseUrls)
    contentsToMySQL(diseases,knowBaseUrls,contents)