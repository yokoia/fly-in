
.PHONY: install run debug clean lint lint-strict

install:
    pip install flake8 mypy pygame

run:
    python3 main.py $(FILE)

debug:
    python3 -m pdb main.py

clean:
    rm -rf pycache .mypy_cache .pytest_cache dist mazegen.egg-info
    find . -type d -name "pycache" -exec rm -rf {} + 2>/dev/null  true
    find . -type f -name "*.pyc" -delete 2>/dev/null  true

lint:
    flake8 .
    mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
    flake8 .
    mypy . --strict