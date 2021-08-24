######################################################
#
#	В этом большом блоке лежит имплементация всех функций, которые используются в main.py
#
######################################################

import vk_api
import keys	# Ключи для использования VkApi
import xml.etree.ElementTree as ET # Парсим-парсим xml
import json
import random
from time import sleep

from host_info_class import hostInfo # См. описание в main.py

import sys
import argparse

def createParser ():		# Парсим аргументы командной строки
    parser = argparse.ArgumentParser()
    parser.add_argument ('mode', nargs='?', default=1)
    return parser

def send_message(message):	# Отправляем сообщение в вк с текстом message
    vk = vk_api.VkApi(token=keys.api_key)
    vk.method('messages.send', {'peer_id':keys.peer_id, 'random_id':random.randint(1,10000), 'message':message})

def analyse_new_nodes(filename): # Парсим xml файл filename и достаём нужную инфу, а именно:
    hostList = []

    numFile = 0
    new_state = ET.parse(filename).getroot()
    for child in new_state:
        if child.tag == 'host':
            tmp = hostInfo()
            for findTag in child:
                if findTag.tag == 'address':
                    tmp.setIPadress(findTag.attrib['addr'])	# Получаем IP адрес
                if findTag.tag == 'ports':
                    for findPort in findTag:
                        if findPort.tag == 'port':
                            for j in findPort:
                                if j.tag == 'state':
                                    if j.attrib['state'] == 'open':	# Получаем список открытых порторв
                                        tmp.addOpenPort(findPort.attrib['portid'])
                                    elif j.attrib['state'] == 'filtered':	# И фильтруемых портов
                                        tmp.addFilteredPort(findPort.attrib['portid'])
                if findTag.tag == 'os':				# По возможности, ищем имя ОС, на которой работает хост
                    for i in findTag:
                        if i.tag == 'osmatch':
                            tmp.setOSname(i.attrib['name'] + " " + i.attrib['accuracy'])
                            break
            hostList.append(tmp)
    return hostList


def save_state(state):	# Сохраняем JSON
    with open('./known_IPs.json', 'w', encoding='utf-8') as file:
        json.dump(state, file, indent=4)


def print_all_ips_to_file(state): # Костыль для связывания работы python и sh скрипта. nmap умеет доставать IP для анализа из файла, так что пользуемся этим и заполняем файл
    with open('./saves/all_ips.txt', 'w', encoding='utf-8') as file:
        for i in state["kIPs"]:
            print(i, file=file)


def send_info_message(hostsList, data_set):	# Функция, которая готовит текст сообщения для отправки.
    message = "Отчет по новым адресам:\n"
    for i in range(len(hostsList)):
        if i % 30 == 0:
            if i != 0:  # Это нужно, чтобы не отправлялись слишком длинные сообщения, вк такого не любит
                send_message(message)
                sleep(0.1)
                message=""
        message += hostsList[i].getInfo()
    send_message(message)

    message = "Итог\nПодозрительные соединения:\n"
    for i in range(len(hostsList)):
        if hostsList[i].getWarning():
            message+=hostsList[i].getIPadress() + "\n"
    send_message(message)

def parse_tmp_xml(data_set, filename): # Парсит xml, полученный после ping сканирования сети
    message = ""
    new_data = ET.parse(filename).getroot()
    for child in new_data:
        for smth in child:
            if smth.tag == "address":
                # print(smth.attrib['addr'])
                IP_addr = smth.attrib['addr']
                if IP_addr not in data_set["kIPs"] and IP_addr not in data_set["nIPs"]:
                    message += IP_addr + "\n"
                    data_set["nIPs"].append(IP_addr)
    return message
