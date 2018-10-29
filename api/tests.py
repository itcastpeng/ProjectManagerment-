from django.test import TestCase

# Create your tests here.





import random
# import socket
# # 获取本机 HOST
# host = socket.gethostname()
# port = 8000
# s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# s.bind((host,port))
# s.listen(1)
# sock,addr = s.accept()
# print('Connection built')
# info = sock.recv(1024).decode()
# while True:
#     print(sock)
#     print('李四:' + info)
#     send_mes = input()
#     # if send_mes:
#     print('====> ', send_mes)
#     sock.send(send_mes.encode())
#     # if send_mes =='exit':
#     #     break
#     info = sock.recv(1024).decode()
# sock.close()
# s.close()


# seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
# sa = []
# for i in range(32):
#     sa.append(random.choice(seed))
# salt = ''.join(sa)
# print('salt------->',salt)
#
# import uuid
# str(uuid.uuid4()).replace('-', '')