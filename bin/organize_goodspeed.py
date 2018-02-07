from argparse import ArgumentParser
import csv
from os import _exit, listdir, scandir, getcwd
from os.path import join
import json

EXCEPTIONS = [
("/data/repository/ac/fpnrxkp1wj69p/0126","0126"),
("/data/repository/ac/fpnrxkp1wj69p/0133","masters 0133"),
("/data/repository/ac/fpnrxkp1wj69p/0715","masters 0715"),
("/data/repository/ac/fpnrxkp1wj69p/0727","masters 0727"),
("/data/repository/ac/fpnrxkp1wj69p/0879","croptif 0879"),
("/data/repository/ac/fpnrxkp1wj69p/1017","masters 1017")
]

ZERO_FILE_IDS = [
'128',
'130',
'134',
'166',
'202',
'275',
'828',
'902',
'948',
'951',
'972',
'1054'
]

MISSING_TIF_FILES = {
    "128":"/storage2/pres2/GMS/0128tiff",
    "130":"/storage2/pres2/GMS/MS 0130/Masters 0130",
    "275":"/storage2/pres2/GMS/MS 0275/Master 0275",
    "828":"/storage2/pres2/GMS/MS 0828/masters 0828",
    "902":"/data/voldemort/pres3/GMS/MS 0902/Master 0902",
    "948":"/storage2/pres2/GMS/MS 0948/Masters 0948",
    "972":"/storage/goodspeed/images/tiff/ms972/",
    "1054":"/storage2/pres2/GMS/1054"
}

INCOMPLETE_TIF_FILES = {
    "62":  ["/storage2/pres2/GMS/MS 0062/Master 0062"],
    "727": ["/data/voldemort/pres3/GMS/MS 0727 additions/croptifs 0727"],
    "899": ["/data/voldemort/pres3/GMS/MS 0899 4 pages/Master 0899"],
    "937": ["/storage2/pres2/GMS/MS 0937/Master 0937"],
    "939": ["/storage2/pres2/GMS/MS 0939/Master 0939"],
    "943": ["/storage2/pres2/GMS/MS 0943/Master 0943"],
    "947": ["/data/voldemort/pres3/GMS/MS 0947 additions/croptifs 0947",
            "/data/voldemort/pres3/GMS/MS 0947 corrections/croptif 0947"],
    "972": ["/storage/goodspeed/images/tiff/ms972"],
    "1341": ["/storage2/pres2/GMS/MS 1341/Master 1341"],
    "1342": ["/storage2/pres2/GMS/MS 1342/Master 1342"]
}

"fpnrxkp1wj69p_manuscript_files.txt"
"hp4j7g3ph0hc5_manuscript_files.txt"
"w9rdpbt1g8kgf_manuscript_files.txt"


def find_tif_files(path):
    for something in scandir(path):
        if something.is_dir():
            yield from find_tif_files(something.path)
        elif something.is_file():
            if something.path.endswith('.tif') or something.path.endswith("bz2"):
                yield something.path

