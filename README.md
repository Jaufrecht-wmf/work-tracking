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

## Configure with private keys
These scripts accept private keys either through the environment or the command line.  The easiest method is to store them in the script that creates the python virtual environment; if so, **be sure that you are not exposing this information by, for example, storing your virtual envirnoment files in a public code repository.**
* Betterworks API access requires an API key provided by technical support.
* Airtable API keys can be found in your [Airtable Account page](https://airtable.com/account)
* add these lines to ~/.venv_example_path/bin/activate
** ```export BETTERWORKS_API_TOKEN=yourtokenhere```
** ```export AIRTABLE_API_KEY=yourkeyhere```

# Usage
```
usage: extract.py [-h] [--betterworks_api_token BETTERWORKS_API_TOKEN] [--airtable_api_key AIRTABLE_API_KEY] [--debug]
                  [--output_type {text,json,csv,graphviz}]
                  {bw_user,bw_goal,airtable} [identifier]

positional arguments:
  {bw_user,bw_goal,airtable}
                        What type of data should be retrieved?
  identifier            What is the identifier for the type of data? For airtable, use base ID. For bw_goal, provide a BetterWorks Goal ID. For
                        bw_user, provide an email address or BetterWorks User ID.

optional arguments:
  -h, --help            show this help message and exit
  --betterworks_api_token BETTERWORKS_API_TOKEN
                        BetterWorks API Token. Defaults to environment variable.
  --airtable_api_key AIRTABLE_API_KEY
                        Airtable API Key. Defaults to environment variable.
  --debug               Set true to see additional logging. Also dumps a representation of any created tree to debug.txt.
  --output_type {text,json,csv,graphviz}
                        Output format; pipe to file to save. Text is an ascii-art representation of a tree. JSON is a complete data dump in
                        hierarchical JSON, including all node data. csv is a flattened dump of all nodes, i.e., with parent node for each row,
                        but WITHOUT full data per node (for now). graphviz is the dot file format.```
