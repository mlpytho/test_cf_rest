#!/usr/bin/bash

sudo docker run --name cft_rest \
    -p 5432:5432 \
    -e POSTGRES_USER=docker \
    -e POSTGRES_DB=docker \
    -e POSTGRES_PASSWORD=mysecretpassword \
    -d postgres
