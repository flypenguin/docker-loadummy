build-one:
	docker build . -f Dockerfile
.PHONY: build-one

build-all:
	export COLORS="orange red blue green yellow magenta navy white black" ; \
	docker build -t flypenguin/test . ; \
	for COLOR in $$COLORS ; do \
	    export COLOR ; \
		docker build \
		    --build-arg ENV_COLOR=$$COLOR \
			-t flypenguin/test:$$COLOR \
			-f Dockerfile.color \
			. ; \
	done ;
.PHONY: build-all
