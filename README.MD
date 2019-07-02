# NOTE: 此项目属于蓝鲸敏感数据，请勿泄漏

# Init environment and start the service

## step 1, mkvirtualenv and install sdk
mkvirtualenv op_esb_template
pip install -r requirements.txt 

## step 2, create database, update DATABASES in settings.py and syncdb
create database op_esb_template CHARACTER SET utf8;
GRANT ALL PRIVILEGES ON op_esb_template.* TO 'op_esb_template'@'127.0.0.1' IDENTIFIED BY 'op_esb_template'; 
python manage.py migrate 

## step 3, runserver
python manage.py runserver

## step 4, unittest
python manage.py test --keepdb tests.components.apis.test_cmdb.TestCMDB.test_get_biz_by_id
