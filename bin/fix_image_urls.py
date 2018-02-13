from argparse import ArgumentParser
from os import _exit, scandir
from urllib.parse import quote
import json

def find_manifest_files(path):
    for a_file in scandir(path):
        if a_file.is_dir():
            yield from find_manifest_files(a_file.path)
        elif a_file.is_file() and a_file.path.endswith(".json"):
            yield a_file.path

def main():
    args = ArgumentParser()
    args.add_argument("manifest_directory", type=str, action='store')
    parsed = args.parse_args()
    try:
        generator = find_manifest_files(parsed.manifest_directory)
        for n_thing in generator:
            data = None
            with open(n_thing) as rf:
                data = json.load(rf)
            copy = data
            keys = [x for x in data]
            if 'sequences' not in keys:
                print(n_thing)
            else:
                for seq in data["sequences"]:
                    for canvas in seq["canvases"]:
                        for img in canvas["images"]:
                            try:
                                full_url = img["resource"]["@id"]
                                the_id_part = full_url.split("http://iiif-server.lib.uchicago.edu/")[1].split("/full/full/0/default.jpg")[0]
                                the_id_part = quote(the_id_part, safe="")
                                final_url = "http://iiif-server.lib.uchicago.edu/" + the_id_part + "/full/full/0/default.jpg"
                                print(final_url)
                            except KeyError:
                                print(n_thing)
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(main())
