from argparse import ArgumentParser
from os import _exit, scandir, listdir
from os.path import exists, join
import json
import re
import string
from xml.etree import ElementTree

METADATA = {
    "mvol-0001": {
        "title": "Cap and Gown",
        "description": "The student yearbook of the University of Chicago."
    },
    "mvol-0002": {
        "title": "University of Chicago Magazine",
        "description": "The alumni magazine of the University of Chicago."
    },
    "mvol-0004":  {"title": "Daily Maroon",
                  "description": "A newspaper produced by students of the University of Chicago published 1900-1942 and continued by the Chicago Maroon."
    },
    "mvol-0005": {
        "title": "Quarterly Calendar",
        "description": "Faculty vitae, degree requirements, course descriptions, lists of students, official reports and addresses, abstracts of papers read before student clubs."
    },
    "mvol-0007": {
        "title": "University Record",
        "description": "Official reports, addresses, actions of Ruling Bodies, notices of campus events, and activities of faculty."
    },
    "mvol-0445": {
        "title": "University Record (New Series)",
        "description": "Official reports, addresses, actions of Ruling Bodies, notices of campus events, and activities of faculty."
    },
    "mvol-0446": {
        "title": "University Record",
        "description": "Official reports, addresses, actions of Ruling Bodies, notices of campus events, and activities of faculty"
    }
}
def _find_issues(path):
    for a_thing in scandir(path):
        if a_thing.is_dir():
            matchable = re.compile(r"mvol[/]\d{4}[/]\d{4}[/]\d{4}$").search(a_thing.path)
            if matchable:
                yield a_thing.path
            yield from _find_issues(a_thing.path)
        else:
            pass

def _build_canvas_list(pages, identifier):
    out = []
    for page in pages:
        """
        if '_' in page:
            page = page.split('_')[1]
            page = page.lstrip('0')
        """
        try:
            page = str(page).lstrip('0')
            id_num = str(int(page) - 1)
            zfilled = page.zfill(4)
            a_canvas = {}
            a_canvas["@id"] = "http://iiif-manifest.lib.uchicago.edu/mvol-0001-0021-0000/canvas/c" + id_num
            a_canvas["@type"] = "sc:Canvas"
            a_canvas["height"] = 1000
            a_canvas["width"] = 500
            a_canvas["label"] = "Page " + page
            img = {}
            img["@id"] = "http://iiif-manifest.lib.uchicago.edu/" + identifier + "/annotations/a" + id_num
            img["@type"] = "oa:Annotation"
            img["motivation"] = "sc:painting"
            img["on"] = "http://iif-manifest.lib.uchicago.edu/" + identifier + "/canvas/c" + id_num
            img["resource"] = {"@id": "http://digcollretriever.lib.uchicago.edu/retriever/" + identifier + "_" + zfilled + "/jpg?jpg_height=1000&jpg_width=500",
                               "@type": "dctypes:Image",
                               "format": "image/jpeg",
                               "height": 1000,
                               "width": 500,
                              }
            a_canvas["images"] = [img]
            out.append(a_canvas)
        except ValueError:
            next
    return out

def _main():
    arguments = ArgumentParser()
    arguments.add_argument("path_to_issues", type=str, action='store')
    parsed_args = arguments.parse_args()
    try:
        scanned_files = _find_issues(parsed_args.path_to_issues)
        for n in scanned_files:
            identifier = n.split("mvol")[1]
            identifier = identifier.split("/")
            identifier[0] = "mvol"
            series = identifier[0] + '-' + identifier[1]
            series_info = METADATA[series]
            issue = identifier[-1].lstrip('0')
            volume = identifier[-2].lstrip('0')
            if issue == "":
                issue = "0"
            identifier = "-".join(identifier)
            outp = {}
            outp["@context"] = "http://iiif.io/api/presentation/2/context.json"
            outp["@id"] = "http://iiif-manifest.lib.uchicago.edu/manifest.json"
            outp["@type"] = "sc:Manifest"

            outp["description"] = series_info["description"]
            outp["metadata"] = []
            outp["metadata"].append({"label": "Title", "value": series_info["title"]})
            outp["metadata"].append({"label": "Identifier", "value": identifier})
            if "mvol-0004" in identifier:
                month = issue[0:2]
                date = issue[2:4].zfill(2)
                publication_date = [volume, date, month]
                print(publication_date)
                publication_date = '-'.join(publication_date)
                title = series_info["title"] + ", " + publication_date
                outp["metadata"].append({"label": "Date", "value": publication_date})
                outp["label"] = title
            else:
                dc_file_path = join(n, identifier + ".dc.xml")
                if exists(dc_file_path):
                    root = ElementTree.parse(dc_file_path).getroot()
                    date = root.find("date").text
                    outp["metadata"].append({"label": "Date", "value": date})
                else:
                    outp["metadata"].append({"label": "volume", "value": volume})
                    outp["metadata"].append({"label": "issue", "value": issue})
                outp["label"] = series_info["title"] + " Volume " + volume + ", Issue " + issue
            outp["license"] =  "http://campub.lib.uchicago.edu/rights/"
            seq = {}
            seq["@id"] = "http://iiif-manifest.lib.uchicago.edu/" + identifier + "/sequence/s0",
            seq["@type"] = "sc:Sequence",
            seq["label"]  = ""
            seq["rendering"]  = {
                "@id": "http://digcollretriever.lib.uchicago.edu/retriever/" + identifier + "/pdf",
                "format": "application/pdf",
                "label": "Download as PDF"
            }
            seq["viewingHint"] = "paged"
            seq["canvases"] = []
            try:
                n_path = join(n, "tif")
                pages = listdir(n_path)
            except:
                n_path = join(n, "TIFF")
                pages = listdir(n_path)
            pages = [x.split(".tif")[0] for x in pages]
            np = []
            for p in pages:
                if 'OCRJob' in p or 'Thumbs' in p:
                    p = None
                elif '_' in p:
                    p = int(p.split('_')[1].lstrip('0'))
                else:
                    try:
                        p = int(p.lstrip('0'))
                    except ValueError:
                        print(p)
                if p:
                    np.append(p)
            canvases = _build_canvas_list(sorted(np), identifier)
            seq["canvas"] = canvases
            outp["sequences"] = seq
            json_file_name = identifier + ".json"
            json_file_path = "./manifests/" + json_file_name
            with open(json_file_path, "w", encoding="utf-8") as write_file:
                json.dump(outp, write_file, indent=4)
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(_main())
