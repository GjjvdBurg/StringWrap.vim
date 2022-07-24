
all: test

.PHONY: test

test:
	PYTHONPATH=./python/ python -m unittest ./test/test_string_wrap.py
