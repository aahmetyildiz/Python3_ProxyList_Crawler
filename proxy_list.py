from lxml import html
import requests


#We can set request header.
headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)", }

#DB connection infos are store at different file
db_file_location = "./"
exec(open(db_file_location + "mysql_connection.py").read())
cursor_db = cnx_db.cursor()

#URL for crawl IP
url = "https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=yes&anonymity=all"

#XPATH for IP data
xpath_ip ='//script[@type="text/javascript"]/text()'
xpath_port ='//*[@id="tblproxy"]//tr/td[3]/a/text()'
xpath_country ='//*[@id="tblproxy"]//tr/td[5]/a/text()'

#URL for control proxy is working.
control_url ='https://www.amazon.com.tr/s?i=electronics&bbn=13709907031&rh=n%3A12466496031%2Cn%3A12466497031%2Cn%3A13709880031%2Cn%3A13709907031%2Cp_6%3AA1UNQM1SR2CHM&s=date-desc-rank&dc&page=1&qid=1561288576&rnid=15358539031&ref=sr_pg_1'



#For insert proxy IPs to DB
def proxy_insert(cursor, data):
    try:
        columns = data.keys()
        joined_columns = ', '.join(data.keys())
        values = [data[column] for column in columns]
        tuple_values = tuple(values)

        if data["status"]==1:
            sql = "INSERT INTO proxy (%s) VALUES %s " % (joined_columns, tuple_values)
            cursor.execute(sql)
            print(data["ip"]+":"+data["port"]+" Added")

            #Delete Proxies previous from last 50
            proxy_delete(cursor, "50")

    except Exception as h:
        hata = str(h)
        if hata.startswith('duplicate key value violates unique constraint'):
            print('This ip:port already have in DB.')
        else:
            print(hata)


#For only last x Proxy IPs stay at DB. Delete previous proxy IPs
def proxy_delete(cursor, count):
    sql = "DELETE FROM proxy WHERE create_time < (SELECT min(bb.create_time) FROM (SELECT cc.create_time FROM proxy cc ORDER BY cc.create_time DESC LIMIT "+count+") bb)"
    cursor.execute(sql)
    cnx_db.commit()



source_code = requests.get(url)
html_text = html.fromstring(source_code.text)
ip_list = source_code.text.splitlines()

i = 0

for ip_port in ip_list:

    print(ip_port)

    ip = ip_port[0:ip_port.find(':')]
    port = ip_port[ip_port.find(':')+1:]

    #If are there any Country info for proxy this field may fill
    country = "-"

    http_proxy = 'http://' + ip + ':'+port
    https_proxy = 'https://' + ip + ':'+port

    proxyDict = {
        "http": http_proxy,
        "https": https_proxy,
    }

    try:
        control_source_code = requests.get(control_url, headers=headers, proxies=proxyDict, timeout=20)
        control_html_text = control_source_code.text

        #"Aranan" is a string from control URL. If there are any "Aranan" string in HTML proxy is working.
        if control_html_text.find('Aranan') > 0:
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

    proxy_insert(cursor_db, data)
    cnx_db.commit()

    #After 100th Proxy job stop.
    if i == 100:
        break

cursor_db.close()
cnx_db.close()