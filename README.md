# s7-cdd-g1
Python project to understand the osi model. UNEMI assignment. 4th semestrer, Information technologies.

## Run

```bash
python app.py
```

The simulator uses a Tkinter desktop interface.

## Test

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Project structure

- `app.py`: interactive mission selector.
- `missions/*.py`: each OSI mission is defined in a separate file.
- `simulator/`: shared engine, models, and terminal UI for encapsulation/decapsulation simulation.
