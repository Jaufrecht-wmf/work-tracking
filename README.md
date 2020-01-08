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

### As CSV
A flat list of nodes, with each node naming its parent.

### As GraphViz data
In the graphviz 'dot' format.
