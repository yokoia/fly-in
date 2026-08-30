.PHONY: install run debug clean lint

install:
	python3 -m pip install -r developer-deps.txt

run:
	@test -n "$(MAP)" || (echo "Usage: make run MAP=<map_file>" && exit 1)
	python3 play.py "$(MAP)"

debug:
	@test -n "$(MAP)" || (echo "Usage: make debug MAP=<map_file>" && exit 1)
	python3 -m pdb play.py "$(MAP)"

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
