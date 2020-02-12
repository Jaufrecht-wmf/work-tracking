import argparse
import logging
import os
import pprint
import requests
import sys
import treelib


class Goal(object):
    """
    This is a partial representation of a BetterWorks Goal.  All items
    in BetterWorks are called goals in the API, regardless of UI
    presentation, so follow that convention here.
    """

    def __init__(self, id, name, parent_id, children, owner, start, end, is_key_result=False):
        self.name = name
        self.id = id
        self.parent_id = parent_id
        self.children = children
        self.owner = owner
        self.start = start
        self.end = end
        if is_key_result:
            self.node_type = 'Key Result'
        else:
            self.node_type = 'Objective'

    def __repr__(self):
        return f'{self.name}'

    def as_dict(self):
        return {'id': self.id,
                'name': self.name,
                'node_type': self.node_type,
                'parent_id': self.parent_id,
                'owner': self.owner,
                'start': self.start,
                'end': self.end}


class RootedTree(treelib.Tree):
    """
    This is the starting point for all tree data representation.
    Use a dummy root node so that, if a child node is added that has a
    parent not in the tree, or no parent, it can still be added without
    breaking the DAGness of the tree.
    """

    ROOT_ID = -1

    def __init__(self):
        super(RootedTree, self).__init__()
        self.create_node('root', identifier=RootedTree.ROOT_ID)


def get_airtable_table(table):
    """
    Returns a list of records from an Airtable table.  Each record
    is a json object.
    """

    url = f'https://api.airtable.com/v0/{base_id}/{table}'
    # Because Airtable truncates any response at 100 items, be
    # ready to handle potential pagination.
    expect_more_results = True
    result_list = []
    params = None
    while expect_more_results:
        logging.debug(f'making request to {url} with airtable_headers\
        {airtable_headers} and params {params}')
        response = requests.get(url, headers=airtable_headers, params=params)
        results = response.json()['records']
        if results:
            result_list.extend(results)
        else:
            e = response.get('reason', 'reason not specified')
            raise Exception(f'Table retrieval search failed for reason {e}')

        offset = response.json().get('offset')
        if offset:
            params = {'offset': offset}
        else:
            expect_more_results = False

    return result_list


