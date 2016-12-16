# SBS Play

# Usage

## Run play
Should output play version info

```bash
docker run --rm digiplant/sbsmanager-playframework
```

## Run play dev
Inject current directory into /app and start play
```bash
docker run --rm -it -v $(pwd):/app -p 9000:9000 -p 8000:8000 digiplant/sbsmanager-playframework run
```

## Create production docker image based on playframework

Dockerfile
```docker
FROM digiplant/sbsmanager-playframework

COPY . /app/

CMD ["run", "-Xms3g", "-Xmx3g", "-XX:MaxPermSize=512m", "--%prod"]
```

# Build and publish to docker hub

```bash
// Build image locally
docker build -t digiplant/sbsmanager-playframework .

// Publish image to docker hub
docker push digiplant/sbsmanager-playframework:latest
```