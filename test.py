import vk_api
import json
from main import send_info_message, analyse_new_nodes
from keys import api_key as token

hostlist = analyse_new_nodes('./saves/analyse_38.xml')

peer_id=113742536

vk=vk_api.VkApi(token=token)
dataset= json.load(open('./known_IPs.json', 'r', encoding='utf-8'))

send_info_message(hostlist, dataset)
