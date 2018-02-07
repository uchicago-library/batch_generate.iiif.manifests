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
        metadata_records = {}
        for n in data:
            manifest_id = uuid4().urn.split(":")[-1]
            outp = {}
            outp["@context"] = "http://iiif.io/api/presentation/2/context.json"
            outp["@id"] = "http://" + manifest_id
            outp["@type"] = "sc:Manifest"
            outp["metadata"] = []
            identifier = 'gms-' + n.zfill(4)

            metadata_records[identifier] = []
            """
            tif_files = data[n]["files"]
            dest_root = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/goodspeed", identifier)
            dest_tif_root = join(dest_root, "tifs")
            if not exists(dest_root):
                mkdir(dest_root)
            if not exists(dest_tif_root):
                mkdir(dest_tif_root)
            for a_tif in tif_files:
                src = a_tif
                dest = basename(a_tif)
                dest = join(dest_tif_root, dest)
                if not exists(dest):
                    copyfile(src, dest)
                else:
                    print("{}->{}".format(src,dest))
            """
            tei_metadata = data[n]["tei_metadata_file"]
            marc_metadata = data[n]["marc_metadata_file"]
            metadata = []
            if tei_metadata:
                xml = ElementTree.parse(tei_metadata)
                root = xml.getroot()
                title = root.find("teiHeader/fileDesc/sourceDesc/msDescription/msHeading/title")
                alt_title = root.find("teiHeader/fileDesc/sourceDesc/msDescription/msHeading/otherName")
                orig_place = root.find("teiHeader/fileDesc/sourceDesc/msDescription/msHeading/origPlace")
                orig_date = root.find("teiHeader/fileDesc/sourceDesc/msDescription/msHeading/origDate")
                textLang = root.find("teiHeader/fileDesc/sourceDesc/msDescription/msHeading/textLang")
                descriptions = [re.sub(re.sub(r"\n", "", x.text), '\s{2,}', ' ') for x in root.findall("teiHeader/fileDesc/sourceDesc/msDescription/msContents/overview/p")]
                keywords = root.findall("teiHeader/profileDesc/textClass/keywords/term")
                if keywords:
                    for keyword in keywords:
                        outp['metadata'].append({"label": "Keyword", "value": keyword.text})
                if alt_title:
                    outp['metadata'].append({"label": "Alternate Title", "value": alt_title.text})
                if orig_place:
                    outp['metadata'].append({"label": "Originating Place", "value": orig_place.text})
                if textLang:
                    outp['metadata'].append({"label": "Language", "value": textLang.text})
                if descriptions:
                    outp['description'] = descriptions[0]
                outp['label'] = title.text
            elif marc_metadata:
                try:
                    with open(marc_metadata, "rb") as fh:
                        reader = MARCReader(fh)
                        for record in reader:
                            title = record['245']['a'].replace(':','').lstrip()
                            descriptions = '\n'.join([x['a'] for x in record.get_fields('520')])
                            outp['label'] = title
                            outp["description"] = descriptions
                            subjs = [x.value() for x in record.get_fields('630')]
                            subjs_more = [x.value() for x in record.get_fields('650')]
                            for s in subjs:
                                outp['metadata'].append({"label": "Keyword", "value": s})
                            for s in subjs_more:
                                outp['metadata'].append({"label": "Keyword", "value": s})
                except RecordLengthInvalid:
                    print(marc_metadata)
            else:
                pass
                #stdout.write("{} has no descriptive metadata: this is an orphaned manuscript\n".format(identifier))
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
            tif_directory = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files", "gms", identifier, "tifs")
            tifs = scandir(tif_directory)
            tifs = sorted([x.path for x in tifs])
            for tif in tifs:
                print(tif)
                tif_path = tif.split("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/")[1]
                a_canvas = {}
                label_string = tif_path.split(".tif")[0].split("-")[-1]
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
