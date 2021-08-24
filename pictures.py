####################################################################
#
# Кусок кода, посвящённый формированию и отправке графиков с состоянием
# сети (какие порты открыты/фильтруются + открытые порты у каждого соединения)
# Мне лень постфактум комментировать этот кусок кода, поскольку
# А: Он не используется в силу исключительной трудозатратности этого метода
# Б: Он не используется в силу некорректного переноса этого куска файла из main.py 
# В: Я не прокомментировал это раньше
#
# Спешу обнадёжить читающего, что если он просмотрел исходники остальных файлов,
# то ему не составит труда разобраться в написанном, потому что де-факто здесь всё то же самое:
# бесконечный парсинг xml, работа со списками, работа с VkAPI + работа с matplotlib
#
####################################################################

import matplotlib.pyplot as plt
import vk_api
import keys
import random

def send_pictures(hostlList, data_set):     # TODO Допилить этот кусок правильно, но вообще он не очень нужен
    vk = vk_api.VkApi(token=keys.api_key)
    if not flag:
        for i in hostsList:
            if i.getIPadress() in data_set["nIPs"]:
                port_opn, port_flt, port_ids = opened_ports_count()
                if len(port_opn) + len(port_flt) > 2:
                    open_ports_count_v2(filename, i.getIPadress(), port_opn, port_flt, port_ids)
                    data = vk.method('photos.getMessagesUploadServer', {'peer_id': 0})
                    upload_url = data['upload_url']
                    name = './pictures/fig' + i.getIPadress() + '.png'
                    files = {'photo': open(name, 'rb')}
                    response = requests.post(upload_url, files=files)
                    result = json.loads(response.text)
                    uploadResult = vk.method('photos.saveMessagesPhoto',
                                            {'server': result["server"], 'photo': result["photo"],
                                            'hash': result["hash"]})
                    attach = "photo" + str(uploadResult[0]["owner_id"]) + "_" + str(uploadResult[0]["id"])
                    vk.method('messages.send',
                            {'peer_id': peer_id, 'message': "", 'random_id': random.randint(1, 10000),
                            'attachment': attach})
    subprocess.call("./clear_pictures.sh")  # Удаляем весь мусор за собой

def opened_ports_count(filename):
    data = ET.parse(filename).getroot()
    out_data = []
    ind = 0
    # Дурацкий парсинг XML.. Но ничего лучше пока не придумал :%)
    for find_host in data:
        # print("find_host ",find_host.tag, find_host.attrib) # host {'starttime': '1620235931', 'endtime': '1620241883'}
        if find_host.tag == 'host':
            host = find_host
            addr = ""
            ports_list = []
            for find_ports in host:
                # print("find_ports ", find_ports.tag, find_ports.attrib)
                if find_ports.tag == 'address' and find_ports.attrib['addr']:
                    addr = find_ports.attrib['addr']

                if find_ports.tag == 'ports':
                    ports = find_ports
                    for port in ports:
                        # print("port in ports ", port.tag, port.attrib) # port {'protocol': 'tcp', 'portid': '625'}
                        for elem in port:
                            # print("elem ", elem.tag, elem.attrib)
                            if elem.tag == 'state':
                                # print(addr, port.attrib['portid'], elem.attrib['state'])

                                ports_list.append((port.attrib['portid'], elem.attrib['state']))
                        # print()
            out_data.append((addr, ports_list))
            ind += 1
        # print()
    port_ids = []  #
    port_opn = []  # Сколько раз порт открыт
    port_flt = []  # Сколько раз порт фильтруется

	#########################################
	#					#
	#	Рекламное место свободно!	#
	#          +7(977)770-28-08		#
	#              Кирилл			#
	#					#
	#########################################

    for i in range(len(out_data)):
        # print("addr: ", out_data[i][0])
        for j in out_data[i][1]:
            # print(j[0], j[1])
            port_id = j[0]
            port_stat = j[1]
            flag = True
            for ind in range(len(port_ids)):
                if port_id == port_ids[ind]:
                    flag = False
                    if port_stat == 'open':
                        port_opn[ind] += 1
                    else:
                        port_flt[ind] += 1
            if flag:
                port_ids.append(port_id)
                if port_stat == 'open':
                    port_opn.append(1)
                    port_flt.append(0)
                else:
                    port_opn.append(0)
                    port_flt.append(1)
        # print()
    # print(port_opn, port_flt, port_ids)
    return port_opn, port_flt, port_ids


def open_ports_count_v2(filename, needed_IP, port_open, port_fltd, port__ids):
    data = ET.parse(filename).getroot()
    flag = False
    needed_open_ports = []
    needed_fltd_ports = []
    for findTag in data:
        if findTag.tag == 'host':
            for findTag_2 in findTag:
                if findTag_2.tag == 'address':
                    if findTag_2.attrib['addr'] == needed_IP:
                        flag = True  # Флаг подтверждает, что мы нашли нужный адрес
                if flag and findTag_2.tag == 'ports':
                    ports = findTag_2
                    for port in ports:
                        # print("port in ports ", port.tag, port.attrib) # port {'protocol': 'tcp', 'portid': '625'}
                        for elem in port:
                            # print("elem ", elem.tag, elem.attrib)
                            if elem.tag == 'state':
                                if elem.attrib['state'] == 'open':
                                    needed_open_ports.append(port.attrib['portid'])
                                    # print(needed_open_ports[-1])
                                else:
                                    needed_fltd_ports.append(port.attrib['portid'])
                                    # print(needed_fltd_ports[-1])
                    break
        if flag:
            break
    fig, ax = plt.subplots()
    ax.bar(port__ids, port_open, label='Открытые порты в известном пуле')
    ax.bar(port__ids, port_fltd, width=0.5, label='Отфильтрованные порты в известном пуле')
    ax.bar(needed_open_ports, 55, width=0.3, label='Открытые порты в заданном адресе')
    ax.bar(needed_fltd_ports, 60, width=0.2, label='Отфильтрованные порты в заданном адресе')
    ax.legend(loc='upper right')
    ax.set_facecolor('seashell')
    fig.set_figwidth(12)  # ширина Figure
    fig.set_figheight(6)  # высота Figure
    fig.set_facecolor('floralwhite')
    # fig.autofmt_xdate()

    plt.suptitle("opened, filtered ports for " + needed_IP + " compared with another known adresses")

    plt.xticks(rotation=90)
    fname = './pictures/fig' + needed_IP + '.png'
    plt.savefig(fname=fname)
    # plt.show()
    return fname
    pass
