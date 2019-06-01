#!/usr/bin/env python
#-*-coding:utf-8-*-
import socket
import rospy
import cv2
import numpy
import pyzbar.pyzbar as pyzbar
from std_msgs.msg import String

with open('/home/park/catkin_ws/src/white_ticket/scripts/tcp_setting.txt') as f:
  TCP_IP = f.readline()[:-1]
  TCP_PORT = int(f.readline()[:-1])

#TCP_IP = 'localhost'
#TCP_PORT = 5005

def recvall(sock, count):
  buf = b''
  while count:
    newbuf = sock.recv(count)
    if not newbuf:
      return None
    buf += newbuf
    count -= len(newbuf)
  return buf

def decode():
  rospy.init_node('decode_node', anonymous=True)
  pub = rospy.Publisher('decode', String, queue_size=10)

  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind((TCP_IP, TCP_PORT))
  s.listen(True)

  conn, addr = s.accept()
  while True:
    len_length = int.from_bytes(conn.recv(1),byteorder='big')
    print("len_length : ", len_length)
    length = int.from_bytes(conn.recv(len_length), byteorder='big')
    stringData = recvall(conn, length)
    data = numpy.fromstring(stringData, dtype='uint8')
    gray=cv2.imdecode(data,0)
    if(str(type(gray))!="<class 'NoneType'>"):
      decoded = pyzbar.decode(gray)
      if(decoded!=None and len(decoded)!=0):
        for d in decoded:
          decode_data = d.data.decode("utf-8")
          print("data :",decode_data)
          decode_data = decode_data.split(',')
          seed = decode_data[0]
          seed = seed.split('}')[0]
          seed = seed.split('=')[1]
          ticket_info = decode_data[2].split(' ')
          row = ticket_info[0][:-1]
          number = ticket_info[1][:-1]
          send_data = seed+','+decode_data[1]+','+row+','+number+','+decode_data[3]
          #if(len(barcode_data)<2):
          # pub.publish('-1')
          # break
          pub.publish(send_data)
          break
      else:
          pub.publish('-1')
      cv2.imshow('SERVER',gray)
      if(cv2.waitKey(1) & 0xFF == ord('q')):
        break
    else:
      print(gray)
      count += 1

if __name__ == '__main__':
  try:
    decode()
  except rospy.ROSInterruptException:
    pass
