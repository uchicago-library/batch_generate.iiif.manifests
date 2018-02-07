from argparse import ArgumentParser
from os import _exit, scandir, listdir, getcwd, makedirs, mkdir
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

"""
{
  "@context": "http://iiif.io/ai/presentations/2/context.json",
  "@id": "http:///[id]",
  "@type": "sc:Manifest",
  "label": "[label]",
  "metadata": [
  ],
  "description": "[description]",
  "license": "http://creativecommons.org/licenses/by/3.0/",
  "attributation": "[attribution text]",
  "sequences": [
      {
          "@id": "http://[id of sequence]",
          "@type": "sc:Sequence",
          "label": "Normal Sequence",
          "canvases": [
              {
                "@id": "http:/[id of canvas]",
                "@type": "sc:Canvas",
                "label": "Page [number]",
                "height": [height of canvas],
                "width": [width of canvas],
                "images": [
                    {
                        "@context": "http://iiif.io/api/presentation/2/context.json",
                        "@id": "http://[id of image]",
                        "@type": "oa:Annotation",
                        "motivation": "sc:Painting",
                        "resource": {
                            "@id": [uri for a iiif image]",
                            "@type": "dctypes:Image",
                            "format": "image/jpeg",
                            "service": {
                                "@context": "http://iiif.io/api/image/2/context.json",
                                "@id": "[uri for the iiif image]",
                                "profile": [
                                    "http://iiif.io/api/image/2/level2.json",
                                    {
                                        "supports": [
                                           "conanicalLinkHeader",
                                           "profileLinkHeader",
                                           "mirroring",
                                           "rotationArbitrary",
                                           "regionSquare",
                                           "sizeAboveFull"
                                        ],
                                        "qualities": [
                                            "default",
                                            "gray",
                                            "bitonal"
                                        ],
                                        "formats": [
                                            "jpg",
                                            "png",
                                            "gif",
                                            "webp"
                                        ]
                                    }
                                ]
                            }
                        }
                    }
                ]
              }
          ]
      }
  ]
}
"""
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
        for a_cho in chos:
            print(a_cho)
            manifest_id = uuid4().urn.split(":")[-1]
            outp = {}
            outp["@context"] = "http://iiif.io/api/presentation/2/context.json"
            outp["@id"] = "http://" + manifest_id
            outp["@type"] = "sc:Manifest"
            outp["metadata"] = []
            tifs = scandir(join(a_cho, "tifs"))
            metadata = scandir(join(a_cho, "metadata"))
            cho_mdata = [x.path for x in metadata]
            cho_tifs = [x.path for x in tifs]
            cho_id = basename(a_cho)
            cho_mdata = sorted(cho_mdata)
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
                outp["metadata"].append({"label": "Title", "value": title})
                outp["label"] = title
            if author:
                outp["metadata"].append({"label": "Author", "value": author})
            if date:
                outp["metadata"].append({"label": "Author", "value": date})
            if publisher:
                outp["metadata"].append({"label": "Publisher", "value": publisher})
            if descriptions:
                outp["metadata"].append({"label": "Description", "value": descriptions[0]})
                outp["description"] = descriptions[0]
            outp["license"] = ""
            outp["attribution"] = "University of Chicago Library"
            outp["viewingDirection"] = "left-to-right"
            outp["viewingHint"] = "non-paged"
            outp["sequences"] = []
            seq_id = uuid4().urn.split(":")[-1]
            a_seq = {}
            a_seq["@id"] = "http://" + seq_id
            a_seq["@type"] = "sc:Sequence"
            a_seq["canvases"] = []
            tifs = scandir(join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/maps/", cho_id, "tifs"))
            tifs = [x.path for x in tifs]
            if len(tifs) > 1:
                filler_list = ["" for x in range(len(tifs))]
                for a_tif in tifs:
                    try:
                        f = open(the_img, "rb")
                        img = Image.open(f)
                        width, height = img.size
                    except OSError:
                        with open(join(getcwd(), "errors.txt"), "a+", encoding="utf-8") as write_file:
                            write_file.write("{}\n".format(a_file))
                        height = None
                        width = None
                    except Image.DecompressionBombError:
                        the_info = magic.from_file(the_img)
                        height = [x for x in the_info if "height=" in x]
                        width = [x for x in the_info if "width=" in x]
                        if width and height:
                            height = height[0].split('=')[1]
                            width = width[0].split('=')[1]
                    if a_tif.endswith("NW.tif"):
                        filler_list[0] = a_tif
                    elif a_tif.endswith("NE.tif"):
                        filler_list[1] = a_tif
                    elif a_tif.endswith("SW.tif"):
                        filler_list[2] = a_tif
                    elif a_tif.endswith("SE.tif"):
                        filler_list[3] = a_tif
                for an_item in filler_list:
                    the_img = an_item
                    a_canvas = {}
                    canvas_id = uuid4().urn.split(":")[-1]
                    a_canvas["@context"] = ""
                    a_canvas["@id"] = "http://" + canvas_id
                    a_canvas["@type"] = "sc:Canvas"
                    a_canvas["label"] = an_item.split('.')[0].split('-')[-1]
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
                        else:
                            pass
                    try:
                        print((a_canvas["height"], a_canvas["width"]))
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
                    tif_id = the_img.split("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/")[1]
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
                    a_canvas["images"] = [an_img]
                    a_seq["canvases"].append(a_canvas)
            else:
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
            outp["sequences"].append(a_seq)
            json_filepath = join("maps", cho_id, cho_id + ".json")
            json_filepath = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Manifests", json_filepath)
            json_filepath_dirs = dirname(json_filepath)
            print(json_filepath)
            with open(json_filepath, "w+", encoding="utf-8") as write_file:
                json.dump(outp, write_file, indent=4)
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(_main())
