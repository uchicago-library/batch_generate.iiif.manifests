
from argparse import ArgumentParser
import csv
from os import _exit
from os.path import join, exists
import requests
from sys import stderr, stdout
from xml.etree.ElementTree import Element, SubElement, ElementTree

def main():
    arguments = ArgumentParser(description="a tool to build DC files for  new issues added to campub site")
    arguments.add_argument("csv_file", type=str, action='store')
    arguments.add_argument("mvol_root_dir", type=str, action='store')
    parsed_args = arguments.parse_args()
    try:
        data = []
        with open(parsed_args.csv_file, "r", encoding="utf-8") as rf:
            reader = csv.reader(rf, delimiter=',', quoting=csv.QUOTE_ALL, quotechar='"')
            for record in reader:
                data.append(record)
            count = 0
            for n in data[1:]:
                count += 1
                title = n[0]
                date = n[1]
                identifier = n[2]
                description = n[3]
                root = Element("dublin_core")
                title_el = SubElement(root, 'title')
                title_el.text = title
                date_el = SubElement(root, 'date')
                date_el.text = date
                identifier_el = SubElement(root, 'identifier')
                identifier_el.text = identifier
                description_el = SubElement(root, 'description')
                description_el.text = description
                tree = ElementTree(root)
                xml_filepath = '/'.join(identifier.split('-'))
                xml_filepath = join(parsed_args.mvol_root_dir, xml_filepath)
                if exists(xml_filepath):
                    xml_file = join(xml_filepath, identifier + ".dc.xml")
                    if not exists(xml_file):
                        tree.write(xml_file, encoding="utf-8", xml_declaration=True)
                    ocr_url = 'https://digcollretriever.lib.uchicago.edu/projects/' + identifier + '/ocr'
                    ocr_url += "?jpg_width=1000&jpg_height=1000&min_year=1900&max_year=2018"
                    if requests.get(ocr_url, 'HEAD').status_code == 200:
                        pass
                    else:
                        stderr.write("{} couldn't be fetched\n".format(ocr_url))
                else:
                    stderr.write("{} does not exist on disk\n".format(xml_filepath))
            stdout.write("successfully created dublin core records for {} issues.\n".format(count))
        return 0
    except KeyboardInterrupt:
        return 131


if __name__ == "__main__":
    _exit(main())
