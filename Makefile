CODE = core
SRC = .


lint:
	flake8 --jobs 4 --statistics --max-line-length=119 $(SRC)
	mypy $(SRC)
	python3 -m black --target-version py310 --skip-string-normalization --line-length=119 --check $(SRC)

pretty:
	python3 -m isort .
	python3 -m black --target-version py310 --skip-string-normalization --line-length=119 $(SRC)
	python3 -m unify --in-place --recursive $(CODE)

plint: pretty lint

run:
	uvicorn $(CODE).app:app --host 0.0.0.0 --port 8000