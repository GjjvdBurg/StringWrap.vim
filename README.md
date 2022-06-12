# StringWrap.vim

This is a *very* simple Vim plugin to wrap or unwrap long strings (mainly 
intended for Python). It will help you turn this:

```python
a = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
)
```

into this (select the string or stand on the line and run `:StringWrap`):
```python
a = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod "
    "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim "
    "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea "
    "commodo consequat. Duis aute irure dolor in reprehenderit in voluptate "
    "velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint "
    "occaecat cupidatat non proident, sunt in culpa qui officia deserunt "
    "mollit anim id est laborum."
)
```

and back again (using visual selection and `:StringUnwrap`). The maximum width 
is equal to your Vim `textwidth` setting. It will not work if the string is 
not on its own line.

## Installation

Using Vundle:

```vim
Plugin 'gjjvdburg/StringWrap.vim'
```

## Notes

For licensing information, see the LICENSE file.

To run the tests, use:
```
PYTHONPATH=./python/ python -m unittest test/test_string_wrap.py
```

Written by [Gertjan van den Burg](https://gertjan.dev)
