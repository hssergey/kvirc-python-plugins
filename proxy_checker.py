
import requests, sys
import urllib2, socket

sys.path.append('/home/sergey/programs/kvirc-plugins')
import socks

timeout = 20

def check_dnsbl(ip):
    # API, через который происходит проверка
    url = 'http://www.ip-score.com/ajax_handler/get_bls'
    # Список серверов с блек-листами
    blacklist = [
      'block.dnsbl.sorbs.net', 
      'dnsbl.dronebl.org',
      'dnsbl.sorbs.net', 
      'dul.dnsbl.sorbs.net', 
      'escalations.dnsbl.sorbs.net',
      'http.dnsbl.sorbs.net', 
      'misc.dnsbl.sorbs.net', 'new.dnsbl.sorbs.net',
      'old.dnsbl.sorbs.net',
      'recent.dnsbl.sorbs.net',
      'smtp.dnsbl.sorbs.net', 'socks.dnsbl.sorbs.net',
      'web.dnsbl.sorbs.net', 'zombie.dnsbl.sorbs.net',
    ]
   
    for server in blacklist:
        try:
            # данные, передаваемые через POST
            data = {'ip': ip, 'server': server}
      
            # полученный ответ, timeout 3 секунды (некоторые серверы могут не отвечать)
            response = requests.post(url, data=data, timeout=3)
      
            # проверяем, что код ответа 200
            if response.status_code != 200:
                raise ValueError('Expected 200 OK')
      
            data = response.json()
            # JSON приходит в формате {"сервер": "пусто или IP адрес"}
            # поэтому берем первое значение первого ключа
            rating = data[data.keys()[0]]
            # если значение не пустое, то IP в блек листе
            if rating != "":
                return server
        except:
            # тут обрабатываются различные ошибки, сообщение выводится в STDERR
            sys.stderr.write ("Skip server: " + server + "\n")
    return None


def check_http_proxy(ip, port):
    socket.setdefaulttimeout(timeout)
    try:        
        proxy_handler = urllib2.ProxyHandler({'http': "%s:%s" % (ip, port)})        
        opener = urllib2.build_opener(proxy_handler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib2.install_opener(opener)        
        req=urllib2.Request('http://www.google.com')  # change the url address here
        sock=urllib2.urlopen(req)
    except urllib2.HTTPError, e: 
        return False
    except Exception, detail:
        return False
    return True



def is_socks4(ip, port):
    try:        
        socket.setdefaulttimeout(timeout)
        socks.set_default_proxy(socks.SOCKS4, ip, port = port)
        socket.socket = socks.socksocket
        res = urllib2.urlopen('http://www.google.com').read()
    except urllib2.HTTPError, e: 
        return False
    except Exception, detail:
        return False
    return True
    
def is_socks5(ip, port):
    try:        
        socket.setdefaulttimeout(timeout)
        socks.set_default_proxy(socks.SOCKS5, ip, port = port)
        socket.socket = socks.socksocket
        res = urllib2.urlopen('http://www.google.com').read()
    except urllib2.HTTPError, e: 
        return False
    except Exception, detail:
        return False
    return True


def get_socks_version(host, port):
    if(is_socks4(host, port)):
        return 5
    elif(is_socks5(host, port)):
        return 4
    else:
        return 0


#main


socks_ports = [
    1080,
    1081,
]

http_ports = [
    3128,
    8080,
]

try:
    host = aArgs[2]
    ip = socket.gethostbyname(host)
    kvirc.eval("echo \"Checking host %s ip %s!\"" % (host, ip));
    if check_dnsbl(ip):
        kvirc.eval("echo \"Host %s is in dnsbl!\"" % host);
        sys.exit()
    for port in socks_ports:
        socks_version = get_socks_version(ip, port)
        if socks_version:
            kvirc.eval("echo \"Socks%s proxy detected!\"" % socks_version);
            sys.exit()
    for port in http_ports:
        if check_http_proxy(ip, port):
            kvirc.eval("echo \"HTTP proxy detected!\"");
            sys.exit()
    kvirc.eval("echo \"Checking complete\"");                
except Exception, e:
    kvirc.eval("echo \"exception: %s\"" % str(e));