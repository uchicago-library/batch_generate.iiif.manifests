
from argparse import ArgumentParser
import json
from os import _exit, scandir

def find_relevant_manifest(path, chicago_number):
    for something in scandir(path):
        if something.is_dir():
            yield from find_relevant_manifest(path, chicago_number)
        elif something.is_file() and something.path.endswith(".json"):
            yield something.path



def main():
    arguments = ArgumentParser(description="a tool to build Speculum IIIF itinerary sequences")
    arguments.add_argument("itinerary_data", help="the file containing itinerary text", type=str, action='store')
    arguments.add_argument("path_to_manifests", help="the location of the manifests to parse for linking to in itinerary manifests", type=str, action='store')
    parsed_args = arguments.parse_args()
    try:
        itinerary_info = json.load(open(parsed_args.itinerary_data, "rb"))
        for an_itinerary in itinerary_info["itineraries"]:
            itinerary_title = an_itinerary["title"]
            itinerary_description = an_itinerary["description"]
            itinerary_creator = an_itinerary["creators"][0]
            itinerary_creator = itinerary_creator["name"] + ", " + itinerary_creator["title"] + ", " + itinerary_creator["institution"]
            itinerary_items = an_itinerary["items"]
            for item in itinerary_items:
                chicago_numbers = item["id"]
                for number in chicago_numbers:
                    d = find_relevant_manifest(parsed_args.path_to_manifests, number)
                    for n in d:
                        print(n)
                    print(number)
        return 0
    except  KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(main())
