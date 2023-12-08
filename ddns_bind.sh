#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/
LOG="/tmp/log_dns.log"
IP6=$(ip -6 a list ppp0 |grep inet6 |grep dynam | awk {'print $2'} | cut -d / -f 1)

if [ -z $IP6 ]; then
echo "`date` - IP6 Não Encontrado" >> $LOG
exit 0
fi

# Configurações
ZONA="YOUR_ZONE"                          # Domínio que você deseja atualizar
DOMAIN="YOUR_SUBDOMAIN"
SERVIDOR_DNS="YOUR_DNS_IP"          # Endereço IP do servidor DNS BIND9
CHAVE="YOUR_DNS_KEY"                    # chave DDNS configurada no BIND9

FILE=/tmp/udpate.txt

NM=$(dig AAAA $DOMAIN.$ZONA @$SERVIDOR_DNS |grep ' ANSWER SECTION:' -A1 |tail -1 |awk {'print $5'})

if [ $NM = $IP6 ]; then
echo  "`date` - IP atual" >> $LOG
exit 0
fi

# Comandos nsupdate
echo "server $SERVIDOR_DNS" > $FILE
echo "zone $ZONA" >> $FILE
echo "update delete $DOMAIN.$ZONA. AAAA" >> $FILE
echo "update add $DOMAIN.$ZONA. 3600 AAAA $IP6" >> $FILE
echo "send" >> $FILE

nsupdate -y $CHAVE -v $FILE
