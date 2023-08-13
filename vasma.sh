read -p "This script is for installing vasma script on server. Do you want to continue? Y/n (default: n): " command
if [[ $command != 'Y' ]]
then
	exit
fi

apt update && apt upgrade -y
apt install ufw

ufw allow ssh
ufw allow http
ufw allow https
ufw enable

curl -LO https://raw.githubusercontent.com/jinwyp/one_click_script/master/install_kernel.sh

bash <(curl -Ls https://raw.githubusercontent.com/mack-a/v2ray-agent/master/install.sh)
bash <(curl -Ls https://gitlab.com/rwkgyg/CFwarp/raw/main/CFwarp.sh)
