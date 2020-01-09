import json
import argparse



def up_name():
    """
    convert treelib json output, which looks like this

    {"root":
      {"children": [
        {"Activity: Build/improve models in response to community demand (ongoing every quarter)":
          {"data":
            {"node_type": "Activities"}}},
        {"Priority: Brand Awareness":
          {"children": [
            {"Outcome: B-O2: Clarify and strengthen brand architecture":
              {"children": [
                {"KD: B-O2-D1: Brand",
                {"data":{"node_type": "Projects"}}}
              ]}
            }
          }
        }
      }]
    }


    to explicitly named json that d3 hierarchies use



    {
     "name": "flare",
     "children": [
      {
       "name": "vis",
       "children": [
        {
         "name": "events",
          "children": [
           {"name": "DataEvent", "size": 2200}]
        }]
      }]
    }



"""


def main():
    """
    Convert a treelib json file from extract.py to a d3 hierarchy-style json file.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('input_filename',
                        type=str,
                        help='What is the input filename?')

    parser.add_argument('output_filename',
                        type=str,
                        help='What is the output filename?')

    args = vars(parser.parse_args())

    input_filename = args.get('input_filename')
    output_filename = args.get('output_filename')

    with open(input_filename, 'r') as input_file:
        data = json.load(input_file)

    fixed_data = up_name(data)

    breakpoint()
    


if __name__ == '__main__':

    main()
