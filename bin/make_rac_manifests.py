from argparse import ArgumentParser
import csv
from os import _exit, listdir, scandir, getcwd, mkdir
from os.path import join, basename, exists, dirname
from shutil import copyfile
import re
from sys import stdout
import json
from xml.etree import ElementTree
from pymarc import MARCReader
from pymarc.exceptions import RecordLengthInvalid
from PIL import Image
from uuid import uuid4

def main():
    arguments = ArgumentParser()
    arguments.add_argument("group_file", action='store', type=str)
    parsed_args = arguments.parse_args()
    try:
        data = json.load(open(parsed_args.group_file, "rb"))
        print(str(data).encode("utf-8"))
        for n in data:
            manifest_id = uuid4().urn.split(":")[-1]
            outp = {}
            outp["@context"] = "http://iiif.io/api/presentation/2/context.json"
            outp["@id"] = "http://" + manifest_id
            outp["@type"] = "sc:Manifest"
            outp["metadata"] = []
            identifier = n["identifier"]
            print(identifier)
            outp["description"] = n["description"]
            outp["label"] = n["title"]
            outp["metadata"].append({"label": "Alternate Title", "value": n["alt_title"]})
            outp["metadata"].append({"label": "Identifier", "value": n["identifier"]})
            outp["license"] = ""
            outp["attribution"] = "University of Chicago Library"
            outp["viewingDirection"] = "left-to-right"
            outp["viewingHint"] = "paged"
            outp["sequences"] = []
            seq_id = uuid4().urn.split(":")[-1]
            a_seq = {}
            a_seq["@id"] = "http://" + seq_id
            a_seq["@type"] = "sc:Sequence"
            a_seq["canvases"] = []
            tif_directory = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files", "rac", str(identifier).zfill(4), "tifs")
            tifs = scandir(tif_directory)
            tifs = sorted([x.path for x in tifs])
            for tif in tifs:
                tif_path = tif.split("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/")[1]
                a_canvas = {}
                label_string = tif_path.split(".tif")[0].split("-")[-1].lstrip('0')
                canvas_id = uuid4().urn.split(":")[-1]
                a_canvas["@id"] = "http://" + canvas_id
                a_canvas["@type"] = "sc:Canvas"
                a_canvas["label"] = "Page " + label_string
                a_canvas["images"] = []
                if not tif_path.endswith("bz2"):
                    a_canvas = {}
                    label_string = tif_path.split(".tif")[0].split("-")[-1].lstrip('0')
                    canvas_id = uuid4().urn.split(":")[-1]
                    a_canvas["@id"] = "http://" + canvas_id
                    a_canvas["@type"] = "sc:Canvas"
                    a_canvas["label"] = "Page " + label_string
                    a_canvas["images"] = []
                    the_img = tif
                    try:
                        f = open(the_img, "rb")
                        img = Image.open(f)
                        width, height = img.size
                        a_canvas["height"] = height
                        a_canvas["width"] = width
                    except OSError:
                        pass
                    an_img = {}
                    an_img["@context"] = "http://iiif.io/api/presentation/2/context.json"
                    img_id = uuid4().urn.split(":")[-1]
                    an_img["@id"] = "http://" + img_id
                    an_img["@type"] = "oa:Annotation"
                    an_img["motivation"] = "sc:Painting"
                    an_img["resource"] = {}
                    tif_id = tif_path
                    print(tif_id)
                    an_img["resource"]["@id"] = "http://iiif-server.lib.uchicago.edu/" + tif_id +  "/full/full/0/default.jpg"
                    an_img["resource"]["service"] = {}
                    an_img["resource"]["service"]["@context"] = "http://iiif.io/api/image/2/context.json"
                    an_img["resource"]["service"]["@id"] = "https://iiif-server.lib.uchicago.edu/" + tif_id
                    img_profile = {}
                    img_profile["supports"] = ["canonicalLinkHeader", "profileLinkHeader", "mirroring", "rotationArbitrary", "regionSquare", "sizeAboveFull"]
                    img_profile["qualities"] = ["default", "gray", "bitonal"]
                    img_profile["format"] = ["jpg", "png", "gif", "webp"]
                    an_img["resource"]["service"]["profile"] = ["http://iiif.io/api/image/2/level2.json", img_profile]
                    a_canvas["images"].append(an_img)
                    a_seq["canvases"].append(a_canvas)
            outp["sequences"].append(a_seq)
            identifier_parts = identifier.split('-')
            identifier_parts = '/'.join(identifier_parts)
            json_filepath = join(getcwd(), "manifests", identifier_parts, identifier + ".json")
            json_dirs = dirname(json_filepath)
            new = "/"
            for a_dir in json_dirs.split('/'):
                new =  join(new, a_dir)
                if exists(new):
                    pass
                else:
                    mkdir(new)
            with open(json_filepath, "w+", encoding="utf-8") as wf:
                json.dump(outp, wf, indent=4)
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(main())
