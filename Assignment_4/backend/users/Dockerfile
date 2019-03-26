FROM alpine:3.7

WORKDIR /users
COPY . /users

RUN apk add --update \
	python3 \
	python3-dev \
	&& pip3 install --no-cache-dir --upgrade pip \
	&& pip3 install pymongo \
	&& pip3 install Flask

EXPOSE 8080
ENV TEAM_ID="CC_251_277_302_396"

CMD ["python3", "app.py"]
