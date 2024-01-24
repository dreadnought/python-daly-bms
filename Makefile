package-build:
	python3 setup.py sdist bdist_wheel
	twine check dist/*`python3 setup.py --version`*
package-upload:
	twine upload --repository dalybms dist/*`python3 setup.py --version`*
package-commit:
	git commit -m "Version `python3 setup.py --version`"
	git tag "v`python3 setup.py --version`"
	git push
	git push --tags