def get_airtable_tree(result_tree=RootedTree()):
    """
    Retrieve a work breakdown tree from Airtable.  The specific table
    and relationship structure is hard-coded into this function.  each
    table has a list of children and the matching table has a list of
    parents.  Working from the top down, by adding children, means
    adding placeholder nodes that have to be updated later.  And the
    children field won't be present in the API results (without extra
    hoops) if the child field is hidden in the default view.  Working
    as we go, meaning to add all nodes in one level, and then go to the
    next table/level and add all those nodes, et al, seems simpler and
    for Airtable requires no extra API calls.  So let's do that.
    """

    base_name = base_id
    url = f'https://api.airtable.com/v0/meta/bases'
    logging.debug(f'making request to {url} with airtable_headers {airtable_headers}')
    response = requests.get(url, headers=airtable_headers)
    results = response.json()['bases']
    if results:
        # assume that if anything comes back, it is a valid api response and base_id is unique
        base_dict = [base for base in results if base['id'] in base_id]
        base_name = base_dict[0]['name']
    root_node = result_tree.get_node(RootedTree.ROOT_ID)
    root_node.tag = base_name

    ######################################################################
    # Priorities
    ######################################################################

    priorities = get_airtable_table('Priorities')
    for priority in priorities:
        id = priority['id']
        name = priority['fields']['ID']
        if ADD_NODE_TYPE_IN_NAME:
            name = 'Priority: ' + name
        data = {'node_type': 'MTP Priority'}
        result_tree.create_node(
            name,
            identifier=id,
            parent=RootedTree.ROOT_ID,
            data=data)
        logging.debug(f'Added {priority}, parent is root')

    ######################################################################
    # Outcomes
    ######################################################################

    outcomes = get_airtable_table('Outcomes')
    for outcome in outcomes:
        id = outcome['id']
        name = outcome['fields']['Name']
        code = outcome['fields']['ID']
        if ADD_NODE_TYPE_IN_NAME:
            name = f'Outcome: {code}: {name}'
        department = outcome['fields'].get('Department')
        data = {'department': department, 'code': code, 'node_type': 'MTP Outcome'}
        try:
            parent_id = outcome['fields']['Priority'][0]
        except Exception:
            logging.warning(f'Outcome "{name}" is an orphan')
            parent_id = RootedTree.ROOT_ID
        try:
            result_tree.create_node(
                name,
                identifier=id,
                parent=parent_id,
                data=data)
        except Exception as e:
            logging.warning(f'Failed to add {outcome} because {e}')

    ######################################################################
    # Key Deliverables
    ######################################################################

    deliverables = get_airtable_table('KDs')
    for deliverable in deliverables:
        id = deliverable['id']
        name = deliverable['fields']['KD Budget Name']
        code = deliverable['fields'].get('K-ID', '')
        if ADD_NODE_TYPE_IN_NAME:
            name = f'KD: {code}: {name}'
        description = deliverable['fields'].get('KD Description')
        data = {'description': description,
                'code': code,
                'node_type': 'MTP Key Deliverable'}
        try:
            parent_id = deliverable['fields']['Outcome'][0]
        except Exception:
            logging.warning(f'KD "{name}" is an orphan because Outcome is missing')
            parent_id = RootedTree.ROOT_ID
        try:
            result_tree.create_node(
                name,
                identifier=id,
                parent=parent_id,
                data=data)
        except Exception as e:
            logging.warning(f'Failed to add {deliverable} because {e}')

    ######################################################################
    # Projects
    ######################################################################

    projects = get_airtable_table('Projects')
    for project in projects:
        id = project['id']
        name = project['fields'].get('Project Name', 'no name')
        if ADD_NODE_TYPE_IN_NAME:
            name = f'Project: {name}'
        data = {'node_type': 'Projects'}
        try:
            parent_id = project['fields']['KD'][0]
        except Exception:
            logging.warning(f'Project "{name}" is an orphan because KD is missing')
            parent_id = RootedTree.ROOT_ID

        # maybe move this try/except to a subroutine
        try:
            result_tree.create_node(
                name,
                identifier=id,
                parent=parent_id,
                data=data)
        except treelib.exceptions.NodeIDAbsentError:
            parent_id = RootedTree.ROOT_ID
            result_tree.create_node(
                name,
                identifier=id,
                parent=parent_id,
                data=data)
            logging.warning(f'Adding {project} as an orphan because KD not found')

    ######################################################################
    # Activities
    ######################################################################

    activities = get_airtable_table('Activities')
    for activity in activities:
        id = activity['id']
        name = activity['fields'].get('Activity', 'no name')
        if ADD_NODE_TYPE_IN_NAME:
            name = f'Activity: {name}'
        data = {'node_type': 'Activities'}
        try:
            parent_id = activity['fields']['KeyDeliverable'][0]
            # there may be more than one; for now, just use the first
        except Exception:
            logging.warning(f'Activity "{name}" is an orphan because KD is missing')
            parent_id = RootedTree.ROOT_ID
        try:
            result_tree.create_node(
                name,
                identifier=id,
                parent=parent_id,
                data=data)
        except treelib.exceptions.NodeIDAbsentError:
            parent_id = RootedTree.ROOT_ID
            result_tree.create_node(
                name,
                identifier=id,
                parent=parent_id,
                data=data)
            logging.warning(f'Adding {activity} as an orphan because KD not found')

    return result_tree


