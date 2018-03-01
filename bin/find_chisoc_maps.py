from argparse import ArgumentParser
from os import _exit, scandir, getcwd
from os.path import basename, join
import json
from pymarc import MARCReader
from sys import stderr, stdout

def find_matching_file(path, pattern_to_match):
    for n in scandir(path):
        if n.is_dir():
            yield from find_matching_file(n.path, pattern_to_match)
        elif n.is_file():
            if n.path.endswith(pattern_to_match + '.tif'):
                yield n.path

def _main():
    arguments = ArgumentParser()
    arguments.add_argument("path_to_chos", type=str, action='store')

    parsed_args = arguments.parse_args()
    try:
        data = None
        master_list = []
        with open(parsed_args.path_to_chos, "r") as rf:
            data = json.load(rf)
        for n in data:
            if n["series_id"]  == "chisoc":
                if len(n["found_files"]) < 1:
                    print(n["identifier"])
                else:
                    master_list.append(n)
        with open(join(getcwd(), "master_chisoc_list.json"), "w+") as wf:
            json.dump(master_list, wf, indent=4)

        """
        chos = scandir(parsed_args.path_to_chos)
        chos = [x.path for x in chos]
        count = 0
        out = []
        for a_cho in chos:
            metadata = scandir(join(a_cho, "metadata"))
            cho_mdata = [x.path for x in metadata]
            a_result = {}
            a_result["identifier"] = (a_cho.split("Maps_CHOs/")[1])
            series_id = None
            for cho_metadata_file in cho_mdata:
                with open(cho_metadata_file, "rb") as read_file:
                    reader = MARCReader(read_file)
                    for record in reader:
                        files = [x.value() for x in record.get_fields('856')]
                        file_ids = [x.split('/')[-1] for x in files]
                        series_id = [x.split('/')[-2] for x in files]
                        try:
                            series_id = series_id[0]
                        except IndexError:
                            pass
                        a_result["file_identifiers"] = file_ids
                        out.append(a_result)
            a_result["series_id"] = series_id
            out.append(a_result)
        copy_out = out
        for n in out:
            ident = n["identifier"]
            print(ident)
            all_found_files = []
            files = n["file_identifiers"]
            for n_thing in files:
                matches = [x for x in find_matching_file("/data/voldemort/digital_collections/data/ldr_oc_admin/files/DC_Work_in_progress/Maps", n_thing)]
                if matches:
                    all_found_files += matches
            copy_out[copy_out.index(n)]["found_files"] = all_found_files
        with open(join(getcwd(), "maps_file_id_info_from_marc.txt"), "w+") as wf:
            json.dump(copy_out, wf, indent=4)
        """
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(_main())
