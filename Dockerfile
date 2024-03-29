#Docker file for local building and serving only
FROM ubuntu:16.04
MAINTAINER James Scott-Brown <james@jamesscottbrown.com>

RUN apt-get update
RUN apt-get install wget curl -y


WORKDIR /root

# dReal
RUN curl -L -o dReal-3.16.09.01-linux.tar.gz https://github.com/dreal/dreal3/archive/v3.16.09.01.tar.gz
RUN tar -zxvf dReal-3.16.09.01-linux.tar.gz

# MathSAT
RUN wget http://mathsat.fbk.eu/release/mathsat-5.5.1-linux-x86_64.tar.gz
RUN tar -zxvf mathsat-5.5.1-linux-x86_64.tar.gz

# iSAT binary
RUN wget http://www.avacs.org/fileadmin/tooladmin/open/isat-ode.tar.gz
RUN tar -zxvf isat-ode.tar.gz


## This site
RUN apt-get install -y python binutils g++ make sqlite3 python-pip git

RUN pip install --upgrade pip

ADD ./requirements /requirements
RUN pip install -r /requirements/dev.txt 

CMD bash
