![image](https://user-images.githubusercontent.com/25791237/198873887-f01f9f69-5a1d-4a5f-95cf-1f1d6dfb63fb.png)


# Mamushi
[![image](https://img.shields.io/pypi/v/mamushi.svg)](https://pypi.org/project/mamushi/)
[![Build Status](https://github.com/benber86/mamushi/actions/workflows/test.yml/badge.svg)](https://github.com/benber86/mamushi/actions)
[![codecov](https://codecov.io/github/benber86/mamushi/branch/main/graph/badge.svg?token=WF0YO4ACIT)](https://codecov.io/github/benber86/mamushi)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)



Mamushi is a fork of the popular [Black](https://github.com/psf/black) formatter adapted to the [Vyper](https://github.com/vyperlang/vyper/) programming language. Mamushi reformats your Vyper contracts in a readable and consistent way.


## Installation

`pip install mamushi`

## Usage

Search all *.vy files and overwrite them after formatting:

`mamushi`

Specify a list of *.vy files or directories and output to console after formatting:

`mamushi [SRC]`

Output the result to console instead of overwriting:


`mamushi --in-place False`


## Notes

#### Line length

The default line length is 80. Line length can be adjusted by using the `--line-length` option.

#### AST Safety
By default, mamushi will compare the AST of your reformatted code with that of the original to ensure that the changes applied remain strictly formal. The option can be disabled with `--safe False` to speed things up.


#### Trailing commas

When handling expressions split by commas, mamushi follows Black's [default behavior](https://test-black.readthedocs.io/en/style-guide/style_guide/trailing_commas.html).

Mamushi also uses Black's [magic trailing comma](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html#pragmatism) to give user the option to collapse a comma-separated expression into one line if possible. If a trailing comma is added, mamushi will always explode the expression. This can have important consequences for the commenting of your code. Consider the following two examples:

This code snippet:

```
self.b(0, # amount to send
       msg.sender, # sender
       True, # refund ?
        )
```

formats to the following with a trailing comma after the last argument (`True`):

```
self.b(
    0,  # amount to send
    msg.sender,  # sender
    True,  # refund ?
)
```

but if the trailing comma is removed, the line will be collapsed to:

```
self.b(0, msg.sender, True)  # amount to send  # sender  # refund ?
```

## Future developments

- [ ] Multiprocessing when processing multiple files
- [ ] Configuration files
- [ ] Improve Windows compatibility
- [ ] Handle versioning of Vyper/lark grammar
- [ ] Refactoring comment handling in the parser
- [ ] Add .gitignore / exclude / include support

