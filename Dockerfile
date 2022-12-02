FROM python:3

RUN apt-get update
RUN apt-get -y install wget systemctl

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY Makefile .

COPY core core
COPY auth auth
COPY utils utils
COPY settings settings

#RUN mkdir ~/.postgresql
#COPY root.crt /root/.postgresql/root.crt

EXPOSE 8000

CMD [ "make" , "run" ]