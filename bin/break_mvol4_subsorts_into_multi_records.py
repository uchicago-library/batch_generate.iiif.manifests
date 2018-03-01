from argparse import ArgumentParser
from os import _exit, scandir, getcwd
from os.path import basename, join
import json
from pymarc import MARCReader
from sys import stderr, stdout

def _main():
    arguments = ArgumentParser()
    arguments.add_argument("path_to_chos", type=str, action='store')
    parsed_args = arguments.parse_args()
    try:
        base_filepath = join(getcwd(), "mvol_0004_manifests")
        data = None
        with open(parsed_args.path_to_chos, "r") as rf:
            data = json.load(rf)
        # start with top collection record for mvol-0004; this is the root dict
        root_filepath = join(base_filepath, "mvol-0004-browse-by-year.json")
        root = {}
        root["label"] = data["label"] + ", Browse By Year"
        root["@id"] = data["@id"]
        root["@context"] = data["@context"]
        root["@type"] = data["@type"]
        root["description"] = data["description"]
        root["attribution"] = data["attribution"]
        root["viewingHint"] = data["viewingHint"]
        root["members"] = []

        big_root_filepath = join(base_filepath, "mvol-0004.json")
        big_root = {}
        big_root["label"] = data["label"]
        big_root["@id"] = data["@id"]
        big_root["@context"] = data["@context"]
        big_root["@type"] = data["@type"]
        big_root["description"] = data["description"]
        big_root["attribution"] = data["attribution"]
        big_root["viewingHint"] = data["viewingHint"]
        big_root["members"] = []

        # now have to iterate through the year members of the top collection
        for year in data["members"]:
            # have to create a dict for year member in root collection record
            year_id = "mvol-0004-" + year["label"].split(", ")[-1]
            year_pkg = {}
            year_pkg["label"] =  year["label"]
            year_pkg["@id"] = "http://iiif-collection.lib.uchicago.edu/mvol/0004/" + year_id + ".json"
            year_pkg["@type"] = "sc:Collection"
            year_pkg["viewingHint"] = "multi-part"

            root["members"].append(year_pkg)

            # now need to create a year collection record
            year_filepath = join(base_filepath, year_id + ".json")
            year_record = {}
            year_record["label"] = year["label"]
            year_record["@id"] = year_pkg["@id"]
            year_record["@context"] = data["@context"]
            year_record["@type"] = data["@type"]
            year_record["description"] = data["description"]
            year_record["attribution"] = data["attribution"]
            year_record["viewingHint"] = "multi-part" 
            year_record["members"] = []

            # from a given year now have to get the month members of that year collection
            for month in year["members"]:
                # have to create a dict for month member in the particular year collection record
                month_id = "mvol-0004-" + month["label"].split(", ")[-1]
                month_pkg = {}
                month_pkg["label"] =  month["label"]
                month_pkg["@id"] = "http://iiif-collection.lib.uchicago.edu/mvol/0004/" + month_id + ".json"
                month_pkg["@type"] = "sc:Collection"
                month_pkg["viewingHint"] = "multi-part"

                # now add month pkg to year record
                year_record["members"].append(month_pkg)

                # now need to create a month collection record
                month_filepath = join(base_filepath, month_id + ".json")
                month_record = {}

                month_record["label"] = month_pkg["label"]
                month_record["@id"] = month_pkg["@id"]
                month_record["@context"] = data["@context"]
                month_record["@type"] = data["@type"]
                month_record["description"] = data["description"]
                month_record["attribution"] = data["attribution"]
                month_record["viewingHint"] = "individuals"
                month_record["members"] = []

                # from a given month now have to get the daily members of that month collection
                for day in month["members"]:
                    # have to crete a dict for day member of the particular month record
                    day_pkg = {}
                    day_id = day["label"].split(", ")[-1].split("-")
                    day_id = 'mvol-0004-' + day_id[0] + '-' + day_id[-2] + day_id[-1]
                    day_id_as_dirs = day_id.split('-')
                    day_id_as_dirs = '/'.join(day_id_as_dirs)
                    day_pkg["label"] =  day["label"]
                    day_pkg["@id"] = "http://iiif-manifest.lib.uchicago.edu/" + day_id_as_dirs + "/" + day_id + ".json"
                    day_pkg["@type"] = "sc:Manifest"
                    day_pkg["viewingHint"] = "individuals"

                    # now need to add day_pkg to month_record
                    month_record["members"].append(day_pkg)

                    # now add the day_pkg to big_root members
                    big_root["members"].append(day_pkg)

                # now need to write the month record to a file
                print(month_filepath)
                with open(month_filepath, "w+") as wf:
                    json.dump(month_record, wf, indent=4)

            # now need to write the year_record to a file
            print(year_filepath)
            with open(year_filepath, "w+") as wf:
                json.dump(year_record, wf, indent=4)

        print(root_filepath)
        with open(root_filepath, "w+") as wf:
            json.dump(root, wf, indent=4)

        print(big_root_filepath)
        with open(big_root_filepath, "w+") as wf:
            json.dump(big_root, wf, indent=4)

        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(_main())