def main():
    arguments = ArgumentParser()
    arguments.add_argument("audit_file", action='store', type=str)
    parsed_args = arguments.parse_args()
    try:
        print("hi")
        out = {}
        with open(parsed_args.audit_file, "r", encoding="utf-8") as read_file:
            reader = csv.reader(read_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
            count = 0
            for row in reader:
                if count > 0:
                    out[row[0]] = {"identifier": row[0],
                                   "required_numfiles": row[3],
                                   "numfiles":0,
                                   "tei_metadata_file": None,
                                    "marc_metadata_file": None,
                                   "files":[]}
                count += 1

        fpnrxkp1wj69p =  "fpnrxkp1wj69p_manuscript_files.txt"
        hp4j7g3ph0hc5 = "hp4j7g3ph0hc5_manuscript_files.txt"
        w9rdpbt1g8kgf = "goodspeed_tei_mdata_files.txt"

        fpnrxkp1wj69_file = open(fpnrxkp1wj69p,  "r", encoding="utf-8")
        fpnrxkp1wj69_lines = [x.strip().split(',') for x in fpnrxkp1wj69_file.readlines()]

        hp4j7g3ph0hc5_files = open(hp4j7g3ph0hc5, "r", encoding="utf-8")
        hp4j7g3ph0hc5_lines = [x.strip().split(',') for x in hp4j7g3ph0hc5_files.readlines()]

        w9rdpbt1g8kgf_file = open(w9rdpbt1g8kgf, "r", encoding="utf-8")
        w9rdpbt1g8kgf_lines = [x.strip().split(',') for x in w9rdpbt1g8kgf_file.readlines()]


        tifs = []

        for line in fpnrxkp1wj69_lines:
            try:
                path = line[1]
                ms_id = line[0]
                if path != "":
                    path_items = [join(path, x) for x in listdir(path) if x.endswith('.mrc')]
                    if path_items:
                        out[ms_id]['marc_metadata_file'] = path_items[0]
                    if 'tif' in listdir(path):
                        tifs = find_tif_files(join(path, "tif"))
                    else:
                        exception = [x for x in EXCEPTIONS if x[0] == path][0]
                        tifs = find_tif_files(join(path, exception[1]))
                for a_tif in tifs:
                    out[ms_id]['files'].append(a_tif)
            except IndexError:
                print(line)

        for line in hp4j7g3ph0hc5_lines:
            try:
                path = line[1]
                ms_id = line[0]
                if path != "":
                    path_items = [join(path, x) for x in listdir(path) if x.endswith('.mrc')]
                    if path_items:
                        out[ms_id]['marc_metadata_file'] = path_items[0]
                    tifs = []
                    for a_thing in listdir(path):
                        if 'master' in a_thing:
                            tifs = find_tif_files(join(path, a_thing))
                            break
                    tifs = [x for x in tifs]
                    if len(out[line[0]]["files"]) == 0 and len(tifs) > 0:
                        for a_tif in tifs:
                            out[line[0]]["files"].append(a_tif)
            except IndexError:
                print(line)

        for line in w9rdpbt1g8kgf_lines:
            try:
                path = line[1]
                ms_id = line[0]
                if out.get(ms_id) and path != "":
                    out[ms_id]["tei_metadata_file"] = path
            except IndexError:
                print(line)
        dual_metadata_count = 0
        null_metadata_count = 0
        still_missing_tifs_count = 0
        too_many_tifs_count = 0
        total_numfiles = 0
        for key in out:
            print(key)
            try:
                num_files = len(out[key]['files'])
                out[key]['numfiles'] = num_files
                if out[key]['numfiles'] == 0:
                    if MISSING_TIF_FILES.get(key):
                        tif_path = MISSING_TIF_FILES[key]
                        for a_tif in find_tif_files(tif_path):
                            out[key]['files'].append(a_tif)
                        out[key]["numfiles"] = len(out[key]['files'])
                if out[key]['required_numfiles'] == '?':
                    out[key]['required_numfiles'] = 0
                    pass
                else:
                    req  = int(out[key]['required_numfiles'])
                    has = out[key]['numfiles']
                    out[key]['required_numfiles'] = req
                    if req > has:
                        if INCOMPLETE_TIF_FILES.get(key):
                            additions_paths = INCOMPLETE_TIF_FILES[key]
                            total_new_tifs_added = 0
                            for n_path in additions_paths:
                                for n_file in find_tif_files(n_path):
                                    out[key]['files'].append(n_file)
                                    total_new_tifs_added += 1
                            out[key]['numfiles'] += total_new_tifs_added
                        else:
                            print(key  + " is not accounted for")
                copy_files = out[key]['files']
                sorted_files = sorted(copy_files)
                out[key]['files'] = sorted_files
                out[key]['numfiles'] = len(sorted_files)
                if (out[key]['tei_metadata_file'] == None) and (out[key]['marc_metadata_file'] == None):
                    print(key + " has no metadata")
                    null_metadata_count += 1
                elif (out[key]['tei_metadata_file'] != None) and (out[key]['marc_metadata_file'] != None):
                    dual_metadata_count += 1
                if out[key]['required_numfiles'] > out[key]['numfiles']:
                    print(key + " has " + str(len(out[key]['files'])) + " and it should have " + str(out[key]['required_numfiles']))
                    still_missing_tifs_count += 1
                if out[key]['required_numfiles'] < out[key]['numfiles']:
                    too_many_tifs_count += 1
            except TypeError:
                print(key)
            total_numfiles += out[key]['numfiles']
        print("there are " + str(total_numfiles) + " total files in goodspeed")
        print("there are " + str(still_missing_tifs_count) + " with not enough tif  files")
        print("there are " + str(too_many_tifs_count) + " with too many tif  files")
        print("there are " + str(null_metadata_count) + " with no metadata options")
        print("there are " + str(dual_metadata_count) + " with both metadata options")
        with open(join(getcwd(), 'first_goodspeed_grouping_2.json'), 'w+', encoding='utf-8') as write_file:
            json.dump(out, write_file, indent=4)
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(main())

