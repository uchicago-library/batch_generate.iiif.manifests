from os.path import join, exists, basename
from os import getcwd, mkdir, scandir
import json
from PIL import Image
import re
from shutil import copyfile
from uuid import uuid4
from xml.etree import ElementTree

def find_particular_tif_files(path, pattern=None):
    for something in scandir(path):
        if something.is_dir():
            yield from find_particular_tif_files(something.path, pattern=pattern)
        elif something.is_file():
            regex = pattern + r".*tif$"
            match = re.compile(regex)
            if match.search(something.path):
                yield something.path

def clean_text_data(a_simple_element):
    try:
        value = a_simple_element.text
        value = re.sub("\n", "", value)
        value = re.sub("\s{2,}", " ", value)
    except TypeError:
        value = None
    return value

def make_metadata_definition(label, value, metadata=[], source=None):
    if isinstance(value, ElementTree.Element):
        value = clean_text_data(value)
    elif isinstance(value, str):
        value = value
    if label and value:
        metadata.append({"label": label, "value": value})
    return metadata

if __name__ == "__main__":
    metadata_filepath = "speculum.xml"
    tifs_filepath = "/data/voldemort/digital_collections/data/ldr_oc_admin/files/DC_Work_in_progress/Speculum/2013-242"
    mdata = ElementTree.parse(metadata_filepath)
    root = mdata.getroot()
    works = mdata.findall("work")
    empty_locs = 0
    unique_locs = set([])
    for work in works:
        manifest_id = uuid4().urn.split(":")[-1]
        outp = {}
        outp["@context"] = "http://iiif.io/api/presentation/2/context.json"
        outp["@id"] = "http://" + manifest_id
        outp["@type"] = "sc:Manifest"
        metadata = []

        source_id = work.attrib["id"]
        geographic_name = work.find("locationSet/location[@type='creation']/name")
        subjects = work.findall("subjectSet/subject/term")
        agents = work.findall("agentSet/agent")
        inscriptions = work.findall("inscriptionSet/inscription")
        descriptions = work.findall("descriptionSet/description")
        desc = ""
        if len(descriptions) > 1:
            for something in descriptions:
                if something.getchildren():
                    data = str(ElementTree.tostring(something))
                    data = re.sub(r"<description source=\".*\">", "", data)
                    data = re.sub(r"</description>", "", data)
                    data = re.sub(r"\s{2,}", " ", data)
                    data = re.sub(r"\\n", "", data)
                    desc += " "  + data
                else:
                    desc = re.sub("\n", "", something.text)
                    desc = re.sub("\s{2,}", " ", desc)
                    desc = desc
            make_metadata_definition("Description", desc, metadata=metadata)
            outp["description"] = desc
        elif len(descriptions) == 1:
            desc = clean_text_data(descriptions[0])
            if desc:
                outp["description"] = desc
                make_metadata_definition("Description", desc, metadata=metadata)
        else:
            pass
        technique = work.find("techniqueSet/display")
        signature = work.find("inscriptionSet/inscription/text[@type='signature']")
        huref = work.find("huref")
        title = work.find("titleSet/title")
        measurement = work.find("measurementSet/display")
        publication_date = work.find("dateSet/display")
        reference = work.find("textrefSet/textref/name")
        chicago_number = work.find("id")
        outp["label"] = clean_text_data(title)
        metadata = make_metadata_definition("Reference", reference, metadata=metadata)
        metadata = make_metadata_definition("Publication Date", publication_date, metadata=metadata)
        metadata = make_metadata_definition("Measurement", measurement, metadata=metadata)
        metadata = make_metadata_definition("Title", title, metadata=metadata)
        metadata = make_metadata_definition("Huelsen Number", huref, metadata=metadata)
        metadata = make_metadata_definition("Chicago Number", chicago_number, metadata=metadata)
        metadata = make_metadata_definition("Location (creation)", geographic_name, metadata=metadata)
        metadata = make_metadata_definition("Technique", technique, metadata=metadata)
        metadata = make_metadata_definition("Technique", signature, metadata=metadata)
        for subj in subjects:
            subject_type = subj.attrib["type"]
            subject_standard = subj.attrib["vocab"]
            subject_key = "{} ({})".format(subject_type, subject_standard)
            metadata = make_metadata_definition(subject_key, subj, metadata=metadata)
        for agent in agents:
            agent_name = agent.find("name").text
            role = agent.find("role").text
            key_name = role[0].upper() + role[1:]
            agent_str = "{}".format(agent_name)
            metadata = make_metadata_definition(key_name, agent_str, metadata=metadata)
        for inscription in inscriptions:
            position = inscription.find("position")
            if position:
                position_text = position.text
            else:
                position_text = None
            text = inscription.findall("text")
            for a_text in text:
                key_name = None
                if a_text.attrib.get("type") == "translation":
                    key_name = "Translation"
                elif a_text.attrib.get("type") == "text":
                    key_name = "Text"
                if position_text:
                    key_name += " ({})".format(position_text)
        outp["metadata"] = metadata
        outp["sequences"] = []
        sequence_id = uuid4().urn.split(":")[-1]
        a_seq = {}
        a_seq["@id"] = "http://" + sequence_id
        a_seq["@type"] = "sc:Sequence"
        a_seq["canvases"] = []
        chos = scandir(join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/speculum"))
        print(source_id)
        for a_directory in chos:
            if source_id in a_directory.path:
                tifs = scandir(join(a_directory.path, "tifs"))
                for tif in tifs:
                    the_img = tif.path
                    try:
                        img = Image.open(the_img)
                        width, height = img.size
                    except OSError:
                        print("{} could not be opened to get size info".format(the_img))
                    except Image.DecompressionBombError:
                        print("{} got a DecompressionBombError".format(the_img))
                        the_info = magic.from_file(the_img).split(',')
                        height = [x for x in the_info if "height=" in x]
                        width = [x for x in the_info if "width=" in x]
                        if width and height:
                            height = height[0].split('=')[1]
                            width = width[0].split('=')[1]
                            a_canvas["height"] = height
                            a_canvas["width"] = width

                    tif_id = the_img.split(join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/"))[1]
                    print(tif_id)
                    a_canvas = {}
                    canvas_id = uuid4().urn.split(":")[-1]
                    a_canvas["@id"] = "http://" + canvas_id
                    a_canvas["@type"] = "sc:Canvas"
                    a_canvas["label" ] = "Image"
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
                    a_seq["canvases"].append(a_canvas)
        outp["sequences"].append(a_seq)
        cho_dir = join(getcwd(), "chos", source_id)
        print(cho_dir)
        if not exists(cho_dir):
            mkdir(cho_dir)
        if exists(cho_dir):
            with open(join(cho_dir, source_id + ".json"), "w+", encoding="utf-8") as write_file:
                json.dump(outp, write_file, indent=4)

    #list_unique_locs = list(unique_locs)
    #new_list = sorted(list_unique_locs)
            #for a_tif in tifs:
            #    tif_src = a_tif
            #    tif_dest = join("/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/", "speculum", source_id, "tifs", basename(a_tif))
            #    copyfile(tif_src, tif_dest)
    #xml = ElementTree.parse(metadata_filepath)
    #root = xml.getroot()
    #works = root.findall("work")
    #for doc in works:
    #    source_id = doc.attrib["id"]
    #    print(source_id)
    #    doc.write(filepath)
    #    print(filepath)
