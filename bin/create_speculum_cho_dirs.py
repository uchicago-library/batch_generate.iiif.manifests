from os.path import join, exists, basename
from os import getcwd, mkdir, scandir
import json
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
        outp["@id"] = manifest_id
        outp["@type"] = "sc:Manifest"
        metadata = [] 
        source_id = work.attrib["id"]
        metadata.append({"label": "Identifier", "value": source_id})
        geographic_name = work.find("locationSet/location[@type='creation']/name")
        subjects = work.findall("subjectSet/subject/term")
        agents = work.findall("agentSet/agent")
        inscriptions = work.findall("inscriptionSet/inscription")
        descriptions = work.findall("descriptionSet/description")
        technique = work.find("techniqueSet/display")
        signature = work.find("inscriptionSet/inscription/text[@type='signature']")
        huref = work.find("huref")
        title = work.find("titleSet/titlte")
        measurement = work.find("measurementSet/display")
        publication_date = work.find("dateSet/display")
        reference = work.find("textrefSet/textref/name")
        if reference:
            metadata.append({"label": "Reference", "value": reference.text})
        if publication_date:
            metadata.append({"label": "Publication Date", "value": publication_date.text})
        if measurement:
            metadata.append({"label": "Measurement", "value": measurement.text})
        if title:
            metadata.append({"label": "Title", "value": title.text})
            outp["label"] = title.text
        if huref:
            metadata.append({"label": "Huelsen Number", "value": huref.text})
        if descriptions:
            metadata.append({"label": "Description", "value": descriptions[0].text})
            outp["description"] = descriptions[0].text
        chicago_number = work.find("id").text
        metadata.append({"label": "Chicago Number", "value": chicago_number})
        inscription_list = []
        for inscription in inscriptions:
            an_inscription = {}
            position = inscription.find("position")
            if position:
                position_text = position.text
            else:
                position_text = None
            text = inscription.findall("text")
            for a_text in text:
                if a_text.attrib.get("type"):
                    if a_text.attrib["type"] == "translation":
                        an_inscription["translation"] = {}
                        an_inscription["translation"]["position"] = position_text
                        an_inscription["translation"]["text"] = a_text.text
                        if position_text:
                            key_name = "Translation ({})".format(position_text)
                            metadata.append({"label": key_name, "value": a_text.text})
                        else:
                            metadata.append({"label": "Translation", "value": a_text.text})
                    elif a_text.attrib["type"] == "text":
                        if position_text:
                            key_name = "Text ({})".format(position_text)
                            metadata.append({"label": key_name, "value": a_text.text})
                        else:
                            metadata.append({"label": "Text", "value": a_text.text})
                    elif a_text.attrib["type"] == "caption":
                            metadata.append({"label": "Caption", "value": a_text.text})
                else:
                    print(source_id)
            inscription_list.append(an_inscription)
        for agent in agents:
            agent_name = agent.find("name").text
            role = agent.find("role").text
            role = role[0].upper() + role[1:]
            agent_str = "{} ({})".format(agent_name, role)
            metadata.append({"label": role, "value": agent_name})
        subject_counter = {}
        if subjects:
            for subj in subjects:
                subject_type = subj.attrib["type"]
                subject_standard = subj.attrib["vocab"]
                subject_key = "{} ({})".format(subject_type, subject_standard)
                if subject_counter.get(subject_key):
                    tally = subject_counter[subject_key]
                    tally += 1
                    subject_counter[subject_key] = tally
                else:
                    subject_counter[subject_key] = 1
                key_num = subject_counter[subject_key]
                subject_key += " " + str(key_num)
                metadata.append({"label": subject_key, "value": subj.text})
        if geographic_name is None:
            empty_locs += 1
            metadata.append({"label": "Location (\"creation\")", "value": "Unknown"})
        else:
            loc = geographic_name.text
            metadata.append({"label": "Location (\"creation\")", "value": loc})
            unique_locs.add(loc)
        if technique:
            metadata["Technique"] = technique.text
            metadata.append({"label": "Technique", "value": loc})
        if signature:
            metadata["Signature"] = technique.text
            metadata.append({"label": "Signature", "value": loc})
        outp["metadata"] = metadata
        if exists(join(getcwd(), "chos", source_id)):
            with open(join(getcwd(), "chos", source_id, "manifest.json"), "w+", encoding="utf-8") as write_file:
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
