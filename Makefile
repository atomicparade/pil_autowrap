run:
	rm -rf output
	./pil_autowrap/pil_autowrap.py LOGLEVEL=DEBUG

lint:
	black pil_autowrap
	mypy --strict pil_autowrap
	pylint pil_autowrap

.PHONY: run lint
