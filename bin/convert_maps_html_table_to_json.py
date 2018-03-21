
from argparse import ArgumentParser
from os import _exit, getcwd
from os.path import join, basename
import json
from xml.etree import ElementTree
"""
    {
        "@context": "http://iiif.io/api/presentation/context.json",
        "@id": "http://iiif-collection.lib.uchicago.edu/maps/maps-collections",
        "@type": "sc:Collection",
        "label": "Maps Digital Collections",
        "description": "The list of Maps collections from the University  of Chicago Library",
        "viewingHint": "multi-part",
        "members": [
            {
                "@type": "sc:Collection",
                "@id": "http://iiif-collection.lib.uchicago.edu/maps/chi-1890s.json",
                "viewingHint": "multi-part",
                "label": "Chicago in the 1890s"
            },
            {
                "@type": "sc:Collection",
                "@id": "http://iiif-collection.lib.uchicago.edu/maps/soc-maps-chi.json",
                "viewingHint": "multi-part",
                "label": "Social Scientists Maps Chicago"
            }
        ]
}
"""

def main():
    arguments = ArgumentParser(description="convert maps html table into json file")
    arguments.add_argument("table_data_file")
    arguments.add_argument("name")
    parsed = arguments.parse_args()
    try:
        data = ElementTree.parse(parsed.table_data_file)
        root = data.getroot()
        table_rows = root.findall("tbody/tr")
        out = {}
        out["@context"] = "http://iiif.io/api/presentation/context.json"
        out["@id"] = "http://iiif-collection.lib.uchicago.edu/maps/social-scientists-maps-collections.json"
        out["@type"] = "sc:Collection"
        out["label"] = "Maps Digital Collections"
        out["description"] = "The list of Maps collections from the University  of Chicago Library"
        out["viewingHint"] = "multi-part"
        out["members"] = []
        for row in table_rows:
            tds = row.findall("td")
            td_a = [x.find("a") for x in tds]
            a_member = {}
            a_member["@type"] = "sc:Manifest"
            a_member["@id"] = "https://iiif-manifest.lib.uchicago.edu/"
            a_member["viewingHint"] = "multi-part"
            if td_a:
                identifier = basename(td_a[0].find("img").attrib["src"]).split('-thumb')[0]
                a_member["identifier"] = identifier
            if tds:
                a_member["label"] = tds[1].text
            out["members"].append(a_member)
        with open(join(getcwd(), parsed.name + "-collection.json"), "w+", encoding="utf-8") as wf:
            json.dump(out, wf, indent=4)
        return 0
    except KeyboardInterrupt:
            return 131

if __name__ == "__main__":
    _exit(main())
