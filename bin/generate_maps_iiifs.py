from argparse import ArgumentParser
from os import _exit, scandir, listdir, getcwd, makedirs, mkdir
from os.path import exists, join, basename, dirname
import json
from PIL import Image
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
        group = {}
        for n in chos:
            tifs = scandir(join(n, "tifs"))
            metadata = scandir(join(n, "metadata"))
            group[basename(n)] = {}
            group[basename(n)]["uppercase"] = []
            group[basename(n)]["lowercase"] = []
            cho_mdata = [x.path for x in metadata]
            cho_tifs = [x.path for x in tifs]
            cho_id = basename(n.path)
            tif_pattern = cho_id + r".*[.]tif|TIF"

            tif_pattern = re.compile(tif_pattern)
            cho_tif_count = 0
            cho_metadata_file = []
            md_count = 0
            cho_mdata = sorted(cho_mdata)
            cho_metadata_file = cho_mdata[-1]
            for tif in cho_tifs:
                if tif_pattern.search(tif):
                    cho_tif_count += 1
            if cho_tif_count == 2:
                final_tifs = [cho_tifs[0]]
            elif cho_tif_count == 1:
                final_tifs = cho_tifs
            elif cho_tif_count == 8:
                lower_count = 0
                upper_count = 0
                for n_tif in cho_tifs:
                    if n_tif.endswith(".tif"):
                        lower_count += 1
                    elif n_tif.endswith(".TIF"):
                        upper_count += 1
                if upper_count == lower_count:
                    final_tifs = [x for x in cho_tifs if x.endswith(".tif")]
            print(cho_id)
            cho_base_dest = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/maps/", cho_id)
            if not exists(cho_base_dest):
                mkdir(cho_base_dest)
            for a_tif in final_tifs:
                basef = basename(a_tif).split('.')[0]
                match = (re.compile('(_copy\d{1})').search(basef))
                if match:
                    basef = (basef.replace(match.groups(1)[0], ''))
                else:
                    basef = basef
                cho_tif_dir = join(cho_base_dest, "tifs")
                if not exists(cho_tif_dir):
                    mkdir(cho_tif_dir)
                dest = join(cho_tif_dir, basef + ".tif")
                src = a_tif
                if not exists(dest):
                    copyfile(src, dest)
                    print(src)
                    print(dest)
            print("--")
        """
        total_groups = 0
        for n in group:
            total_groups += 1
            the_files = []
            uppers = group[n]['uppercase']
            lowers = group[n]['lowercase']
            if len(uppers) != len(lowers):
                if len(uppers) > 0:
                    the_files = uppers
                else:
                    the_files = lowers
            else:
                the_files = lowers
            only_copy2 = [x for x in the_files if 'copy2' in x]
            only_copy1 = [x for x in the_files if 'copy1' in x]
            new_copy2 = []
            new_copy1 = []
            for c in only_copy2:
                new_string = c.replace('_copy2', '')
                new_copy2.append(new_string)
            for c in only_copy1:
                new_string = c.replace('_copy1', '')
                new_copy1.append(new_string)
            if (not (set(new_copy1) - set(new_copy2))) and (only_copy2 and only_copy2):
                single_file_src = only_copy2[0]
                dest = single_file_src.split(parsed_args.path_to_chos+"/")[1].replace('_copy2','')
                dest = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/maps", dest)

                final_group[n]["files"].append({"src": only_copy2[0], "dest": dest})
            if len(lowers) == 1:
                dest = lowers[0].split(parsed_args.path_to_chos+"/")[1]
                dest = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/maps", dest)
                final_group[n]["files"].append({"src":lowers[0], "dest":dest})

            ne_quad = [x for x in the_files if 'NE' in x]
            nw_quad = [x for x in the_files if 'NW' in x]
            se_quad = [x for x in the_files if 'SE' in x]
            sw_quad = [x for x in the_files if 'SW' in x]
            recto_side = [x for x in the_files if 'recto' in x]
            verso_side = [x for x in the_files if 'verso' in x]
            print(recto_side)
            print(verso_side)
            if len(recto_side) == 1:
                recto_dest = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/maps", n, "tifs", basename(recto_side[0]))
                final_group[n]["files"].append({"src":recto_side[0], "dest":dest})
            if len(verso_side) == 1:
                verso_dest = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/maps", n, "tifs", basename(verso_side[0]))
                final_group[n]["files"].append({"src":verso_side[0], "dest":dest})
            if len(ne_quad) == 1:
                ne_dest = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/maps", n, "tifs", basename(ne_quad[0]))
                final_group[n]["files"].append({"src":ne_quad[0], "dest":dest})
            if len(nw_quad) == 1:
                nw_dest = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/maps", n, "tifs", basename(nw_quad[0]))
                final_group[n]["files"].append({"src":nw_quad[0], "dest":dest})
            if len(se_quad) == 1:
                se_dest = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/maps", n, "tifs", basename(se_quad[0]))
                final_group[n]["files"].append({"src":se_quad[0], "dest":dest})
            if len(sw_quad) == 1:
                sw_dest = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/maps", n, "tifs", basename(sw_quad[0]))
                final_group[n]["files"].append({"src":sw_quad[0], "dest":dest})
        counter = 0
        missing_files = 0
        has_files = 0
        for n in final_group:
            print("---")
            print(n)
            if n == "G4104-C6-1893-R3":
                print(final_group[n]["files"])
        """
        """
            if len(final_group[n]["files"]) == 0:
                print("has no files")
                missing_files += 1
            else:
                has_files += 1
            for a_file in final_group[n]["files"]:
                print(a_file["dest"])
            counter += 1
        print(missing_files)
        print(has_files)
        print(counter)
        """
        """
            for t in tifs:
                relpath = t.path.split(parsed_args.path_to_photos+"/")[1]
                src = t
                dest = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/mepa/", relpath)
                new = "/"
                print(dest)
                for n in dirname(dest).split('/'):
                    new = join(new, n)
                    print(new)
                    if not exists(new):
                        mkdir(new)
                print("{} to {}".format(src.path, dest))
                copyfile(src.path, dest)
            outp = {}
            try:
                json_mdata_path = [join(n, x) for x in listdir(n) if '.json' in x][0]
            except FileNotFoundError:
                print("hi")
            json_data = json.load(open(json_mdata_path, "r", encoding="utf-8"))
            manifest_id = uuid4().urn.split(":")[-1]
            outp["@context"] = "http://iiif.io/api/presentation/2/context.json"
            outp["@id"] = "http://" + manifest_id
            outp["@type"] = "sc:Manifest"
            outp["metadata"] = []
            outp["license"] = "http://photoarchive.lib.uchicago.edu/rights.html"
            outp["attribution"] = "University of Chicago Library"
            json_src = json_mdata_path
            manifest_dest_relpath = json_src.split(parsed_args.path_to_photos + "/")[1]
            manifest_dest = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Manifests/mepa", manifest_dest_relpath)
            original_metadata = json.load(open(json_src, "r", encoding="utf-8"))
            outp["metadata"] = []
            for n in original_metadata:
                if n == "Description" and original_metadata[n] != "":
                    outp["description"] = original_metadata[n]
                if n == "Title":
                    outp["label"] = original_metadata[n]
                if original_metadata[n] != '':
                    outp["metadata"].append({"label": n, "value": original_metadata[n]})
            outp["attribution"] = "University of Chicago Library"
            outp["sequences"] = []
            sequence_id = uuid4().urn.split(":")[-1]
            a_seq = {}
            a_seq["@id"] = "http://" + sequence_id
            a_seq["@type"] = "sc:Sequence"
            a_seq["canvases"] = []
            tif_directory = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/mepa", basename(manifest_dest).split('.json')[0], "tifs")
            if exists(tif_directory):
                tifs = scandir(tif_directory)
                for tif in tifs:
                    the_img = tif.path
                    try:
                        img = Image.open(the_img)
                        width, height = img.size
                    except OSError:
                        print("{} could not be opened to get size info".format(the_img))
                    except Image.DecompressionBombError:
                        print("{} got a DecompressionBombError".format(the_img))
                    label_string = ""

                    tif_id = tif.path.split("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/")[1]
                    if tif_id.endswith("r.tif"):
                        label_string = "recto"
                    else:
                        label_string = "verso"
                    a_canvas = {}
                    canvas_id = uuid4().urn.split(":")[-1]
                    a_canvas["@id"] = "http://" + canvas_id
                    a_canvas["@type"] = "sc:Canvas"
                    a_canvas["label" ] = label_string
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
                    an_img["resource"]["@id"] = "http://iiif-server.lib.uchicago.edu/" + tif_id +  "/full/full/0/default.jpg"
                    an_img["resource"]["@type"] = "dctypes:Image"
                    an_img["resource"]["format"] = "image/jpeg"
                    an_img["resource"]["height"] = height
                    an_img["resource"]["width"] = width
                    an_img["on"] = "http://" + canvas_id
                    an_img["resource"]["service"] = {}
                    an_img["resource"]["service"]["@context"] = "http://iiif.io/api/image/2/context.json"
                    an_img["resource"]["service"]["@id"] = "https://iiif-server.lib.uchicago.edu/" + tif_id
                    img_profile = {}
                    img_profile["supports"] = ["canonicalLinkHeader", "profileLinkHeader", "mirroring", "rotationArbitrary", "regionSquare", "sizeAboveFull"]
                    img_profile["qualities"] = ["default", "gray", "bitonal"]
                    img_profile["format"] = ["jpg", "png", "gif", "webp"]
                    an_img["resource"]["service"]["profile"] = ["http://iiif.io/api/image/2/level2.json", img_profile]
                    a_canvas["images"].append(an_img)
                    if label_string == "recto":
                        a_seq["canvases"].insert(0, a_canvas)
                    else:
                        a_seq["canvases"].append(a_canvas)
                outp["sequences"].append(a_seq)
            json_file_path = join(getcwd(), "manifests/mepa", manifest_dest_relpath)
            json_filepath_dirs = dirname(json_file_path)
            print(json_filepath_dirs)
            new = "/"
            for n in json_filepath_dirs.split('/'):
                new = join(new, n)
                if not exists(new):
                    mkdir(new)
            print(json_file_path)
            with open(json_file_path, "w+", encoding="utf-8") as write_file:
                json.dump(outp, write_file, indent=4)

            basef = basename(n).split('.tif')[0]
            mdata_filestring = 'oai_dc' + basef
            creators = None
            subjects = None
            identifiers = None
            titles = None
            dates = None
            formats = None
            main_identifier = n.split("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/")[1]
            outp = {}
            manifest_id = uuid4().urn.split(":")[-1]
            outp["@context"] = "http://iiif.io/api/presentation/2/context.json"
            outp["@id"] = "http://" + manifest_id
            outp["@type"] = "sc:Manifest"
            outp["metadata"] = []
            outp["license"] = "http://photoarchive.lib.uchicago.edu/rights.html"
            outp["attribution"] = "University of Chicago Library"
            for m in metadata:
                if basef in m:
                    root = ElementTree.parse(m).getroot()
                    titles = [x.text for x in root.findall("{http://purl.org/dc/elements/1.1/}title")]
                    creators = [x.text for x in root.findall("{http://purl.org/dc/elements/1.1/}creator")]
                    dates = [x.text for x in root.findall("{http://purl.org/dc/elements/1.1/}date")]
                    identifiers = [x.text for x in root.findall("{http://purl.org/dc/elements/1.1/}identifier")]
                    subjects = [x.text for x in root.findall("{http://purl.org/dc/elements/1.1/}subject")]
                    formats = [x.text for x in root.findall("{http://purl.org/dc/elements/1.1/}format")]

                    description = root.find("{http://purl.org/dc/elements/1.1/}description")
                    if description:
                        outp["description"] = description.text
                        print(description)
                    for title in titles:
                        outp["metadata"].append({"label": "Title", "value": title})
                    for creator in creators:
                        outp["metadata"].append({"label": "Creator", "value": creator})
                    for date in dates:
                        outp["metadata"].append({"label": "Date", "value": date})
                    for identifier in identifiers:
                        outp["metadata"].append({"label": "Identifiers", "value": identifier})
                    for subject in subjects:
                        outp["metadata"].append({"label": "Subject", "value": subject})
                    for format in formats:
                        outp["metadata"].append({"label": "Format", "value": format})
                    outp["label"] = titles[0]
                    break
            outp["sequences"] = []
            outp["structures"] = []
            outp["viewingDirection"] = "left-to-right"
            sequence = {}
            sequence_id = uuid4().urn.split(":")[-1]
            sequence["@id"] = "http://" + sequence_id
            sequence["@type"] = "sc:Sequence"
            sequence["canvases"] = []
            canvas_id = uuid4().urn.split(":")[-1]
            the_img = n
            try:
                img = Image.open(the_img)
                width, height = img.size
            except OSError:
                print("{} could not be opened to get size info".format(the_img))
            except Image.DecompressionBombError:
                print("{} got a DecompressionBombError".format(the_img))
            a_canvas = {}
            a_canvas["@id"] = "http://" + canvas_id
            a_canvas["@type"] = "sc:Canvas"
            a_canvas["label" ] = "Photograph of " + title
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
            n_path = n.split("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/")[1]
            print(n_path)
            an_img["resource"]["@id"] = "http://iiif-server.lib.uchicago.edu/" + n_path +  "/full/full/0/default.jpg"
            an_img["resource"]["@type"] = "dctypes:Image"
            an_img["resource"]["format"] = "image/jpeg"
            an_img["resource"]["height"] = height
            an_img["resource"]["width"] = width
            an_img["on"] = "http://" + canvas_id
            an_img["resource"]["service"] = {}
            an_img["resource"]["service"]["@context"] = "http://iiif.io/api/image/2/context.json"
            an_img["resource"]["service"]["@id"] = "https://iiif-server.lib.uchicago.edu/" + n_path
            img_profile = {}
            img_profile["supports"] = ["canonicalLinkHeader", "profileLinkHeader", "mirroring", "rotationArbitrary", "regionSquare", "sizeAboveFull"]
            img_profile["qualities"] = ["default", "gray", "bitonal"]
            img_profile["format"] = ["jpg", "png", "gif", "webp"]
            an_img["resource"]["service"]["profile"] = ["http://iiif.io/api/image/2/level2.json", img_profile]
            a_canvas["images"].append(an_img)
            sequence["canvases"].append(a_canvas)
            outp["sequences"].append(sequence)
            json_file_name = main_identifier.split(".tif")[0] + ".json"
            json_file_path = join(getcwd(), "manifests", json_file_name)
            json_filepath_dirs = dirname(json_file_path)
            new = "/"
            for n in json_filepath_dirs.split('/'):
                new = join(new, n)
                if not exists(new):
                    mkdir(new)
            print(json_file_path)
            with open(json_file_path, "w+", encoding="utf-8") as write_file:
                json.dump(outp, write_file, indent=4)
        """
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(_main())
