frontend: cli_frontend.c
	gcc cli_frontend.c -o cli_frontend \
    -I/usr/include/python3.13 \
    -lpython3.13 \
    -lpthread -lm -ldl -lutil

clean: rm cli_frontend

all: frontend

