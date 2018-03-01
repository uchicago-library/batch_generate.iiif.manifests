
from argparse import ArgumentParser
import json
from os import _exit, scandir, getcwd
from os.path import join
from uuid import uuid4

def find_manifests(path, chicago_number):
    for something in scandir(path):
        if something.is_dir():
            yield from find_manifests(something.path, chicago_number)
        elif something.is_file() and something.path.endswith(".json"):
            data = json.load(open(something.path, "rb"))
            metadata_list = data["metadata"]
            for mdata in metadata_list:
                lbl = mdata["label"]
                val = mdata["value"]
                if lbl == "Chicago Number" and val == chicago_number:
                    yield (something.path, data)



def main():
    arguments = ArgumentParser(description="a tool to build Speculum IIIF itinerary sequences")
    arguments.add_argument("itinerary_data", help="the file containing itinerary text", type=str, action='store')
    arguments.add_argument("path_to_manifests", help="the location of the manifests to parse for linking to in itinerary manifests", type=str, action='store')
    parsed_args = arguments.parse_args()
    try:
        itinerary_info = json.load(open(parsed_args.itinerary_data, "rb"))

        itineraries_collection_id = "itineraries.json"
        itineraries_collection_uri = "https://iiif-collection.lib.uchicago.edu/speculum/" + itineraries_collection_id
        itineraries_collection_filepath = join(getcwd(), "manifests" , "speculum", itineraries_collection_id)
        itineraries_collection = {}
        itineraries_collection["@context"] = "http://iiif.io/api/presentation/2/context.json"
        itineraries_collection["@id"] = itineraries_collection_uri
        itineraries_collection["@type"] = "sc:Collection"
        itineraries_collection["label"] = "Itineraries"
        itineraries_collection["description"] = "Virtual itineraries are mini-exhibitions designed by scholars that allow you to travel through the collection along a particular path based on a theme, location, collection, or artist. These allow for a more specialized, but still lively and accessible, introduction to selected works from the collection, draw attention to particular intellectual questions associated with these prints, and serve as a new mode of scholarly publishing."
        itineraries_collection["viewingHint"] = "individuals"
        itineraries_collection["license"] = ""
        itineraries_collection["attribution"] = "University of Chicago Library"
        itineraries_collection["members"] = []
        count = 1
        for an_itinerary in itinerary_info["itineraries"]:
            manifest_id = uuid4().urn.split(":")[-1]
            outp = {}
            itinerary_id = 'itinerary-' + str(count)
            itinerary_filepath = join(getcwd(), "manifests", "speculum", "itineraries", itinerary_id + ".json")
            itinerary_uri = "https://iiif-collection.lib.uchicago.edu/speculum/itineraries/" + itinerary_id + ".json"
            itinerary_pkg = {}
            itinerary_pkg["@id"] = itinerary_uri
            itinerary_pkg["@type"] = "sc:Collection"
            itinerary_pkg["label"] = an_itinerary["title"]

            itineraries_collection["members"].append(itinerary_pkg)

            outp["@context"] = "http://iiif.io/api/presentation/2/context.json"
            outp["@id"] = itinerary_uri
            outp["@type"] = "sc:Collection"
            outp["label"] = an_itinerary["title"]
            outp["description"] = an_itinerary["description"]
            outp["viewingHint"] = "multi-part"
            outp["metadata"] = []
            for n in an_itinerary["creators"]:
                outp["metadata"].append({"label": "Creator", "value": n["name"] + ", " + n["title"] + ", " + n["institution"]})
            outp["license"] = ""
            outp["attribution"] = "University of Chicago Library"
            outp["members"] = []
            item_counter = 1
            for item in an_itinerary["items"]:
                # need to get info for item collection record and pkg
                item_description = item["description"]
                item_label = item["title"]
                item_id = itinerary_id + "-" + str(item_counter) + ".json"
                item_filepath = join(getcwd(), "manifests", "speculum", "itineraries" , item_id)
                item_uri = "https://iiif-collection.lib.uchicago.edu/speculum/itineraries/" + item_id

                item_pkg = {}
                item_pkg["@id"] = item_uri
                item_pkg["@type"] = "sc:Collection"
                item_pkg["label"] = item_label
                item_pkg["viewingHint"] = "multi-part"
                outp["members"].append(item_pkg)

                item_root = {}
                item_root["@context"] = "http://iiif.io/api/presentation/2/context.json"
                item_root["@id"] = item_uri
                item_root["@type"] = "sc:Collection"
                item_root["label"] = item_label
                item_root["description"] = item_description
                item_root["viewingHint"] = "individuals"
                item_root["license"] = ""
                item_root["attribution"] = "University of Chicago Library"
                item_root["members"] = []

                chicago_numbers = item["id"]
                for number in chicago_numbers:
                    for a_manifest in find_manifests(parsed_args.path_to_manifests, number):
                        test = a_manifest
                        member_uri = a_manifest[1]["@id"]
                        member_label = a_manifest[1]["label"]

                        cho_pkg = {}
                        cho_pkg["@id"] = member_uri
                        cho_pkg["@type"] = "sc:Manifest"
                        cho_pkg["label"] = member_label
                        cho_pkg["viewingHint"] = "individuals"
                        item_root["members"].append(cho_pkg)

                # write item itinerary record
                with open(item_filepath, "w+") as wf:
                    json.dump(item_root, wf, indent=4)
                item_counter += 1
            with open(itinerary_filepath, "w+", encoding="utf-8") as write_file:
                json.dump(outp, write_file, indent=4)
            count += 1
            print(itinerary_filepath)
        with open(itineraries_collection_filepath, "w+") as wf:
            json.dump(itineraries_collection, wf, indent=4)
        return 0
    except  KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(main())
