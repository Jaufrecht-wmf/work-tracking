SHELL := /bin/bash

all: dndtree

dndtree:
	cp dndTree.html target/index.html
	cp flare.json target/flare.json
	cp dndTree.js target/
