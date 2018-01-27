
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
        count = 1
        for an_itinerary in itinerary_info["itineraries"]:
            manifest_id = uuid4().urn.split(":")[-1]
            outp = {}
            outp["@context"] = "http://iiif.io/api/presentation/2/context.json"
            outp["@id"] = "http://" + manifest_id
            outp["@type"] = "sc:Manifest"
            outp["metadata"] = []
            outp["license"] = ""
            outp["attribution"] = "University of Chicago Library"
            outp["sequences"] = []
            seq_id = uuid4().urn.split(":")[-1]
            a_seq = {}
            a_seq["@id"] = "http://" + seq_id
            a_seq["@type"] = "sc:Sequence"
            a_seq["canvases"] = []

            itinerary_title = an_itinerary["title"]
            itinerary_description = an_itinerary["description"]
            itinerary_creator = an_itinerary["creators"][0]
            itinerary_creator = itinerary_creator["name"] + ", " + itinerary_creator["title"] + ", " + itinerary_creator["institution"]
            outp["label"] = itinerary_title
            outp["description"] = itinerary_description
            outp["metadata"].append({"label": "Creator", "value": itinerary_creator})
            outp["viewingHint"] = "non-paged"
            outp["viewingDirection"] = "left-to-right"
            outp["sequences"] = []
            outp["seeAlso"] = []
            itinerary_items = an_itinerary["items"]
            for item in itinerary_items:
                img_url = None
                title = None
                description = None
                metadata = None
                new_canvas = {}
                chicago_numbers = item["id"]
                if item.get("seeAlso"):
                    see_alsos = item.get("seeAlso")
                else:
                    see_alsos = []
                for an_also in see_alsos:
                    for a_manifest in find_manifests(parsed_args.path_to_manifests, an_also):
                        test = a_manifest
                        path = a_manifest[0]
                        url = path.split(parsed_args.path_to_manifests)[1]
                        url = "https://iiif-manifest.lib.uchicago.edu/speculum" + url
                        url = "https://universalviewer.io/uv.html?manifest=" + url
                        outp["seeAlso"].append(url)
                for number in chicago_numbers:
                    for a_manifest in find_manifests(parsed_args.path_to_manifests, number):
                        test = a_manifest
                        a_manifest = a_manifest[1]
                        for a_canvas in a_manifest["sequences"][0]["canvases"]:
                            new_canvas = a_canvas
                            new_canvas["label"] = item["title"]
                            if item.get("description"):
                                new_metadata = [{"label": "Itinerary Guide Information", "value": item["description"]}]
                                new_metadata += a_manifest["metadata"]
                                new_canvas["metadata"] =  new_metadata
                            else:
                                new_metadata = a_manifest["metadata"]
                                new_canvas["metadata"] = a_manifest["metadata"]
                            a_seq["canvases"].append(new_canvas)
            outp["sequences"].append(a_seq)
            json_filepath = join(getcwd(), "itineraries", "speculum-itinerary-" + str(count) + ".json")
            with open(json_filepath, "w+", encoding="utf-8") as write_file:
                json.dump(outp, write_file, indent=4)
            count += 1
            print(json_filepath)
        return 0
    except  KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(main())
