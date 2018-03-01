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
        out = {}
        data = None
        master_list = []
        with open(parsed_args.path_to_chos, "r") as rf:
            data = json.load(rf)
        label = data["label"]
        members = data["members"]
        members = sorted(members, key=lambda x: x["label"])
        out["label"] = label
        out["@id"] = data["@id"]
        out["@context"] = data["@context"]
        out["@type"] = data["@type"]
        out["description"] = data["description"]
        out["attribution"] = data["attribution"]
        out["viewingHint"] = data["viewingHint"]
        out["members"] = []

        for n in members:
            label = n["label"]
            title, date = label.split(", ")
            year, month, date = date.split('-')

            year_check = [x for x in out["members"]]
            year_check = [x for x in year_check if year in x["label"]]
            if len(year_check) > 0:
                new_month_dict = {}
                month_check = [x for x in year_check[0]["members"] if year + "-" + month in x["label"]]

                if month_check:
                    month_check[0]["members"].append(n)
                else:
                    new_month_id = data["@id"].split('.json')[0] + '-' + year + '-' + month + '.json'
                    new_month_dict["@id"] = new_year_id
                    new_month_dict["@type"] = "sc:Collection"
                    new_month_dict["label"] = data["label"] + ", " + year + "-" + month
                    new_month_dict["members"] = [n]
                    year_check[0]["members"].append(new_month_dict)
            else:
                new_year_dict = {}
                new_year_id = data["@id"].split('.json')[0] + '-' + year + '.json'
                new_year_dict["@id"] = new_year_id
                new_year_dict["@type"] = "sc:Collection"
                new_year_dict["label"] = data["label"] + ", " + year
                new_year_dict["members"] = []
                new_month_dict = {}
                new_month_id = data["@id"].split('.json')[0] + '-' + year + '-' + month + '.json'
                new_month_dict["@id"] = new_year_id
                new_month_dict["@type"] = "sc:Collection"
                new_month_dict["label"] = data["label"] + ", " + year + "-" + month
                new_month_dict["members"] = [n]
                new_year_dict["members"].append(new_month_dict)
                out["members"].append(new_year_dict)


            """
            year_label = data["label"] + ", " + year
            year_top_level_check = [x for x in out["members"] if x["label"] == year_label]
            if len(year_top_level_check) == 1:
                print("hi")
            else:
                new_year_dict = {}
                new_year_id = data["@id"].split('.json')[0] + year + '.json'
                new_year_dict["@id"] = new_year_id
                new_year_dict["@type"] = "sc:Collection"
                new_year_dict["label"] = data["label"] + ", " + year

                new_month_dict = {}
                new_month_id = data["@id"].split(".json")[0] + year + "-" + month + ".json"
                new_month_dict["@id"] = new_month_id
                new_month_dict["@type"] = "sc:Collection"
                new_month_dict["label"] = data["label"] + ", " + year + "-" + month

                new_month_dict["members"] = [n]
                new_year_dict["members"] = [new_month_dict]
                out["members"] = [new_year_dict]
            """
        with open("mvol4_sorted_by_year.json", "w+") as wf:
            json.dump(out, wf, indent=4)
        return 0
        """
        outp = {}
        outp["label"] = "Daily Maroon"
        outp["@context"] = "https://iiif.io/api/presentation/2/context.json"
        outp["@type"] = "sc:Collection"
        outp["description"] = "A newspaper produced by students of the University of Chicago. Published 1900-1942 and continued by the Chicago Maroon."
        outp["@id"] = "https://iiif-collection.lib.uchicago.edu/mvol-0004.json"
        outp["attribution"] = "University of Chicago"
        outp["viewingHint"] = "multi-part"
        outp["members"] = []
        for n in data:
            n_id = n.split("IIIF_Manifests/")[1]
            n_url = "https://iiif-manifest.lib.uchicago.edu/" + n_id
            n_dict = {}
            n_dict["viewingHint"] = "multi-part"
            n_dict["@id"] = n_url
            n_dict["@type"] = "sc:Collection"
            n_dict["label"] = json.load(open(n, "r"))["label"]
            print(n_dict["label"])
            outp["members"].append(n_dict)
        with open(join(getcwd(), "mvol-0004.json"), "w+") as wf:
            json.dump(outp, wf, indent=4)
        """
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(_main())

