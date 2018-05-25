
from os import _exit, scandir, getcwd
import json
from os.path import join
from argparse import ArgumentParser
import requests
import re
from sys import stdout, stderr
import urllib

def find_issues(path):
    for a_thing in scandir(path):
        if a_thing.is_dir():
            matchable = re.compile(r"mvol[/]\d{4}[/]\d{4}[/]\d{4}$").search(a_thing.path)
            if matchable:
                yield a_thing.path
            yield from find_issues(a_thing.path)
        else:
            pass

def main():
    arguments = ArgumentParser()
    arguments.add_argument("path_to_issues", type=str, action='store')
    arguments.add_argument("width", type=str, action='store')
    arguments.add_argument("height", type=str, action='store')
    arguments.add_argument("min_year", type=str, action='store')
    arguments.add_argument("max_year", type=str, action='store')
    arguments.add_argument("output_file", type=str, action='store')
    parsed_args = arguments.parse_args()
    try:
        found_issues = find_issues(parsed_args.path_to_issues)
        found_issues = sorted([x for x in found_issues])
        whole_list = []
        for n in found_issues:
            identifier = n.split("mvol")[1]
            identifier = identifier.split("/")
            identifier[0] = "mvol"
            identifier_dir = '/'.join(identifier)
            identifier = '-'.join(identifier)
            ocr_url = "https://digcollretriever.lib.uchicago.edu/projects/{}/ocr?jpg_width={}&jpg_height={}&min_year={}&max_year={}".format(identifier, parsed_args.width, parsed_args.height, parsed_args.min_year, parsed_args.max_year)
            ocr_status = requests.get(ocr_url, "HEAD").status_code
            if ocr_status == 200:
                ocr_info = {"url": ocr_url, "status":ocr_status}
                output = {}
                output["identifier"] = identifier
                output["ocr"] =  ocr_info
                output["pages"] = []
                pages = [x.path for x in scandir(join(n, "TIFF"))]
                pages = sorted(pages)
                count = 1
                for o in pages:
                    jpeg_id = join('/', identifier_dir, o.split(n)[1][1:])[1:]
                    quoted_jpeg_id = urllib.parse.quote(jpeg_id, safe='')

                    jpeg_info_url = "https://iiif-server.lib.uchicago.edu/" + quoted_jpeg_id + "/info.json"
                    jpeg_url = "https://iiif-server.lib.uchicago.edu/" + jpeg_id + "/full/" + parsed_args.width + "," + parsed_args.height + "/0/default.jpg"

                    jpg_url_status = requests.get(jpeg_url, "HEAD").status_code
                    jpg_info_url_status = requests.get(jpeg_info_url, "HEAD").status_code

                    jpeg_url_info = {"image":{"url":None, "status":None}, "info":{"url":None, "status":None}, "page_number": count}
                    jpeg_url_info["image"] = {"url": jpeg_url, "status": jpg_url_status}
                    jpeg_url_info["info"] = {"url": jpeg_info_url, "status": jpg_info_url_status}

                    output["pages"].append(jpeg_url_info)

                    count += 1
                stdout.write("{} has OCR and {} pages\n".format(identifier, str(count)))
                whole_list.append(output)
            else:
                stderr.write("{} could not have OCR generated\n".format(identifier))

            with open(join(getcwd(), parsed_args.output_file + ".json"), "w+") as wf:
                json.dump(whole_list, wf, indent=4)
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(main())
