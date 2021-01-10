from lxml import html
import requests
import json
import os
import pytz
import sys
from datetime import datetime
import time
import signal


class TimeoutException(Exception):
    pass


def _timeout(signum, frame):
    raise TimeoutException()

#signal.signal(signal.SIGALRM, _timeout)



file_location = "D:\Proje Python/karaca/"
#file_location = "/home/python/karaca/"
exec(open(file_location + "configuration.py").read())
cursor_karaca = cnx_karaca.cursor()


LCK_FILE = file_location + "proxy_list_tr.lck"


if os.path.exists(LCK_FILE):

    file_read = open(LCK_FILE, 'r')
    old_time = file_read.read()
    old_time = datetime.strptime(old_time, '%Y-%m-%d %H:%M:%S %z')

    c_time = datetime.replace(datetime.now(), tzinfo=pytz.timezone(TIME_ZONE))
    c_time = datetime.strftime(c_time, '%Y-%m-%d %H:%M:%S %z')
    c_time = datetime.strptime(c_time, '%Y-%m-%d %H:%M:%S %z')

    second = c_time - old_time
    second = second.total_seconds()

    if second > 1800:
        print('LCK Dosyası Zamanaşımı!')
        os.remove(LCK_FILE)
        c_time = datetime.replace(datetime.now(), tzinfo=pytz.timezone(TIME_ZONE))
        c_time = datetime.strftime(c_time, '%Y-%m-%d %H:%M:%S %z')
        file_write = open(LCK_FILE, 'w')
        file_write.write(c_time)
        file_write.close()
        print('Yeni LCK Dosyası Oluşturuldu')

    else:
        print("LCK dosyası var. (İşlem çalışıyor)")
        sys.exit(0)


else:
    c_time = datetime.replace(datetime.now(), tzinfo=pytz.timezone(TIME_ZONE))
    c_time = datetime.strftime(c_time, '%Y-%m-%d %H:%M:%S %z')
    file_write = open(LCK_FILE, 'w')
    file_write.write(c_time)
    file_write.close()
    print('LCK Dosyası Oluşturuldu')


encoding = "utf-8"

"""
url = "https://www.proxy-list.download/api/v0/get?l=en&t=https"
xpath_ip ="//tr/td[1]/font[2]/text()"
xpath_port ="//tr/td[1]/font[2]/text()"
xpath_country ="//tr/td[4]//font/text()"
"""
url = "https://api.proxyscrape.com/?request=getproxies&proxytype=https&timeout=10000&country=tr&ssl=all&anonymity=all"
xpath_ip ='//script[@type="text/javascript"]/text()'
xpath_port ='//*[@id="tblproxy"]//tr/td[3]/a/text()'
xpath_country ='//*[@id="tblproxy"]//tr/td[5]/a/text()'


hb_url ='https://www.amazon.com.tr/s?i=electronics&bbn=13709907031&rh=n%3A12466496031%2Cn%3A12466497031%2Cn%3A13709880031%2Cn%3A13709907031%2Cp_6%3AA1UNQM1SR2CHM&s=date-desc-rank&dc&page=1&qid=1561288576&rnid=15358539031&ref=sr_pg_1'


source_code = requests.get(url)
html_text = html.fromstring(source_code.text)
ip_list = source_code.text.splitlines()

#ip_list = html_text.xpath(xpath_ip)
#port_list = html_text.xpath(xpath_port)
#country_list = html_text.xpath(xpath_country)
#ip_list_json = json.loads(ip_list)
#ip_list = ip_list_json[0]["LISTA"]




def link_insert(cursor, data):
    try:
        columns = data.keys()
        joined_columns = ', '.join(data.keys())
        values = [data[column] for column in columns]
        tuple_values = tuple(values)

        if data["status"]==1:
            sql = "INSERT INTO proxy (%s) VALUES %s " % (joined_columns, tuple_values)
            cursor.execute(sql)
            print(data["ip"]+":"+data["port"]+" Eklendi")
            link_delete(cursor, "50")

    except Exception as h:
        hata = str(h)
        if hata.startswith('duplicate key value violates unique constraint'):
            print('Bu ip:port sistemde kayÄ±tlÄ±.')
        else:
            print(hata)

def link_delete(cursor, count):
    sql = "DELETE FROM proxy WHERE create_time < (SELECT min(bb.create_time) FROM (SELECT cc.create_time FROM proxy cc ORDER BY cc.create_time DESC LIMIT "+count+") bb)"
    cursor.execute(sql)
    cnx_karaca.commit()

i = 0
for ip_port in ip_list:
#for i in range(0, len(ip_list)):
    print(ip_port)
    #ip = ip_list[i]["PROXY_IP"]
    ip = ip_port[0:ip_port.find(':')]

    #port = ip_list[i]["PROXY_PORT"]
    port = ip_port[ip_port.find(':')+1:]

    #country = ip_list[i]["PROXY_COUNTRY"]
    country = "TR"

    http_proxy = 'http://' + ip + ':'+port
    https_proxy = 'https://' + ip + ':'+port


    proxyDict = {
        "http": http_proxy,
        "https": https_proxy,
    }


    try:
        hb_source_code = requests.get(hb_url, headers=headers, proxies=proxyDict, timeout=20)
        hb_html_text = hb_source_code.text


        if hb_html_text.find('<ul class="product-list') > 0:
            status = 1
        else:
            status = 0

    except:
        status = -1

    data = {
        "ip": ip,
        "port": port,
        "country": country,
        "status": status,
    }
    print(data)
    i += 1
    link_insert(cursor_karaca, data)
    cnx_karaca.commit()
    if i == 100:
        break


cursor_karaca.close()
cnx_karaca.close()

os.remove(LCK_FILE)
