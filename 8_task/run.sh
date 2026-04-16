#!/bin/bash

case "$1" in
    start)
        docker start postgres-container
        docker start parser-container
        docker start nginx-proxy 2>/dev/null || \
        docker run -d \
          --name nginx-proxy \
          --network parser-network \
          -p 80:80 \
          -v $(pwd)/nginx_proxy.conf:/etc/nginx/nginx.conf:ro \
          -v $(pwd)/nginx/geoip:/etc/nginx/geoip:ro \
          -v $(pwd)/nginx/blocked.html:/usr/share/nginx/html/blocked.html:ro \
          nginx:alpine
        docker ps
        ;;
    stop)
        docker stop nginx-proxy parser-container postgres-container
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        ;;
esac