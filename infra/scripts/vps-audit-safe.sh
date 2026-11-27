#!/usr/bin/env bash
# Read-only VPS inventory. Output is designed for a public report and excludes
# secret values. Review output manually before committing it.

set -u

section() {
  printf '\n## %s\n' "$1"
}

section SYSTEM
date -Is
hostnamectl | sed -E \
  -e 's/^( *Static hostname:).*/\1 [REDACTED_HOSTNAME]/' \
  -e '/Machine ID:/d' \
  -e '/Boot ID:/d'
uptime -p
timedatectl show -p Timezone --value
test -f /var/run/reboot-required && echo 'reboot-required: yes' || echo 'reboot-required: no'

section RESOURCES
lscpu | grep -E '^(Architecture|CPU\(s\)|Model name|Thread|Core|Socket|Virtualization|Hypervisor vendor)'
free -h
swapon --show
lsblk -o NAME,SIZE,FSTYPE,TYPE,MOUNTPOINTS
df -hT -x tmpfs -x devtmpfs

section NETWORK
ip -br addr | sed -E 's/([0-9]{1,3}\.){3}[0-9]{1,3}/[REDACTED_IPV4]/g'
ss -lntup
ufw status verbose

section SECURITY
sshd -T 2>/dev/null | grep -E \
  '^(port|permitrootlogin|passwordauthentication|pubkeyauthentication|maxauthtries|x11forwarding|clientaliveinterval|clientalivecountmax) ' | sort
systemctl is-active fail2ban 2>/dev/null || true
fail2ban-client status 2>/dev/null || true
apparmor_status 2>/dev/null | head -n 8

section SERVICES
systemctl list-units --type=service --state=running --no-pager --no-legend | awk '{print $1}'
systemctl --failed --no-pager --no-legend

section DOCKER
docker version --format 'client={{.Client.Version}} server={{.Server.Version}}'
docker compose ls
docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}'
for container in $(docker ps -aq); do
  docker inspect --format \
    'name={{.Name}} image={{.Config.Image}} restart={{.HostConfig.RestartPolicy.Name}} user={{.Config.User}} readonly_rootfs={{.HostConfig.ReadonlyRootfs}} network={{.HostConfig.NetworkMode}}' \
    "$container"
  docker inspect --format \
    'mounts={{range .Mounts}}{{.Type}}:{{.Source}}->{{.Destination}}(rw={{.RW}});{{end}}' \
    "$container"
  printf 'env_names='
  docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' "$container" \
    | cut -d= -f1 | sort | paste -sd ',' -
done
docker system df

section WEB_DATABASE
nginx -v 2>&1
nginx -t
find /etc/nginx/sites-enabled -maxdepth 1 -type l -printf '%f\n' 2>/dev/null
certbot certificates 2>/dev/null | grep -E 'Certificate Name:|Domains:|Expiry Date:' || true
psql --version
sudo -u postgres psql -Atc \
  "SELECT datname || '|' || pg_size_pretty(pg_database_size(datname)) FROM pg_database WHERE datistemplate = false ORDER BY datname;"

section PACKAGES
printf 'installed-deb: '
dpkg-query -W -f='${binary:Package}\n' | wc -l
printf 'upgradable: '
apt list --upgradable 2>/dev/null | tail -n +2 | wc -l
printf 'unattended-upgrades: '
systemctl is-enabled unattended-upgrades.service 2>/dev/null || true
