# Bash Brace Expansion in Python
This project is a rough approximation of the curly brace expansion feature from the Bash language, implemented in Python. Note that *no error handling* is included and some Bash specific quirks are intentionally ignored.  
Not supported:
- `{}` empty braces and `{a}` single item braces are treated literally as literals Bash. In this program, `{}` is ignored and `{a}` acts as `a`.

## Examples
To see how curly brace expansion works in Bash, [see Google](https://www.google.com/search?q=bash+curly+brace+expansion). You can play around with it at the terminal with the `echo` command, as in `echo a{1,2,3}`, `echo example{1..9}`, or `echo {a,b}{1,2,3}{x,y{q,w,e}r,z}`.

Run this program as `python3 braceexpansion.py 'a{1,2,3}'`, `python3 braceexpansion.py 'example{1..9}'`, or `python3 braceexpansion.py '{a,b}{1,2,3}{x,y{q,w,e}r,z}'`. You can add the `-d` to see the parsed syntax tree printed out, as in `python3 braceexpansion.py -d 'a{1,2,3}'`. Note the `''` to prevent the shell from doing expansion on the braces.

The expansion functionality can be imported directly:
```python
from braceexpansion import expand
text = 'a{1,2,3}'
result_list = expand(text)
print(*result_list)
```

## Logic
The brace expansion is implemented as a very very simple programming language, represented by this grammar:
```ebnf
expression = {[symbol], [grouping]}
grouping = '{', (expression, {',', expression}) | range, '}'
range = symbol, '..', symbol
symbol = '([a-z][A-Z][0-9]-)+'
```

1. Input string is [lexically scanned](https://en.wikipedia.org/wiki/Lexical_analysis) into a token stream.
2. Token stream is parsed into an [abstract syntax tree](https://en.wikipedia.org/wiki/Abstract_syntax_tree) using a [recursive descent parser](https://en.wikipedia.org/wiki/Recursive_descent_parser) with a one token look-ahead.
3. The abstract syntax tree is evaluated to get the result.
