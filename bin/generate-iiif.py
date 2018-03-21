from argparse import ArgumentParser
from os import _exit, scandir, listdir, getcwd, mkdir
from os.path import exists, join, dirname
import json
from PIL import Image
import re
import string
from uuid import uuid4
from urllib.parse import quote
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
    },
    "mvol-0500": {
        "title": "Automatic Age",
        "description": "Journal devoted to the Interests and Promotion of Vending Machines, Self-Service Appliances, and Devices and Automatic Merchandising."
    },

    "mvol-0501": {
        "title": "Amerikán. Prostonárodní kalendář na obyčejný rok",
        "description": "An annual calendar for Czech-Americans issued by the Chicago based Czech newspaper."
    },
    "mvol-0502": {
        "title":  "Annual report of cancer research",
        "description": "Annual report of cancer research."
    },
    "mvol-0503": {
        "title": "Medicine on the Midway",
        "description": "Bulletin of the University of Chicago Medical Alumni Association."
    },
    "mvol-0504": {
        "title": "Research in Progress",
        "description": "Research in Progress. University of Chicago. Division of the Biological Sciences and the Pritzker School of Medicine"

    },
    "mvol-0506": {
        "title": "Reports. University of Chicago. Division of the Biological Sciences",
        "description": "Research reports from the University of Chicago Division of the Biological Sciences and the Pritzker School of Medicine."
    },
    "mvol-0510": {
        "title": "Law School Record",
        "description": "A publication for the alumni of the University of Chicago Law School."
    },
    "mvol-0075": {
        "title": "Announcements. University of Chicago. Law School",
        "description": "Information on admissions, regulations, course offerings."
    },
    "mvol-0006": {
        "title": "Annual register",
        "description": "Faculty vitae, course descriptions, lists of students, registration statistics."
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
            https://iiif-server.lib.uchicago.edu/loris/mvol/0004/1918/0406/TIFF/mvol-0004-1918-0406_0002.tif/full/full/0/default.jpg
        """
        try:
            original_page = page
            id_num = str(page["number"] - 1)
            loc = page["loc"]
            page = page["number"]
            a_canvas = {}
            a_canvas["@id"] = "http://iiif-manifest.lib.uchicago.edu/" + identifier + "/canvas/c" + id_num
            a_canvas["@type"] = "sc:Canvas"
            a_canvas["height"] = 1000
            a_canvas["width"] = 500
            a_canvas["label"] = "Page " + str(page)
            img = {}
            img["@id"] = "http://iiif-manifest.lib.uchicago.edu/" + identifier + "/annotations/a" + id_num
            img["@type"] = "oa:Annotation"
            img["motivation"] = "sc:painting"
            img["on"] = "http://iif-manifest.lib.uchicago.edu/" + identifier + "/canvas/c" + id_num

            img["resource"] = {"@id": "https://iiif-server.lib.uchicago.edu/" + loc + "/full/full/0/default.jpg",
                               "@type": "dctypes:Image",
                               "format": "image/jpeg",
                               "height": 1000,
                               "width": 500,
                              }
            img["resource"]["profile"] = {"@context": "http://iiif.io/api/image/2/context.json", 
                                          "@id": img["resource"]["@id"], 
                                          "profile": [
                                            "http://iiif.io/api/image/2/level2.json",
                                            {"supports": [
                                                "canonicalLinkHeader",
                                                "profileLinkHeader",
                                                "mirroring",
                                                "rotationArbitrary",
                                                "regionSquare",
                                                "sizeAboveFull",
                                             ],
                                             "qualities": [
                                                "default",
                                                "gray",
                                                "bitonal",
                                             ],
                                             "formats": [
                                                "jpg",
                                                "png",
                                                "gif",
                                                "webp",
                                             ]
                                            }
                                          ]
                                         }
            print(img["resource"]["@id"])
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
            identifier_dir = '/'.join(identifier)
            real_id = '-'.join(identifier)
            print(real_id)
            manifest_id = "https://iiif-manifest.lib.uchicago.edu/" + join(identifier_dir, real_id + ".json")
            series = identifier[0] + '-' + identifier[1]
            series_info = METADATA[series]
            title = series_info["title"]
            description = series_info["description"]
            issue = identifier[-1].lstrip('0')
            volume = identifier[-2].lstrip('0')
            if issue == "":
                issue = "0"
            identifier = "-".join(identifier)
            outp = {}
            outp["@context"] = "http://iiif.io/api/presentation/2/context.json"
            outp["@id"] = manifest_id
            outp["@type"] = "sc:Manifest"
            outp["metadata"] = []
            outp["metadata"].append({"label": "Title", "value": series_info["title"]})
            outp["metadata"].append({"label": "Identifier", "value": identifier})
            outp["description"] = series_info["description"]
            outp["logo"] = "https://www.lib.uchicago.edu/static/base/images/color-logo.png"
            outp["license"] = "http://campub.lib.uchicago.edu/rights/"
            outp["attribution"] = "University of Chicago Library"
            if "mvol-0004" in identifier:
                spcl_issue = identifier.split('-')[-1]
                month = spcl_issue[0:2]
                date = spcl_issue[2:4].zfill(2)
                publication_date = [volume, month, date]
                publication_date = '-'.join(publication_date)
                outp["metadata"].append({"label": "Date", "value": publication_date})
                title = series_info["title"] + ", " + publication_date
                outp["label"] = title
            else:
                dc_file_path = join(n, identifier + ".dc.xml")
                if exists(dc_file_path):
                    root = ElementTree.parse(dc_file_path).getroot()
                    date = root.find("date").text
                    outp["metadata"].append({"label": "Date", "value": date})
                else:
                    outp["metadata"].append({"label": "volume", "value": volume})
                    outp["label"] = title + ", volume " + volume + ", issue " + issue
                title = series_info["title"] + " volume " + volume + ", issue " + issue
                outp["label"] = title

            outp["sequences"] = []
            outp["structures"] = []
            outp["viewingDirection"] = "left-to-right"

            sequence = {}
            sequence_id = uuid4().urn.split(":")[-1]
            sequence_id = manifest_id + "/sequences/" + sequence_id
            sequence["@id"] =  sequence_id
            sequence["@type"] = "sc:Sequence"
            sequence["canvases"] = []
            try:
                n_path = join(n, "tif")
                tif_dirname = "tif"
                pages = listdir(n_path)
            except:
                n_path = join(n, "TIFF")
                tif_dirname = "TIFF"
                pages = listdir(n_path)

            pages = [x.split(".tif")[0] for x in pages]
            pages_data = []
            for x in pages:
                if 'OCRJob' in x or 'Thumbs' in x:
                    pass
                else:
                    num = x.split(".tif")[0]
                    if tif_dirname == "TIFF":
                        try:
                            num = num.split('_')[-1]
                            num = num.lstrip('0')
                            pages_data.append({"number": int(num), "loc":identifier.replace('-','/') + '/' + tif_dirname + '/' + x})
                        except IndexError:
                            print("{} couldn't be split".format(num))
                    elif tif_dirname == "tif":
                        num = num.lstrip('0')
                        pages_data.append({"number": int(num), "loc": identifier.replace('-','/') + '/' + tif_dirname + '/' + x})

            pages_data = sorted(pages_data, key=lambda x: x["number"])
            count = 1
            copy = pages_data
            for p in pages_data:
                copy[copy.index(p)]["label"] = "Page " + str(count)
                count += 1

            for page in copy:
                the_img = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files", page["loc"] + ".tif")
                try:
                    img = Image.open(the_img)
                    width, height = img.size
                except OSError:
                    print("{} could not be opened to get size info".format(the_img))
                a_canvas = {}
                canvas_id = uuid4().urn.split(":")[-1]
                canvas_id = sequence_id + "/canvases/" + canvas_id
                a_canvas["@id"] = canvas_id
                a_canvas["@type"] = "sc:Canvas"
                a_canvas["label" ] = page["label"]
                a_canvas["height"] = height
                a_canvas["width"] =  width
                a_canvas["images"] = []
                an_img = {}
                an_img["@context"] = "http://iiif.io/api/presentation/2/context.json"
                img_id = uuid4().urn.split(":")[-1]
                an_img["@id"] = "http://" + img_id
                an_img["@type"] = "oa:Annotation"
                an_img["motivation"] = "sc:Painting"
                an_img["resource"] = {}
                an_img["resource"]["@id"] = "http://iiif-server.lib.uchicago.edu/" + quote(page["loc"], safe="") +  ".tif/full/full/0/default.jpg"
                an_img["resource"]["@type"] = "dctypes:Image"
                an_img["resource"]["format"] = "image/jpeg"
                an_img["resource"]["height"] = height
                an_img["resource"]["width"] = width
                an_img["on"] = canvas_id
                an_img["resource"]["service"] = {}
                an_img["resource"]["service"]["@context"] = "http://iiif.io/api/image/2/context.json"
                an_img["resource"]["service"]["@id"] = "https://iiif-server.lib.uchicago.edu/" + quote(page["loc"], safe="") +  ".tif"
                img_profile = {}
                img_profile["supports"] = ["canonicalLinkHeader", "profileLinkHeader", "mirroring", "rotationArbitrary", "regionSquare", "sizeAboveFull"]
                img_profile["qualities"] = ["default", "gray", "bitonal"]
                img_profile["format"] = ["jpg", "png", "gif", "webp"]
                an_img["resource"]["service"]["profile"] = ["http://iiif.io/api/image/2/level2.json", img_profile]
                a_canvas["images"].append(an_img)
                sequence["canvases"].append(a_canvas)
            outp["sequences"].append(sequence)
            identifier_directory = identifier.split('-')
            identifier_directory = '/'.join(identifier_directory)
            json_file_name = join(identifier_directory, identifier + ".json")
            json_file_path = join(getcwd(), "manifests", json_file_name)
            new_json_dirs = dirname(json_file_path).split('/')
            new = "/"
            for n in dirname(json_file_path).split("/"):
                new = join(new, n)
                if not exists(new):
                    mkdir(new)
            with open(json_file_path, "w+") as write_file:
                json.dump(outp, write_file, indent=4)
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(_main())
