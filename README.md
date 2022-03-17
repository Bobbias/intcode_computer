# Intcode Computer

This is a python implementation of an [Intcode](https://esolangs.org/wiki/Intcode) VM.

This repo also contains several solutions for the Advent of Code 2019 along with the Intcode VM.

## Running

This project assumes the user has some python knowledge. To run any of the included solutions, simply replace the main function in `main.py` with the function for a given solution. For example:

```python
if __name__ == '__main__':
    run_day7_part1() # change this line to select which solution to run.
    pass
```

## Building documentation

Documentation is generated using [Sphinx](https://www.sphinx-doc.org/en/master/).

Building the documentation is easy.

### Linux

Run the command `make html` in the documentation folder.

### Windows

Run the command `make.bat html` in the documentation folder. Use `./make.bat html` instead if you're using powershell.