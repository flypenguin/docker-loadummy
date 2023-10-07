CONTAINER_NAME = flypenguin/test
COLORS = orange red blue green yellow magenta navy white black
RUN_COLOR = white

build-one:
	docker build -t $(CONTAINER_NAME) -f Dockerfile .
.PHONY: build-one

build-all: build-one
	# https://is.gd/jxU0eq
	for COLOR in $(COLORS) ; do \
		docker buildx build --platform linux/amd64 \
		    --build-arg TAG_COLOR=$$COLOR \
			-t $(CONTAINER_NAME):$$COLOR \
			-f Dockerfile.color \
			. ; \
	done ;
.PHONY: build-all

push: build
	docker push $(CONTAINER_NAME)
.PHONY: push

push-all: build-all
	docker push $(CONTAINER_NAME)
	echo $(COLORS) | tr " " "\n" | parallel docker push $(CONTAINER_NAME):{}
.PHONY: push-all

upload: push
.PHONY: upload

upload-all: push
.PHONY: upload-all

build: build-all
.PHONY: build

run: build-one
	docker run --rm -e FLASK_PORT=8000 -e COLOR=$(RUN_COLOR) -p 8000:8000 $(CONTAINER_NAME)
.PHONY: run


orange: RUN_COLOR=orange
orange: run
.PHONY: orange

red: RUN_COLOR=red
red: run
.PHONY: red

blue: RUN_COLOR=blue
blue: run
.PHONY: blue

green: RUN_COLOR=green
green: run
.PHONY: green

yellow: RUN_COLOR=yellow
yellow: run
.PHONY: yellow

magenta: RUN_COLOR=magenta
magenta: run
.PHONY: magenta

navy: RUN_COLOR=navy
navy: run
.PHONY: navy

white: RUN_COLOR=white
white: run
.PHONY: white

black: RUN_COLOR=black
black: run
.PHONY: black
