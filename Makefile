.PHONY: build debug run

build:
	docker build . -t 0x0l/pdfsearch

debug:
	docker run -it --rm -v ${PWD}:/app -e "FLASK_DEBUG=1" -p 5000:5000 0x0l/pdfsearch

run:
	docker run -it --rm -p 5000:5000 0x0l/pdfsearch
