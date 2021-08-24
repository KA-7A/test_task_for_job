#!/bin/sh

i=`cat num.txt`
echo Начало анализа конфигурации неизвестных хостов. Модификации анализа: -sV -A
# Анализируем все возможные и невозможные порты
nmap -oX ./saves/analyse_$i.xml -sV -A -p 1-65535 -iL  ip_to_check.txt >/dev/null
# nmap -oX ./saves/analyse_$i.xml -sV -A -p 1-10 -iL  ip_to_check.txt >/dev/null # Только для ускорения тестов :)
# Дальше трансформируем текст из сплошного в читаемый
cat ./saves/analyse_$i.xml | xmllint --format - > ./tmp.xml
cat ./tmp.xml > ./saves/analyse_$i.xml
echo Анализ завершен, отчёт будет отправлен в ВК скором времени.
