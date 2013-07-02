
clean:
	find . -name '*.pyc' -delete

test:
	nosetests -v

coverage:
	coverage run `which nosetests` -v
	coverage html
	xdg-open htmlcov/index.html

shell:
	python3 -i -c "from lookupy import Collection, Q"

