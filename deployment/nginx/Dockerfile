FROM nginx:1.27-alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY deployment/nginx/*.conf /etc/nginx/conf.d/
RUN mkdir -p /etc/nginx/certs
EXPOSE 80 443
STOPSIGNAL SIGQUIT
