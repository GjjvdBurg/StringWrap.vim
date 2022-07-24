let s:plugin_root_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')

fun! <SID>StringWrap(args) range
python3 << endpython
import sys
import vim
import os

# Import the python functionality
plugin_root_dir = vim.eval("s:plugin_root_dir")
python_root_dir = os.path.join(plugin_root_dir, "..", "python")
python_root_dir = os.path.normpath(python_root_dir)

# Insert the python dir into sys.path so we can import it
sys.path.insert(0, python_root_dir)
import string_wrap

# Get the values we need from vim
buf = vim.current.buffer
line_idx = int(vim.eval('line(".")')) - 1
line = buf[line_idx]
text_width = int(vim.eval("&textwidth"))

# Wrap the lines
lines = string_wrap.string_wrap(line, text_width)

# Insert the result
if not lines is None:
  buf[line_idx] = lines[0]
  buf.append(lines[1:], line_idx+1)

endpython
endfun

fun! <SID>StringUnwrap(args) range
python3 << endpython
import sys
import vim
import os

# Import the python functionality
plugin_root_dir = vim.eval("s:plugin_root_dir")
python_root_dir = os.path.join(plugin_root_dir, "..", "python")
python_root_dir = os.path.normpath(python_root_dir)

# Insert the python dir into sys.path so we can import it
sys.path.insert(0, python_root_dir)
import string_wrap

# Get the values we need from vim
buf = vim.current.buffer
(line_index_start, col_start) = buf.mark('<')
(line_index_end, col_end) = buf.mark('>')
lines = vim.eval('getline({},{})'.format(line_index_start, line_index_end))

# Unwrap the lines
lines = string_wrap.string_unwrap(lines)

# Insert the result
if not lines is None:
  del buf[line_index_start-1:line_index_end]
  buf.append(lines, line_index_start-1)

endpython
endfun

fun! <SID>StringRewrap(args) range
python3 << endpython
import sys
import vim
import os

# Import the python functionality
plugin_root_dir = vim.eval("s:plugin_root_dir")
python_root_dir = os.path.join(plugin_root_dir, "..", "python")
python_root_dir = os.path.normpath(python_root_dir)

# Insert the python dir into sys.path so we can import it
sys.path.insert(0, python_root_dir)
import string_wrap

# Get the values we need from vim
buf = vim.current.buffer
(line_index_start, col_start) = buf.mark('<')
(line_index_end, col_end) = buf.mark('>')
lines = vim.eval('getline({},{})'.format(line_index_start, line_index_end))

# Rewrap the lines
lines = string_wrap.string_rewrap(lines)

# Insert the result
if not lines is None:
  del buf[line_index_start-1:line_index_end]
  buf.append(lines, line_index_start-1)

endpython
endfun

command! -nargs=? -range StringWrap call <SID>StringWrap(<q-args>)
command! -nargs=? -range StringUnwrap call <SID>StringUnwrap(<q-args>)
command! -nargs=? -range StringRewrap call <SID>StringRewrap(<q-args>)
