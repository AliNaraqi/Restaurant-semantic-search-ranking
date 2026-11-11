.PHONY: setup data indexes train eval web all

setup:
	python -m pip install -r requirements.txt

data:
	python scripts/prepare_data.py

indexes:
	python scripts/build_indexes.py

train:
	python scripts/train_ltr.py

eval:
	python scripts/evaluate.py

web:
	OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 bash scripts/run_web.sh

all: data indexes train eval
