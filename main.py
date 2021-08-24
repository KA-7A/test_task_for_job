########################################################
#
# Тестовая прога в MyOffice: сканирует пингами сеть, потом
# анализирует, собирает всю информацию из xml файлов и от-
# правляет всё это дело в вк.
########################################################
#
# Usage: python3 main.py [mode]
# mode - необязательный параметр.
# 0: прога пропустит сканирования и отправит результаты пос-
# леднего анализа
# 1: запустится в дефолтном режиме
#
########################################################
import os
from time import sleep
import keys				# Тут лежат ключи от VkApi
import datetime
import json

import subprocess			# Нужно чтобы запускать bash скрипты через питон

from host_info_class import hostInfo	# Тут лежит класс, в котором содержится вся инфа о хосте: IP, открытыеЪ фильтруемые поры
from utilities import *			# Тут лежат исходники всех функций, кроме всего, что касается отправки картинок
from pictures import *			# Тут лежат исходники функций, посвящённых формированию и отправке картинок
########################################################
# Не менять! После переезда в отдельный файл, было лениво сделать всё по человечески, предстоит немного работы напильником
PICTURES = False
########################################################

def main():
    START_FLAG = True			# Флаг для mode (смотри описание в шапке файла)
    parser = createParser()
    namespace = parser.parse_args (sys.argv[1:])	# Парсим аргументы командной строки
    if int(namespace.mode) == 0:
        START_FLAG = False

    flag = True
    with open('./known_IPs.json', 'r', encoding='utf-8') as file:	# Открываем служебный JSON. kIPs - IP для которых анализ готов, nIPs - новые адреса
        data_set = json.load(file)
        print_all_ips_to_file(data_set)
    while True:
        try:
            if START_FLAG == False:  # Это в случае, если мы не хотим, чтобы длинный анализ шел заново после перезагрузки программы
                filename = './saves/analyse_' + str(data_set['num']) + '.xml'
                hostsList = analyse_new_nodes(filename)
                send_info_message(hostsList, data_set)
                START_FLAG = True
                continue

            else:
                if datetime.time(1, 0, 0) <= datetime.datetime.now().time() <= datetime.time(2, 30, 0):	# Раз в сутки сбрасываем всю инфу, чтобы новая машина не встала на чужой IP и мы её не пропустили
                    if flag:
                        print("##### Освобождаем пул адресов ##### (его можно найти тут './old_IP_pool.txt'")
                        message = ""
                        with open('./old_IP_pool.txt', 'w', encoding='utf-8') as file:
                            for i in data_set["kIPs"]:
                                message += i + "\n"
                                print(i, file=file)
                        data_set["kIPs"] = []
                        send_message("Пул адресов сброшен. Вот список ранее известных адресов:\n" + message)
                        save_state(data_set)	# Фунция сохранения нашего JSON
                        flag = False
                else:
                    flag = True
                subprocess.call("./ping_scan.sh")	# Устраиваем ping сканирование. Результат в './tmp.xml'
                message = parse_tmp_xml(data_set, 'tmp.xml')	# Обновляем наш JSON

                if message != "":  # Чтобы не получать пустые сообщения и не перезаписывать файл лишний раз (на случай, если ping сканирование не выявило новых адресов)
                    send_message("Вот новые адреса:\n" + message + "\nПосле более подробного анализа будет отправлен дополнительный отчет.\n\nХорошего дня.")
                    save_state(data_set)

                if len(data_set["nIPs"]) != 0: 	# Если нашлись новые адреса, то запускаем -sV -A анализ
                    print("Найдено ", len(data_set["nIPs"]), " новых узлов в сети. Просканируем их более подробно.")
                    with open('./ip_to_check.txt', 'w', encoding='utf-8') as file:  # Закинули адреса в файл на проверку
                        for i in data_set["nIPs"]:
                            print(i, file=file)

                    subprocess.call("./sV_A_analyse.sh")
                    filename = './saves/analyse_' + str(data_set['num']) + '.xml'
                    hostsList = analyse_new_nodes(filename)	# Эта функция парсит наш xml отчет на список из экземпляров класса со всей инфой

                    send_info_message(hostsList, data_set)	# Отправляем сообщение

                    if PICTURES:    #TODO Сделать всё так, чтобы оно работало. Не знаю, зачем, но было бы неплохо. А сейчас это лучше не трогать
                        send_pictures(hostlList, data_set)

			# Ну, тут вроде понятно, что происходит.
                    data_set["num"] += 1
                    with open('./num.txt', 'w', encoding='utf-8') as file:
                        print(data_set["num"], file=file)
                    data_set["kIPs"] += data_set["nIPs"]
                    data_set["nIPs"] = []
                    save_state(data_set)

                else:
                    print("Новых узлов не найдено, увидимся через час")
                    sleep(3600)
        except Exception as e:
            print("Exception: ", e, ". Try to reload bot")
            send_message("Что-то опять пошло не так, пробуем перезагрузиться")
            continue


if __name__ == '__main__':
    main()