def get_goal_as_object(goal_id):
    """
    Retrieve a single BW goal by ID.  Maybe this should be a class method?
    """
    url = f'https://app.betterworks.com/api/v1/goals/{goal_id}/'
    try:
        response = requests.get(url, headers=betterworks_headers)
        results = response.json()
    except Exception as e:
        logging.warning(f'Could not retrieve goal {goal_id}: {e}')
    goal_id = int(results.get('id'))
    goal_name = results.get('name')
    # categories = results.get('categories')
    children = results.get('children')
    is_key_result = results.get('is_key_result')
    parent = results.get('parent')
    try:
        owner = results['owner']['user']['name']
    except KeyError:
        owner = ''
    start = results.get('start')
    end = results.get('end')
    if parent:
        parent_id = parent.get('id')
    else:
        parent_id = RootedTree.ROOT_ID
    goal = Goal(goal_id, goal_name, parent_id, children, owner, start, end, is_key_result)
    return goal


def get_goal_as_tree(goal_id, result_tree=RootedTree()):
    """
    Retrieve a BW goal and all descendents.  Return as a tree, added to an
    existing tree if passed in.
    """
    goal = get_goal_as_object(goal_id)
    if not goal:
        logging.warning(f'Looked for {goal_id} but did not get result')
        return

    try:
        # Add the goal to the tree
        # Data is added as dict because treelib.to_json can't serialize objects
        result_tree.create_node(
            repr(goal),
            identifier=int(goal_id),
            parent=int(goal.parent_id),
            data=goal.as_dict())
        logging.debug(f'Added {repr(goal)}, parent {goal.parent_id}')
    except treelib.exceptions.NodeIDAbsentError as e:
        # Allow special cases where there is no parent or parent is mangled
        # This is a separate branch because we can't know ahead of time if it's needed
        result_tree.create_node(
            goal.name,
            identifier=goal_id,
            parent=RootedTree.ROOT_ID,
            data=goal.as_dict())
        logging.warning(f'Added "{repr(goal)}" as an orphan because {e}')
    except treelib.exceptions.DuplicatedNodeIdError:
        logging.debug(f'Saw {goal_id} again; did not add')
    except Exception as e:
        logging.error(f'failed to add {pprint.pprint(goal)} because {e}')

    for child in goal.children:
        child_goal_id = child['id']
        result_tree = get_goal_as_tree(child_goal_id, result_tree)

    return result_tree


def get_goals_for_user(user_id, result_tree=RootedTree()):
    """
    Return a tree of BW goals that this user_id owns and all their descendents.
    """

    url = f'https://app.betterworks.com/api/v1/goals/filter'
    params = {'owner': user_id}

    # Because BetterWorks truncates any response at 30 items, be
    # ready to handle potential pagination.
    expect_more_results = True
    while expect_more_results:
        try:
            logging.debug(f'making request to {url} with betterworks_headers\
            {betterworks_headers} and params {params}')
            response = requests.get(url, headers=betterworks_headers, params=params)
            results = response.json().get('results')
            if not results:
                e = response.get('reason', 'reason not specified')
                raise Exception(f'Goals search failed for reason {e}')
            for item in results:
                goal_id = int(item['id'])
                result_tree = get_goal_as_tree(goal_id, result_tree)
        except Exception as e:
            raise Exception(f'Goals search failed for reason {e}')

        more = response.json().get('more')
        url = response.json().get('nextURL')
        if not (more and url):
            expect_more_results = False

    return result_tree


def get_bw_user(userstring):
    """
    Search for user by email or user id, and return tuple of userid and name
    """
    url = f'https://app.betterworks.com/api/v1/users/{userstring}'
    try:
        response = requests.get(url, headers=betterworks_headers)
        results = response.json()
        name = results.get('name')
        id = results.get('id')
    except Exception as e:
        raise Exception(f'User Search query failed with {e}')
    return id, name


