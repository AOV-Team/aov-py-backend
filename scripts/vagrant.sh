#!/usr/bin/env bash

echo "Installing packages..."
sudo apt-get install --reinstall software-properties-common -y > /dev/null 2>&1
echo | sudo add-apt-repository ppa:fkrull/deadsnakes > /dev/null 2>&1
sudo apt-get update > /dev/null 2>&1
sudo apt-get install python3.5 -y > /dev/null 2>&1

sudo apt-get install python3-pip python3.5-dev libffi-dev libpq-dev \
nginx python-virtualenv libjpeg8 libjpeg62-dev libfreetype6 \
libfreetype6-dev build-essential binutils libproj-dev gdal-bin -y > /dev/null 2>&1

sudo apt-get install postgresql postgresql-contrib postgis postgresql-9.3-postgis-2.1 -y > /dev/null 2>&1
sudo apt-get build-dep python-imaging -y > /dev/null 2>&1

# Set up virtual environment and env variables
mkdir virtualenvs
sudo pip3 install virtualenv virtualenvwrapper > /dev/null 2>&1
printf "\n\n# Virtualenv settings\n" >> ~vagrant/.bash_profile
printf "export WORKON_HOME=~vagrant/virtualenvs\n" >> ~vagrant/.bash_profile
printf "export PROJECT_HOME=/vagrant\n" >> ~vagrant/.bash_profile
printf "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3\n" >> ~vagrant/.bash_profile
printf "source /usr/local/bin/virtualenvwrapper.sh\n" >> ~vagrant/.bash_profile
source ~vagrant/.bash_profile > /dev/null 2>&1

# Aliases
printf "\n# Useful Aliases:\n" >> ~vagrant/.bash_profile
printf "alias runserver='python manage.py runserver 0.0.0.0:8000'\n" >> ~vagrant/.bash_profile
printf "alias test='python manage.py test -v2'\n" >> ~vagrant/.bash_profile
printf "alias coveragetest='coverage run --source='apps' manage.py test'\n" >> ~vagrant/.bash_profile
mkvirtualenv --python=python3.5 backend > /dev/null 2>&1

# Set up db
sudo -u postgres bash -c "psql -c \"CREATE USER djangodev WITH PASSWORD 'golden';\""
sudo -u postgres bash -c "psql -c \"CREATE DATABASE aov WITH OWNER djangodev;\""
sudo -u postgres bash -c "psql -c \"ALTER USER djangodev WITH SUPERUSER;\""

# Set up project deps
echo "Setting up project"
cd /vagrant
setvirtualenvproject
workon backend
pip install -r requirements.txt > /dev/null 2>&1
./scripts/setup.sh dev > /dev/null
./manage.py migrate
pip install coverage
pip install django-debug-toolbar

# Redis
echo "Installing Redis"
./scripts/install_redis.sh > /dev/null 2>&1
redis-server --daemonize yes
sudo printf "\nbind 0.0.0.0" >> /etc/redis/6379.conf
sudo /etc/init.d/redis_6379 restart

# Set virtualenvs owner
sudo chown -R vagrant:vagrant ~vagrant/virtualenvs