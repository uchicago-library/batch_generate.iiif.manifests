from argparse import ArgumentParser
from os import _exit, scandir, listdir, getcwd, makedirs, mkdir
from urllib.parse import quote
from os.path import exists, join, basename, dirname
import json
import magic
from PIL import Image
from pymarc import MARCReader
import re
from shutil import copyfile
import string
from uuid import uuid4
from xml.etree import ElementTree

def _find_all_mepa_chos(path):
    for a_thing in scandir(path):
        if a_thing.is_dir():
            matchable = re.compile(r"\d{3}$").search(a_thing.path)
            if matchable:
                yield a_thing.path

            yield from _find_all_mepa_chos(a_thing.path)
        else:
            pass


def find_all_photo_chos(path):
    for p in scandir(path):
        if p.is_dir():
            yield from find_all_ph

def _main():
    arguments = ArgumentParser()
    arguments.add_argument("path_to_chos", type=str, action='store')
    parsed_args = arguments.parse_args()
    quadrant_definitions = ["NW", "NE", "SW", "SE"]
    try:
        chos = scandir(parsed_args.path_to_chos)
        chos = [x.path for x in chos]
        count = 0
        for a_cho in chos:
            cho_id = "{}".format(basename(a_cho))
            manifest_id = "https://iiif-manifest.lib.uchicago.edu/maps/chicago_1890/" + cho_id + "/" + cho_id + ".json"
            outp = {}
            outp["@context"] = "http://iiif.io/api/presentation/2/context.json"
            outp["@id"] =  manifest_id
            outp["@type"] = "sc:Manifest"
            outp["metadata"] = []
            tifs = scandir(join(a_cho, "tifs"))
            for n_tif in tifs:
                src = n_tif.path
                dest = basename(n_tif.path)
                dest = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/maps/", basename(a_cho), "tifs", dest)
                new = "/"
                for n_dir in dirname(dest).split('/'):
                    new = join(new, n_dir)
                    if not exists(new):
                        mkdir(new)
                count += 1
                #copyfile(src, dest)
            metadata = scandir(join(a_cho, "metadata"))
            cho_mdata = [x.path for x in metadata] 
            cho_metadata_file = cho_mdata[-1]
            title = None
            author = None
            descriptions = None
            publisher = None
            with open(cho_metadata_file, "rb") as read_file:
                reader = MARCReader(read_file)
                for record in reader:
                    title = record.title()
                    author = record.author()
                    descriptions = [x.value() for x in record.physicaldescription()]
                    date = record.pubyear()
                    publisher = record.publisher()
            if title:
                outp["label"] = title
                outp["metadata"].append({"label": "Title", "value": title})
            if author:
                outp["metadata"].append({"label": "Creator", "value": author})
            if descriptions:
                description_text = '\n'.join(descriptions)
                outp["description"] = title
            if publisher:
                outp["metadata"].append({"label": "Publisher", "value": publisher})
            if date:
                outp["metadata"].append({"label": "Date", "value": date})
            outp["logo"] = "https://www.lib.uchicago.edu/static/base/images/color-logo.png"
            outp["license"] = "https://creativecommons.org/licenses/by-nc/4.0/"
            outp["attribution"] = "University of Chicago Library"
            outp["viewingDirection"] = "left-to-right"
            outp["viewingHint"] = "non-paged"
            outp["sequences"] = []
            seq_id = uuid4().urn.split(":")[-1]
            a_seq = {}
            a_seq["@id"] = "http://" + seq_id
            a_seq["@type"] = "sc:Sequence"
            a_seq["canvases"] = []
            tifs_path = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/maps/", quote(cho_id, safe=""), "tifs")
            if exists(tifs_path):
                tifs = scandir(tifs_path)
                tifs = [x.path for x in tifs]
            else:
                pass
                tifs = []
            if len(tifs) > 1:
                filler_list = ["" for x in range(len(tifs))]
                quadrant_definitions = ["NW", "NE", "SW", "SE"]
                for a_tif in tifs:
                    the_img = a_tif
                    a_canvas = {}
                    canvas_id = uuid4().urn.split(":")[-1]
                    a_canvas["@context"] = ""
                    a_canvas["@id"] = "http://" + canvas_id
                    a_canvas["@type"] = "sc:Canvas"
                    a_canvas["label"] = ""
                    if '-NW' in the_img:
                        a_canvas["label"] = "NW"
                    elif '-NE' in the_img:
                        a_canvas["label"] = "NE"
                    elif '-SW' in the_img:
                        a_canvas["label"] = "SW"
                    elif '-SE' in the_img:
                       a_canvas["label"] = "SE"
                    elif '-verso' in the_img:
                       a_canvas["label"] = "verso"
                    elif '-recto' in the_img:
                       a_canvas["label"] = "recto"
 
                    else:
                        a_canvas["label"] = "A map"
                    try:
                        f = open(the_img, "rb")
                        img = Image.open(f)
                        width, height = img.size
                        a_canvas["height"] = height
                        a_canvas["width"] = width
                    except OSError:
                        with open(join(getcwd(), "errors.txt"), "a+", encoding="utf-8") as write_file:
                            write_file.write("{}\n".format(the_img))
                    except Image.DecompressionBombError:
                        the_info = magic.from_file(the_img)
                        height = [x for x in the_info if "height=" in x]
                        width = [x for x in the_info if "width=" in x]
                        if width and height:
                            height = height[0].split('=')[1]
                            width = width[0].split('=')[1]
                            a_canvas["height"] = height
                            a_canvas["width"] = width
                        else:
                            pass
                    try:
                        h = a_canvas["height"]
                        w = a_canvas["width"]
                    except KeyError:
                        a_canvas["height"] = 800
                        a_canvas["width"] = 500
                    an_img = {}
                    an_img["@context"] = "http://iiif.io/api/presentation/2/context.json"
                    img_id = uuid4().urn.split(":")[-1]
                    an_img["@id"] = "http://" + img_id
                    an_img["@type"] = "oa:Annotation"
                    an_img["motivation"] = "sc:Painting"
                    an_img["resource"] = {}
                    tif_id = the_img.split("IIIF_Files")
                    tif_id = quote(tif_id[1], safe="")
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
            elif len(tifs) == 1:
                the_img = tifs[0]
                a_canvas = {}
                canvas_id = uuid4().urn.split(":")[-1]
                a_canvas["@id"] = "http://" + canvas_id
                a_canvas["@type"] = "sc:Canvas"
                a_canvas["label"] = "Map"
                try:
                    f = open(the_img, "rb")
                    img = Image.open(f)
                    width, height = img.size
                    a_canvas["height"] = height
                    a_canvas["width"] = width
                except OSError:
                    with open(join(getcwd(), "errors.txt"), "a+", encoding="utf-8") as write_file:
                        write_file.write("{}\n".format(a_file))
                except Image.DecompressionBombError:
                    the_info = magic.from_file(the_img)
                    height = [x for x in the_info if "height=" in x]
                    width = [x for x in the_info if "width=" in x]
                    if width and height:
                        height = height[0].split('=')[1]
                        width = width[0].split('=')[1]
                        a_canvas["height"] = height
                        a_canvas["width"] = width
                an_img = {}
                an_img["@context"] = "http://iiif.io/api/presentation/2/context.json"
                img_id = uuid4().urn.split(":")[-1]
                an_img["@id"] = "http://" + img_id
                an_img["@type"] = "oa:Annotation"
                an_img["motivation"] = "sc:Painting"
                an_img["resource"] = {}
                tif_id = the_img.split("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/")[1]
                tif_id = quote(tif_id, safe="")
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
            elif len(tifs) == 0:
                with open(join(getcwd(), "maps_without_tiffs.txt"), "a+") as af:
                    af.write("{}\n".format(a_cho))
            copy = a_seq["canvases"]
            for n_canvas in a_seq["canvases"]:
                label = n_canvas["label"]
                if label == 'NW':
                    old_first = copy[0]
                    n_canvas_pos = copy.index(n_canvas)
                    copy[0] = n_canvas
                    copy[n_canvas_pos] = old_first
                elif label == 'NE':
                    old_first = copy[1]
                    n_canvas_pos = copy.index(n_canvas)
                    copy[1] = n_canvas
                    copy[n_canvas_pos] = old_first
                elif label == 'SW':
                    old_first = copy[2]
                    n_canvas_pos = copy.index(n_canvas)
                    copy[2] = n_canvas
                    copy[n_canvas_pos] = old_first
                elif label == 'SE':
                    old_first = copy[3]
                    n_canvas_pos = copy.index(n_canvas)
                    copy[3] = n_canvas
                    copy[n_canvas_pos] = old_first
                if label == 'recto':
                    old_first = copy[0]
                    n_canvas_pos = copy.index(n_canvas)
                    copy[0] = n_canvas
                    copy[n_canvas_pos] = old_first
                if label == 'verso':
                    old_first = copy[1]
                    n_canvas_pos = copy.index(n_canvas)
                    copy[1] = n_canvas
                    copy[n_canvas_pos] = old_first
                resource_id = n_canvas["images"][0]["resource"]["@id"].lower()
                matches = [x for x in copy if x["images"][0]["resource"]["@id"].lower() == resource_id]
                if len(matches) > 1:
                    valid_op = matches[0]
                    rest = matches[1:]
                    for n in rest:
                        pos = copy.index(n)
                        del copy[pos]

            a_seq["canvases"] = copy
            outp["sequences"].append(a_seq)
            json_filepath = join("maps", cho_id, cho_id + ".json")
            json_filepath = join(getcwd(), "manifests", json_filepath)
            json_filepath_dirs = dirname(json_filepath)
            new_json_path = "/"
            for n in json_filepath_dirs.split("/"):
                new_json_path = join(new_json_path, n)
                if not exists(new_json_path):
                    mkdir(new_json_path)
            with open(json_filepath, "w+") as write_file:
                json.dump(outp, write_file, indent=4)
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(_main())
