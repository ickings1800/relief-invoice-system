FROM nginx:1.17.4-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY ./docker/prod/nginx/nginx.conf /etc/nginx/conf.d/

WORKDIR /static/

## add permissions for nginx user
RUN chown -R nginx:nginx /static && chmod -R 755 /static && \
        chown -R nginx:nginx /var/cache/nginx && \
        chown -R nginx:nginx /var/log/nginx && \
        chown -R nginx:nginx /etc/nginx/conf.d
RUN touch /var/run/nginx.pid && \
        chown -R nginx:nginx /var/run/nginx.pid

USER nginx