# pull official base image
FROM python:3.8.1

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get -y install netcat lsb-release


RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y wget gnupg \
 && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
 && echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> tee  /etc/apt/sources.list.d/pgdg.list

ENV PG_VERSION=11 

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y acl sudo locales \
      postgresql-${PG_VERSION} postgresql-client-${PG_VERSION} postgresql-contrib-${PG_VERSION} postgis postgresql-${PG_VERSION}-postgis-2.5

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt


# copy project
COPY . /usr/src/app/

# run docker-entrypoint.sh
ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]