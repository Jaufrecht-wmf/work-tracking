SHELL := /bin/bash

all: extract_by_name dndtree

extract_by_name:
        python extract.py bw_user yourname@example.com --output_type json > yourname.treelib.json

dndtree:
	# Use the output name flare.json to work directly with d3 examples with no code editing
        python treelib_json_to_d3.py yourname.treelib.json flare.json --trim 30 --max_depth 3
        cp dndTree.html /var/www/html/index.html
        cp flare.json /var/www/html/
        cp dndTree.js /var/www/html
