frontend: cli_frontend.c
	gcc cli_frontend.c -o cli_frontend \
    -I/usr/include/python3.13 \
    -lpython3.13 \
    -lpthread -lm -ldl -lutil

CC = gcc
CFLAGS = -Wall -g `pkg-config --cflags gtk+-3.0`
LDFLAGS = `pkg-config --libs gtk+-3.0` -pthread

gtk_client: test-gtk.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

.PHONY: all clean
clean: rm cli_frontend
	rm -f gtk_client

all: frontend

