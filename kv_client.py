import socket
import argparse

i = 0
state = '-1'  # 状态未登录，无使用URL命令的权限
try:
    i = i + 1
    parser = argparse.ArgumentParser()
    parser.add_argument('--host',default='localhost')
    parser.add_argument('--port',type=int,default=5678)
    client = socket.socket()
    args = parser.parse_args()
    print(args)
    client.connect((args.host, args.port))
except ConnectionRefusedError:
    print('服务端地址错误或服务端尚未打开!')
    input('---------回车后退出----------')
    exit()
while True:                                                     #运行后循环读取用户输入
    cmd = input('请输入命令:').strip()
    try:
        if not cmd: continue
        elif state == '0' and 'URL' in cmd:                     #错误输入放到了服务端，输入错误命令会从服务端进行提示
            pass                                                #客户端断开后，state自然更新为-1，失去URL权限
        elif state == '-1' and 'URL' in cmd:
            cmd = 'NONE'
        client.send(cmd.encode('utf-8'))
        cmd_receive=client.recv(1024)
        if cmd_receive.decode() == 'ok':
            continue
        else:
            print(cmd_receive.decode())
        if cmd_receive.decode() == '0':                       #返回0时，状态修改，可以使用URL权限
            state = '0'
        elif cmd_receive.decode() == '-1':
            state = "-1"
    except ConnectionResetError:
        print('>>与服务端失去连接')                             #程序应能处理连接服务器失败的情况并给出错误提示。
        exit()
client.close()