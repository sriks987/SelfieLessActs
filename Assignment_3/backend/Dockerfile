FROM alpine:3.7

WORKDIR /users
COPY . /users


RUN apk add --update \
    python3 \
    python3-dev \
  && pip3 install --no-cache-dir --upgrade pip \
  && pip3 install pymongo \
  && pip3 install Flask \
  && pip3 install mongoengine

# RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.6/main' >> /etc/apk/repositories
# RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.6/community' >> /etc/apk/repositories
# RUN apk update
# RUN apk add mongodb=3.4.4-r0
# RUN mongo --version

RUN apk add --no-cache mongodb su-exec
RUN mkdir -p /data/db

VOLUME [ "/data/db" ]

EXPOSE 27017 27017

ENTRYPOINT [ "start.sh" ]

EXPOSE 8080

CMD ["service", "mongod", "start"]
CMD ["python3", "app.py"]
