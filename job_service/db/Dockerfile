FROM postgres
ENV POSTGRES_DB job_service_db
ARG POSTGRES_PASSWORD
ENV POSTGRES_PASSWORD=$POSTGRES_PASSWORD
COPY jobservice_db.sql /docker-entrypoint-initdb.d/

