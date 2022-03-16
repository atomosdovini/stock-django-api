# Celery

Guia de como instalar e rodar o Celery junto ao Rabbitmq para adicionar tasks e o serviço de organização por fila à aplicação Django.

## Install

Guia para implantação, necessário somente a instalação da biblioteca do Celery via pip e e do Rabbitmq

### Celery

        pip install celery

### Rabbitmq

       sudo apt-get install rabbitmq-server 

## Run

### Rabbitmq

        sudo systemctl enable rabbitmq-server

        sudo systemctl start rabbitmq-server

### Celery

        celery -A backend worker -l info

### Teste

### Rabbitmq

        systemctl status rabbitmq-server

### Celery

Para testar somente pare o serviço do Rabbit, se o setup estiver correto haverá um erro no terminal do celery

        sudo rabbitmqctl stop