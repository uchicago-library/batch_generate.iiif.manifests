from argparse import ArgumentParser
import json
from os import listdir, scandir, getcwd
from os.path import join
from uuid import uuid4

"""
{
  "@context": "http://iiif.io/api/presentation/2/context.json",
  "@id": "http://universalviewer.io/manifests.json",
  "@type": "sc:Collection",
  "collections": [
    {
      "@context": "http://iiif.io/api/presentation/2/context.json",
      "@id": "http://universalviewer.io/manifests.json",
      "@type": "sc:Collection",
      "label": "University of Chicago - Quarterly Calendar",
      "manifests": [
        {
          "@id": "https://iiif-manifest.lib.uchicago.edu/mvol/mvol-0005-0004-0001.json",
          "@type": "sc:Manifest",
          "label": "Quarterly Calendar"
        }
      ]
    },
    {
      "@context": "http://iiif.io/api/presentation/2/context.json",
      "@id": "http://universalviewer.io/manifests.json",
      "@type": "sc:Collection",
      "label": "University of Chicago - APF",
      "manifests": [
        {
          "@id": "https://iiif-manifest.lib.uchicago.edu/apf/1/apf1-00001.json",
          "@type": "sc:Manifest",
          "label": "APF"
        }
      ]
    }
  ]
}
"""

def find_all_manifests(path):
    if path.endswith("manifest.json"):
        pass
    else: 
        for something in scandir(path):
            if something.is_dir():
                yield from find_all_manifests(something.path)
            elif something.is_file() and something.path.endswith(".json"):
                yield something.path

def main():
    arguments = ArgumentParser()
    arguments.add_argument("manifest_root", type=str, action='store')
    parsed_args = arguments.parse_args()
    try:
        collections = scandir(parsed_args.manifest_root)
        manifest_id = uuid4().urn.split(":")[-1]
        manifest = {}
        manifest["@context"] = "http://iiif.io/api/presentation/2/context.json"
        manifest["@id"] = "http://" + manifest_id
        manifest["@type"] = "sc:Mcollection"
        manifest["collections"] = []
        for collection in collections:
            if collection.path.endswith("mvol"):
                coll_label = "University Publications"
            elif collection.path.endswith("mepa"):
                coll_label = "Middle East Photograph Archive"
            elif collection.path.endswith("apf"): 
                coll_label = "University Photographic Archive"
            coll_id = uuid4().urn.split(":")[-1]
            a_coll = {}
            a_coll["@context"] = "http://iiif.io/api/presentation/2/context.json"
            a_coll["@id"] = "http://" + coll_id
            a_coll["@type"] = "sc:Collection"
            a_coll["label"] = coll_label
            a_coll["manifests"] = []
            gen = find_all_manifests(collection.path)
            for n_manifest in gen:
                json_data = json.load(open(n_manifest, "r", encoding="utf-8"))
                if json_data.get("label", None):
                    manifest_title = json_data["label"]
                else:
                    manifest_title = "Untitled"
                a_manifest = {}
                a_manifest["@id"] = "https://iiif-manifest.lib.uchicago.edu/" + n_manifest.split(parsed_args.manifest_root + "/")[1]
                a_manifest["@type"] = "sc:Manifest"
                a_manifest["label"] = manifest_title
                a_coll["manifests"].append(a_manifest)
            manifest["collections"].append(a_coll)
        with open(join(getcwd(), "manifest.json"), "w+", encoding="utf-8") as write_file:
            json.dump(manifest, write_file, indent=4)
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    main()

