import socket
import re
import argparse
import os
import json
from threading import Thread
import requests

#打开配置文件(账户和密码)
jud = os.path.exists('auth.conf')           #文件按字典格式记录,如需添加用户,请按照格式添加
if jud == True:
    pass
else:
    h = open('auth.conf','w')
    h.close()
cal = {}                         #定义储存用户key-value的字典
account = {}                                #定义用户账号密码字典
line_get = []
f = open('auth.conf','r')
js = f.read()
account = json.loads(js)
print(account)                  #打印出具有URL命令的用户名和密码

#创建服务端
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
parser = argparse.ArgumentParser()
parser.add_argument('--host',default='localhost')
parser.add_argument('--port',type=int,default=5678)
args = parser.parse_args()
print(args)
server.bind((args.host, args.port))      #默认连接5678
server.listen(5)               #进行TCP监听,请求数为5个
# count = 0                 #设置消息的接受个数

#设置多线程，以便于多个客户端同时连接
def tcplink(coon,addr):
    while True:
        try:                            #防止客户端崩溃而导致服务端崩溃
            data = conn.recv(1024)
            d = data.decode()
            print(d)                                                #反馈客户端的信息
            if not data:
                print('Lost Connect')
                break

            elif 'GET' in d:                       #GET命令：从字典cal中获取key相对应的值
                try:
                    p = re.compile('(.+) (.+)')
                    b = p.search(d)
                    print('执行命令GET')
                    key = b.group(2)
                    value = cal[key]
                    conn.send(value.encode('utf-8'))
                except AttributeError:                           #输入错误的带有GET的命令进行提示
                    conn.send('Your command is wrong'.encode('utf-8'))
                except KeyError:                                 #不存在key时进行提示None
                    conn.send(' '.encode('utf-8'))

            elif 'SET' in d:                        #SET命令：接收key-value，储存到字典cal中
                try:
                    p = re.compile('(.+) (.+) (.+)')
                    b = p.search(d)
                    print('执行命令SET')
                    key = b.group(2)                    #如果 key 已经持有其他值，SET 就覆写旧值。
                    value = b.group(3)
                    cal[key] = value
                    conn.send('ok'.encode('utf-8'))
                except AttributeError:
                    conn.send('Your command is wrong.'.encode('utf-8'))

            elif 'AUTH' in d:
                try:
                    p = re.compile('(.+) (.+) (.+)')
                    b = p.search(d)
                    print('执行命令AUTH')
                    account_recv = b.group(2)
                    password_recv = b.group(3)
                    password = account[account_recv]
                    print(password)
                    if password_recv == password:
                        conn.send('0'.encode('utf-8'))
                    else:
                        conn.send('-1'.encode('utf-8'))
                except AttributeError:
                    conn.send('Your command is wrong.'.encode('utf-8'))
                except KeyError:                                 #不存在该用户时进行提示None
                    conn.send('-1'.encode('utf-8'))

            elif 'URL' in d:
                try:
                    p = re.compile('(.+) (.+) (.+)')
                    b = p.search(d)
                    net = b.group(3)
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
                    response = requests.post(net,headers=headers)                   #伪装HTTP头部，防止无法访问
                    content = response.headers['Content-Length']
                    content = str(content)
                    print(content)
                    key = b.group(2)
                    judge = key in cal.keys()
                    if judge == True:                                            #如果key存在值就返回已有值
                        value = cal[key]
                        conn.send(value.encode('utf-8'))
                    else:                                                       #如果key不存在就写入改值，并返回该值
                        cal[key] = content
                        conn.send(content.encode('utf-8'))
                except AttributeError:
                    conn.send('Your command is wrong.'.encode('utf-8'))
                except requests.exceptions.InvalidURL:
                    conn.send('Your website is wrong.'.encode('utf-8'))
                except requests.exceptions.MissingSchema:
                    conn.send('Your website is wrong.'.encode('utf-8'))

            elif d == 'NONE':
                conn.send(' '.encode('utf-8'))

            else:
                conn.send('Wrong Command,please enter again and check your command.'.encode('utf-8'))
            # count += 1
            # if count>=10:                   #限制发送10次消息
            #     conn.send('Too more command,you lost connect.'.encode('utf-8'))
            #     break
        except ConnectionResetError:
            break

#客户端登陆功能
#实现服务端命令的功能
while True:
    conn, addr = server.accept()
    print('客户端连接: ', addr)
    t = Thread(target=tcplink, args=(conn,addr))                #新的线程,新的客户端使用
    t.start()
server.close()