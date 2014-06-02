

ifndef PYTHON
	PYTHON=python3.3
endif

all:
	cc -shared -std=gnu99 -fPIC -lX11 -I/usr/include/$(PYTHON) -o xwrapper.so xwrapper.c

clean:
	rm xwrapper.so