def main():
    """
    Retrieve some hierarchical data from WMF's work tracking systems.  Save it
    in a pickled Treelib file.
    """
    ######################################################################
    # Initialize
    ######################################################################

    parser = argparse.ArgumentParser()
    parser.add_argument('type',
                        choices=['bw_user', 'bw_goal', 'airtable'],
                        help='What type of data should be retrieved?')

    parser.add_argument('identifier',
                        type=str,
                        nargs='+',  # required; multiple accepted; list returned.
                        help="""What is the identifier for the type of data?  For airtable,
                        use base ID.  For bw_goal, provide a BetterWorks Goal ID.
                        For bw_user, provide an email address, BetterWorks User ID,
                        or space-delimited list of one or both types.""")

    parser.add_argument('--betterworks_api_token',
                        metavar='BETTERWORKS_API_TOKEN',
                        type=str,
                        help='BetterWorks API Token.  Defaults to environment variable.',
                        default=os.getenv('BETTERWORKS_API_TOKEN'))

    parser.add_argument('--airtable_api_key',
                        metavar='AIRTABLE_API_KEY',
                        type=str,
                        help='Airtable API Key.  Defaults to environment variable.',
                        default=os.getenv('AIRTABLE_API_KEY'))

    parser.add_argument('--output_file',
                        type=str,
                        help='File name for output',
                        default='pickle.json')

    parser.add_argument('--debug',
                        action='store_true',
                        help="""Set true to see additional logging.""")

    args = vars(parser.parse_args())

    airtable_api_key = args.get('airtable_api_key')
    global airtable_headers
    airtable_headers = {'Authorization': f'Bearer {airtable_api_key}'}

    betterworks_api_token = args.get('betterworks_api_token')
    global betterworks_headers
    betterworks_headers = {'Authorization': f'APIToken {betterworks_api_token}'}

    output_file = args.get('output_file')
    global DEBUG
    DEBUG = args.get('debug')
    if DEBUG:
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S %z',
            level=logging.DEBUG,
            stream=sys.stdout)

    ######################################################################
    # Fetch the data
    ######################################################################

    fetch_type = args.get('type')
    identifier = args.get('identifier')
    if not identifier:
        raise Exception(
            'An identifier must be specified in the command line.'  # NOQA
        )

    if fetch_type == 'airtable':
        if not airtable_api_key:
            raise Exception(
                'AIRTABLE_API_KEY must be in the environment, or specified in the command line.'  # NOQA
            )
        global base_id  # avoid a bunch of passing around base_id
        base_id = identifier[0]
        result_tree = get_airtable_tree()
    else:
        if not betterworks_api_token:
            raise Exception(
                'BETTERWORKS_API_TOKEN must be in the environment, or specified in the command line.'  # NOQA
            )
        result_tree = RootedTree()
        root_node = result_tree.get_node(RootedTree.ROOT_ID)
        root_node.tag = 'root'
        if fetch_type == 'bw_user':
            for user_identifier in identifier:
                user_id, user_name = get_bw_user(user_identifier)
                result_tree = get_goals_for_user(user_id, result_tree)
                if len(identifier) == 1:
                    root_node = result_tree.get_node(RootedTree.ROOT_ID)
                    root_node.tag = user_name
        else:  # assume retrieval by goal ID
            for goal_id in identifier:
                result_tree = get_goal_as_tree(goal_id, result_tree)
                if len(identifier) == 1:
                    root_node = result_tree.get_node(RootedTree.ROOT_ID)
                    root_node.tag = identifier

    ######################################################################
    # Output the data
    ######################################################################

    breakpoint()
    import pickle
    logging.debug(f'dumping serialized json')
    pickle.dump(result_tree, open(output_file, 'wb'))


if __name__ == '__main__':

    # temporary variable to stick node type into the name as a quick
    # hack to make it visible in reports; permanent solution is to
    # have reports get it from node_type

    global ADD_NODE_TYPE_IN_NAME
    ADD_NODE_TYPE_IN_NAME = True
    main()
