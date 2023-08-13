read -p "This script is for deploying GameGuard panel on server. Do you want to continue? Y/n (default: n): " command
if [[ $command != 'Y' ]]
then
	exit
fi

apt update && apt upgrade -y
apt install nginx apache2-utils sqlite3 build-essential python3-pip python3-dev python3-certbot-nginx -y

pip3 install django uwsgi python-dotenv django-apscheduler apscheduler

ln -s ~/.local/bin/uwsgi /usr/bin/
ln -s /etc/x-ui/x-ui.db .
mkdir /var/log/uwsgi

read -p "Enter your domain for SSL certification: " domain
read -p "Enter username for htpasswd: " username
htpasswd -c /etc/nginx/.htpasswd $username

echo """
upstream django {
	server 127.0.0.1:8001;
}

server {
	listen 80;
	server_name $domain;

	location /static {
		root /var/www/html;
	}

	location / {
		uwsgi_pass  django;
		auth_basic	\"Restricted Content\";
		auth_basic_user_file /etc/nginx/.htpasswd;
		include     /etc/nginx/uwsgi_params;
	}
}
""" > /etc/nginx/sites-available/VPN
ln -s /etc/nginx/sites-available/VPN /etc/nginx/sites-enabled
certbot --nginx -d $domain

bash renew.sh
nginx -s reload
python3 manage.py createsuperuser
python3 manage.py collectstatic

echo """
[uwsgi]
chdir=$(pwd)
module=VPN.wsgi:application
socket=127.0.0.1:8001
master=True
processes=5
harakiri=20
vacuum=True
max-requests=5000
daemonize=/var/log/uwsgi/VPN.log
""" > VPN.ini
uwsgi --enable-threads --ini VPN.ini
