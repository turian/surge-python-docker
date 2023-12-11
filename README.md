# surge-python-docker

Surge synthesizer through Python, dockerized.

```
docker pull turian/surge-python:latest-arm64
# Or, build the docker yourself
#docker build -t turian/surge-python:latest-arm64 -f Dockerfile-arm64 . --push
docker run --rm --mount source=`pwd`/output,target=/home/surge/output,type=bind -it turian/surge-python bash
```

```
docker buildx create --name mybuilder --use
docker buildx inspect --bootstrap
docker buildx ls


docker buildx build --platform linux/arm64,linux/amd64 -t turian/surge-python:latest --push .
```


```
docker build -t turian/surge-python:ubuntu2204-arm64 -f Dockerfile-arm64-ubuntu22.04 . --push
docker build -t turian/surge-python:latest-arm64 -f Dockerfile-arm64 . --push
```

Within docker:
```
# Check quickly that you have surgepy working
./example.py
# Generate all patches with all notes in the MIDI range of a grand
# piano writing ogg files to output/
./run.py
```
