# build from the base nginx image 
FROM nginx

# copy html to nginx working dir
COPY www /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
COPY fastcgi.conf /etc/nginx/fastcgi.conf

CMD ["nginx","-g", "daemon off;"]