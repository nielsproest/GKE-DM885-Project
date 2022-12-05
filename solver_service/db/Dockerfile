FROM postgres
ENV POSTGRES_PASSWORD psltest
ENV POSTGRES_DB solver_service_db
COPY solver_service_db.sql /docker-entrypoint-initdb.d/

