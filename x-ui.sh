read -p "This script is for installing x-ui panel on server. Do you want to continue? Y/n (default: n): " command
if [[ $command != 'Y' ]]
then
	exit
fi

apt update && apt upgrade -y && apt autoremove -y
apt install curl socat nodejs npm -y
npm install pm2 -g

curl https://get.acme.sh | sh
~/.acme.sh/acme.sh --set-default-ca --server letsencrypt

read -p "Enter your email for SSL certificate: " email
~/.acme.sh/acme.sh --register-account -m $email

read -p "Enter your domain: " domain
~/.acme.sh/acme.sh --issue -d $domain --standalone
~/.acme.sh/acme.sh --installcert -d $domain --key-file /root/private.key --fullchain-file /root/cert.crt

printf "Which x-ui panel you want to install?\n1. vaxilu\n2. FranzKafkaYu\n"
read -p "Your choice (default: vaxilu): " command
if [[ $command == '2' ]]
then
	bash <(curl -Ls https://raw.githubusercontent.com/FranzKafkaYu/x-ui/master/install_en.sh)
else
	bash <(curl -Ls https://raw.githubusercontent.com/vaxilu/x-ui/master/install.sh)
fi

curl -LO https://raw.githubusercontent.com/bootmortis/iran-hosted-domains/main/scripts/update_iran_dat.sh
curl -LO https://raw.githubusercontent.com/jinwyp/one_click_script/master/install_kernel.sh

CRON_JOB="0 0 * * 2 $(pwd)/update_iran_dat.sh /usr/local/x-ui/bin/iran.dat"
(crontab -l 2>/dev/null; echo "$CRON_JOB > /dev/null 2>&1") | crontab -
bash update_iran_dat.sh /usr/local/x-ui/bin/iran.dat
