# Mamushi

[![Build Status](https://github.com/benber86/mamushi/actions/workflows/test.yml/badge.svg)](https://github.com/benber86/mamushi/actions)

Mamushi is a fork of the popular [Black](https://github.com/psf/black) formatter adapted to the [Vyper](https://github.com/vyperlang/vyper/) programming language. Mamushi reformats your Vyper contracts in a readable and consistent way.


### Installation

`pip install -e .`

### Usage

Search all *.vy files and overwrite them after formatting:

`mamushi --in-place`

Specify a list of *.vy files or directories and output to console after formatting:

`mamushi [SRC]`

### Options

By default, mamushi will compare the AST of your reformatted code with that of the original to ensure that the changes applied remain strictly formal. The option can be disabled with `--safe False` to speed things up.
