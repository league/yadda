FROM ubuntu:14.04
MAINTAINER Christopher League <league@contrapunctus.net>
RUN apt-get install -y python
RUN mkdir /app
ADD servery /app/server.py
VOLUME /logs
EXPOSE 8000
CMD /app/server.py /logs/access.log
