
all: test

.PHONY: test

test:
	PYTHONPATH=./python/ python -m unittest -v ./test/test_string_wrap.py
