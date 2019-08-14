![rustcov][100]

Rustcov is an embarrasingly simple, tiny little script I created for myself
which helps generating coverage report of Rust projects.  It is written in
Python.

## Requirements

- [`python`][110] (3.7+)
- [`kcov`][120]
- [`xdg-open`][130]

## Installation

1. Install requirements:
   ```bash
   $ pip install -r requirements.txt
   ```
2. Install `rustcov`:
   ```bash
   $ bash install.sh
   ```
3. _Happy, happy, joy, joy!_

## License

Copyright &copy; 2019 **Peter Varo**

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program, most likely a file in the root directory, called 'LICENSE'.
If not, see [http://www.gnu.org/licenses][200].

<!-- links -->
[100]: img/rustcov.png?raw=true "rustcov"
[110]: https://www.python.org/downloads
[120]: https://simonkagstrom.github.io/kcov
[130]: https://linux.die.net/man/1/xdg-open
[200]: http://www.gnu.org/licenses
