# work-tracking
Tools for reporting from and updating WMF work tracking systems

# Installation

## Create Python environment
Create a Python 3.6 or higher virtualenv and install necessary libraries via pip.

```bash
python3.8 -m venv ~/.venv_example_path
source ~/.venv_example_path/bin/activate
pip install -r requirements.txt
```

## Configure with private API keys
The extract script depends on API key to identify and authenticate to end points and get access to data. BetterWorks API access requires an API token specific to a BetterWorks account.  Airtable API access required an API key specific to an Airtable user.

Betterworks API token are provided by technical support. Airtable API keys can be found in your [Airtable Account page](https://airtable.com/account). 

These scripts accept private keys either through the environment or the command line.  The easiest method is to store them in the script that creates the python virtual environment; if so, **be sure that you are not exposing this information by, for example, storing your virtual envirnoment files in a public code repository.** Add these lines to ~/.venv_example_path/bin/activate
```bash
export BETTERWORKS_API_TOKEN=yourtokenhere
export AIRTABLE_API_KEY=yourkeyhere
```

# Usage

## Data Extraction

### Get BetterWorks goals tree for a user
```python extract.py bw_user youremail@wikimedia.org```

Retrieves all goals (Objectives and Key Results) owned by the user, and all goals that are descendents of those goals.  Descendents includes all direct children, i.e., Key Deliverables that roll up to an Objective, and all alignment relationships created in BetterWorks.

### Get BetterWorks goals tree for a goal
```python extract.py bw_goal 1234567890```

Retrieves all goals (Objectives and Key Results) that are descendents of the indicated.  Definition of descendent is the same as by user.

### Get Airtable complete Priority tree
```python extract.py airtable 1234567890```

Retrieves a work breakdown tree combining Priorition, Outcomes, Key Deliverables, OKRs, Projects, and Activities from the WMF Medium-term Plan, Annual Plan, and other planning documents and systems.  Tied to a specific table and field structure.

## Data output

### As ASCII tree
Shows the tree as indented plain text.

### As JSON
As a JSON file—representing the [treelib](https://treelib.readthedocs.io/en/latest/) data structure—that includes all extracted data.
```python extract.py airtable 1234567890 --output_type json > tree123.treelib.json```

### As CSV
A flat list of nodes, with each node naming its parent.

### As GraphViz data
In the graphviz 'dot' format.


## Visualization

### In D3
Many visualization tools use D3 javascript as a fundamental library in the browser stack.  The hierarchical JSON provided by the treelib library is slightly different from the tree format typically used in hierarchical D3 reports, as exemplified by the flare.json sample file.  The ```treelib_json_to_d3.py``` script converts the output of ```extract.py``` to be ready to load in D3 tools.  It can also shorten the node names and/or truncate the tree at a fixed depth, which can be helpful if the final report does not perform these functions.

#### Preparing the data
1. Run extract.py to generate json output.  For traceability, name it something like foo.treelib.json.
2. ```python treelib_json_to_d3.py foo.treelib.json foo.d3.json```

#### Publishing
D3 reports are viewed in web browsers.  Security issues with javascript may mean that they have to be viewed from a webserver, or even an HTTPS webserver, rather than being loaded from a local file.  If so, quick notes:

1. Set up a local webserver
..1. ```sudo apt install nginx``` or apache2
2. set up file permissions
..1. ```sudo usermod -a -G www-data username```  Add the www-data group to the account used to run the extract scripts.  log the affected user account and back in for the group change to take effect.
..1. ``` sudo chgrp www-data /var/www/html```  Change the default web data directory to belong to the www-data group.
..1. ```sudo chmod g+S /var/www/html``` Modify the default web data directory so that all new files automatically belong to the www-data group.
3. Edit the Makefile to set up the data extraction, editing, and publication chain
4. ```make```
