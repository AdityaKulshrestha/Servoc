SHELL:=/bin/bash


setup:
	sudo docker build -t servoc:latest .


start:
	sudo docker run -d -p 8081:8080 -p 5555:5555 --cpuset-cpus="0-31" --cpuset-mems="0"  -v ./models:/app/models/ --privileged --name servoc_container_1 servoc:latest && \
	sudo docker run -d -p 8082:8080 -p 5556:5555 --cpuset-cpus="32-63" --cpuset-mems="1" -v ./models:/app/models --privileged --name servoc_container_2 servoc:latest && \
	cd deployment/haproxy && sudo docker run -d --name servoc-haproxy --add-host=host.docker.internal:host-gateway -v ./haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro -p 8080:8080 -p 8404:8404 servoc_haproxy_image

stop:
	sudo docker stop servoc-haproxy && sudo docker rm servoc-haproxy && \
	sudo docker stop servoc_container_1 && sudo docker rm servoc_container_1 && \
	sudo docker stop servoc_container_2 && sudo docker rm servoc_container_2
