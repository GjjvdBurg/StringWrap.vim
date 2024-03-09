
all: test

.PHONY: test testdefault test38

test: testdefault test38

testdefault:
	PYTHONPATH=./python/ python -m unittest -v ./test/test_string_wrap.py

test38:
	PYTHONPATH=./python/ python3.8 -m unittest -v test/test_string_wrap.py
