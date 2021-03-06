# docker-makerss

[makerss](https://github.com/soju6jan/soju6jan.github.io/tree/master/makerss)를 실행하기 위한 도커 이미지. [참고](https://www.clien.net/service/board/cm_nas/12534455)

## Usage

먼저 아래 명령어를 참고하여 백그라운드에서 컨테이너를 실행합니다.

```bash
docker run -d \
	--name=<container name> \
	-v <path to config>:/config \
	-v <path to generated rssxml>:/rssxml \
	-e PUID=<UID for user> \
	-e PGID=<GID for user> \
	wiserain/makerss
```

초기화 과정을 진행하고 phantomjs를 띄워서 준비 상태가 됩니다.

```/config```와 매핑된 폴더에 ```makerss_*.py``` 파일이 준비되어 있습니다. 사이트를 주석 처리하거나 게시판을 추가하여 자신만의 설정을 저장하고 아래 명령어를 실행합니다. (자세한 내용은 상단의 설명 참고)

```bash
docker exec -it <container name> makerss_run
```

백그라운드 실행은 ```-it``` 대신 ```-d```를 입력합니다.
