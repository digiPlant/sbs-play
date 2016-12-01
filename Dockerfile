FROM openjdk:8-jdk-alpine

# Install deps
RUN apk update && apk upgrade \
	&& apk --no-cache add --virtual build-dependencies unzip \
	&& apk --no-cache add curl python

# Delete caches
RUN apk del --purge build-dependencies \
	&& rm -fr /var/cache/apk/*

# Create workdir
RUN mkdir -p /app

# Add playframework to image
COPY . /opt/play

# Add play to path so that the "play" command is available
ENV PATH /opt/play:$PATH

WORKDIR /app

# Play default port
EXPOSE 9000

# Debug port
EXPOSE 8000

ENTRYPOINT ["play"]

CMD ["help"]
