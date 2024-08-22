## verilog translator

Translate verilog to a circuitsim file.

### credits

Thanks to:
 - Yosys
 - especially https://yosyshq.readthedocs.io/projects/yosys/en/latest/using_yosys/synthesis/cell_libs.html

### setup

```
# make a venv
$ python -m venv .venv
$ . .venv/bin/activate  # on *nix
$ ./.venv/Scripts/activate  # on Windows
# install dependencies
$ pip install -r requirements.txt
```

Then, make a verilog file called `in.v` in this directory.

### Running

```
$ python translate.py
```

Then, open `circuit.sim` in this directory.
