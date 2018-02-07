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
    arguments.add_argument("mods_metadata_loc", action='store', type=str)
    arguments.add_argument("tifs_loc", action='store', type=str)
    parsed_args = arguments.parse_args()
    try:
        mods_files = scandir(parsed_args.mods_metadata_loc)
        tif_dirs = [x.path for x in scandir(parsed_args.tifs_loc)]
        organization = []
        for n in mods_files:
            an_org = {}
            mdata_type, project, record = basename(n.path).split('.')[0].split('-')
            tif_id = project + record
            an_org["mods_file"] = n.path
            an_org["identifier"] = "chopin-" + record
            an_org["tif_files"] = []
            for p in tif_dirs:
                if tif_id in p:
                    for n in scandir(p):
                        an_org["tif_files"].append(n.path)
            organization.append(an_org)
        json_filepath = join(getcwd(), "chopin_org.json")
        print(json_filepath)
        total_n = 0 
        total_tifs = 0
        for n in organization:
            total_n += 1
            identifier = n["identifier"]
            n_cho_dir = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/chopin", identifier)
            n_manifest_dir = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Manifests/chopin", identifier)
            n_cho_tifs = join(n_cho_dir, "tifs")
            if not exists(n_manifest_dir):
                mkdir(n_manifest_dir)
            if not exists(n_cho_dir):
                mkdir(n_cho_dir)
            if not exists(n_cho_tifs):
                mkdir(n_cho_tifs)
            tifs = n["tif_files"]
            for a_tif in tifs:
                total_tifs += 1
                src = a_tif
                dest = identifier + '-' + basename(src).split('.tif')[0].split('-')[1] + ".tif.bz2"
                dest = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files", "chopin", identifier, "tifs", dest)
                new = "/"
                #for n in dirname(dest).split("/"):
                #    new = join(new, n)
                #    if not exists(new):
                #        print(new)
                #copyfile(src, dest)
        print(total_n)
        print(total_tifs)
        with open(json_filepath, "w+", encoding="utf-8") as wf:
            json.dump(organization, wf, indent=4)

        #for n in tif_dirs:
        #    print(n)

        """
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
        """
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(main())
