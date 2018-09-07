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
	-e TZ=<timezone>
	wiserain/makerss
```

초기화 과정을 진행하고 phantomjs를 띄워서 준비 상태가 됩니다.

```/config```와 매핑된 폴더에 ```config.yml``` 파일이 준비되어 있습니다. 사이트를 주석 처리하거나 게시판을 추가하여 자신만의 설정을 저장하고 아래 명령어를 실행합니다. (yaml 형식으로 되어 있으니 편집할때 참고 바랍니다.)

```bash
docker exec -it <container name> makerss_run
```

백그라운드 실행은 ```-it``` 대신 ```-d```를 입력합니다.

### Cronjob

환경변수를 통해 컨테이너 내부의 crontab을 설정할 수 있습니다. 가장 앞의 5개 인자(분시일월주)만 입력하면 됩니다. 예외 처리가 되어 있지 않으니 참고해 주세요.

```bash
-e CRONTAB="* * * * *"
```
