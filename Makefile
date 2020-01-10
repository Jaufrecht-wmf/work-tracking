SHELL := /bin/bash

all: dndtree

dndtree:
	cp dndTree.html target/index.html
	cp airtable.d3.json target/flare.json
	cp dndTree.js target/
