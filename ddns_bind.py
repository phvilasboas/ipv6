#!/usr/bin/env python3
import subprocess
from datetime import datetime

LOG = "/tmp/log_dns.log"
ZONA = "YOUR_ZONE"  # Domínio que você deseja atualizar
DOMAIN = "YOUR_SUBDOMAIN"
SERVIDOR_DNS = "YOUR_DNS_IP"  # Endereço IP do servidor DNS BIND9
CHAVE = "YOUR_DNS_KEY"  # chave DDNS configurada no BIND9

# Obtendo o endereço IPv6 da interface ppp0
result = subprocess.run(["ip", "-6", "a", "list", "ppp0"], capture_output=True, text=True)
ip6_lines = result.stdout.split('\n')
IP6 = None
for line in ip6_lines:
    if "inet6" in line and "dynam" in line:
        IP6 = line.split()[1].split('/')[0]
        break

if IP6 is None:
    with open(LOG, "a") as log_file:
        log_file.write(f"{datetime.now()} - IP6 Não Encontrado\n")
    exit(0)

# Consultando o endereço IPv6 atual do subdomínio no servidor DNS
result = subprocess.run(["dig", "AAAA", f"{DOMAIN}.{ZONA}", f"@{SERVIDOR_DNS}"], capture_output=True, text=True)
dig_output = result.stdout
NM = dig_output.split("ANSWER SECTION:")[-1].split()[-1]

if NM == IP6:
    with open(LOG, "a") as log_file:
        log_file.write(f"{datetime.now()} - IP atual\n")
    exit(0)

# Criando o arquivo de atualização para o nsupdate
update_commands = [
    f"server {SERVIDOR_DNS}",
    f"zone {ZONA}",
    f"update delete {DOMAIN}.{ZONA}. AAAA",
    f"update add {DOMAIN}.{ZONA}. 3600 AAAA {IP6}",
    "send"
]

with open("/tmp/update.txt", "w") as update_file:
    update_file.write('\n'.join(update_commands))

# Executando o nsupdate
result = subprocess.run(["nsupdate", "-y", CHAVE, "-v", "/tmp/update.txt"])

# Você pode adicionar tratamento de erro ou registrar em um log em caso de falha no nsupdate
