FROM alpine:3.7

WORKDIR /acts
COPY . /acts

RUN apk add --update \
	python3 \
	python3-dev \
	&& pip3 install --no-cache-dir --upgrade pip \
	&& pip3 install pymongo \
	&& pip3 install Flask \
	&& pip3 install requests

ENV TEAM_ID="CC_251_277_302_396"

EXPOSE 8000

CMD ["python3", "app.py"]
