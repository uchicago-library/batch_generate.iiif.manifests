from argparse import ArgumentParser
import json
from os import listdir, scandir, getcwd, mkdir

from os.path import basename, join, dirname, exists
from pymarc import MARCReader
from uuid import uuid4
import magic
from shutil import copyfile
from urllib.parse import quote

def find_all_manifests(path):
    if path.endswith("manifest.json"):
        pass
    else:
        for something in scandir(path):
            if something.is_dir():
                yield from find_all_manifests(something.path)
            elif something.is_file() and something.path.endswith(".json"):
                yield something.path

def find_matching_files(path, identifier=None):
    for n in scandir(path):
        if n.is_dir():
            yield from find_matching_files(n.path, identifier=identifier)
        elif n.is_file():
            if identifier in n.path:
                yield n.path

def find_all_marc_records(path):
    for n in scandir(path):
        if n.is_dir():
            yield from find_all_marc_records(n.path)
        elif n.is_file() and n.path.endswith("mrc"):
            yield n.path

def find_matching_manifest(path, title=None):
    for n in scandir(path):
        if n.is_dir():
            yield from find_matching_manifest(n.path, title=title)
        elif n.is_file() and n.path.endswith(".json"):
            data = json.load(open(n.path, "r"))
            pot_title = data["label"]
            if pot_title = title:
                print(n.path)


def main():
    arguments = ArgumentParser()
    arguments.add_argument("titles_manifest", type=str, action='store')
    arguments.add_argument("path_to_manifests", type=str, action='store')
    parsed_args = arguments.parse_args()
    try:
        out = []
        data = None
        with open(parsed_args.titles_manifest, "r") as rf:
            data = json.load(rf)
        for n in data["members"]:
            matchable_title = n.get("label")
            relevant_manifests = find_matching_manifest(parsed_args.path_to_manifests,
                                                        title=matchable_title)
            m = [x for x in relevant_manifests]

        for n in data:
            pass
            """
            cho_title = n["cho_title"].split("/")[0] if "/" in n["cho_title"] else n["cho_title"]
            matched_title = n["matched_title"].split("/")[0] if "/" in n["matched_title"] else n["matched_title"]
            if cho_title == matched_title:
                out = {}
                out["@context"] = "https://iiif.io/api/presentation/2/context.json"
                out["@id"] = "https://iiif-manifest.lib.uchicago.edu/maps/social_scientists/" + n["identifier"] + "/" + n["identifier"] + ".json"
                out["@type"] = "sc:Manifest"
                out["logo"] = "https://www.lib.uchicago.edu/static/base/images/color-logo.png"
                out["attribution"] = "University of Chicago Library"
                out["label"] = matched_title
                out["sequences"] = []
                a_seq = {}
                a_seq["@id"] = out["@id"] + '/sequences/0'
                a_seq["@type"] = "sc:Sequence"
                a_seq["canvases"] = []
                files = n["files"]
                files = [x for x in files if not x.endswith(".xml")]
                files =  [x for x in files if not  x.endswith(".mrc")]
                for af in files:
                    a_canvas = {}
                    canvas_id = uuid4().urn.split(":")[-1]
                    a_canvas["@context"] = ""
                    a_canvas["@id"] = "http://" + canvas_id
                    a_canvas["@type"] = "sc:Canvas"
                    a_canvas["label"] = ""
                    the_info = magic.from_file(af)
                    height = [x for x in the_info if "height=" in x]
                    width = [x for x in the_info if "width=" in x]
                    if width and height:
                        height = height[0].split('=')[1]
                        width = width[0].split('=')[1]
                        a_canvas["height"] = height
                        a_canvas["width"] = width
                    an_img = {}
                    basef = basename(af)
                    basef, extension = basef.split(".")
                    extension = extension.lower()
                    dest =  join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/maps/social_scientists", n["identifier"], "tifs", basef + "." + extension)
                    dest_dirs = dirname(dest)
                    src = af
                    new = "/"
                    for new_part in dest_dirs.split("/"):
                        new = join(new, new_part)
                        if not exists(new):
                            mkdir(new)
                    copyfile(src,dest)
                    tif_id = "maps/social_scientists/" + n["identifier"] + "/tifs/" + basef + "." + extension
                    tif_id = quote(tif_id, safe="")
                    an_img = {}
                    an_img["@type"] = "oa:Annotation"
                    an_img["motivation"] = "sc:Painting"
                    an_img["resource"] = {}

                    an_img["resource"]["@id"] = "http://iiif-server.lib.uchicago.edu/" + tif_id +  "/full/full/0/default.jpg"
                    an_img["resource"]["service"] = {}
                    an_img["resource"]["service"]["@context"] = "http://iiif.io/api/image/2/context.json"
                    an_img["resource"]["service"]["@id"] = "https://iiif-server.lib.uchicago.edu/" + tif_id
                    img_profile = {}
                    img_profile["supports"] = ["canonicalLinkHeader", "profileLinkHeader", "mirroring", "rotationArbitrary", "regionSquare", "sizeAboveFull"]
                    img_profile["qualities"] = ["default", "gray", "bitonal"]
                    img_profile["format"] = ["jpg", "png", "gif", "webp"]
                    an_img["resource"]["service"]["profile"] = ["http://iiif.io/api/image/2/level2.json", img_profile]
                    a_canvas["images"] = [an_img]
                    a_seq["canvases"].append(a_canvas)
                out["sequences"].append(a_seq)
                json_filepath = join(getcwd(), "manifests/maps/social_scientists", n["identifier"] + ".json")
                with open(json_filepath, "w+") as wf:
                    json.dump(out, wf, indent=4)
            """
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    main()

