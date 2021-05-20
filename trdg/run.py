import argparse
import os, errno
import sys
import pandas as pd
import random
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import random as rnd
import string
import sys

from tqdm import tqdm
from trdg.string_generator import (
    create_strings_from_dict,
    create_strings_from_file,
    create_strings_from_wikipedia,
    create_strings_randomly,
)
from trdg.utils import load_dict, load_fonts
from trdg.data_generator import FakeTextDataGenerator
from multiprocessing import Pool


def format_date(list_date):
    out_date = []
    for item in list_date:
        if '-' in item:
            item = item.replace('-','/')
        tmp_date = "            ".join(item.split('/'))
        out_date.append(tmp_date)
    return out_date
def margins(margin):
    margins = margin.split(",")
    if len(margins) == 1:
        return [int(margins[0])] * 4
    return [int(m) for m in margins]


def init_args(id_type, field, row_count):
    args_dict = {}
    args_dict["output_dir"] = "out/{}/{}/".format(id_type, field)
    args_dict["language"] = "en"
    args_dict["count"] = row_count
    args_dict["random_sequences"] = False
    args_dict["include_letters"] = False
    args_dict["include_numbers"] = False
    args_dict["include_symbols"] = False
    args_dict["length"] = 1
    args_dict["random"] = False
    args_dict["thread_count"] = 1
    args_dict["extension"] = "jpg"
    args_dict["skew_angle"] = 0
    args_dict["random_skew"] = False
    args_dict["use_wikipedia"] = False
    args_dict["background"] = 3
    args_dict["handwritten"] = False
    args_dict["output_mask"] = 0
    args_dict["distorsion"] = 0
    args_dict["distorsion_orientation"] = 0
    args_dict["width"] = -1
    args_dict["alignment"] = 0
    args_dict["orientation"] = 0
    args_dict["space_width"] = 1.0
    args_dict["character_spacing"] = 0
    args_dict["margins"] = (5, 5, 5, 5)
    args_dict["fit"] = False
    args_dict["font_dir"] = "fonts/my_font/"
    args_dict["dict"] = ""
    args_dict["word_split"] = False
    args_dict["image_mode"] = "RGB"
    args_dict["name_format"] = 0
    args_dict["stroke_fill"] = "#383838"
    args_dict["text_color"] = "#303030"
    args_dict["case"] = ''
    args_dict["image_dir"] = os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                          "images/{}/{}".format(id_type, field))
    if id_type == 'cccd':
        if field == "name":
            args_dict["stroke_width"] = 1
            args_dict["format"] = 50
            args_dict["blur"] = 2
            args_dict["random_blur"] = True
            args_dict["font"] = "arialbd.ttf"
            args_dict["case"] = 'upper'
        else:
            args_dict["stroke_width"] = 0
            if field in ["address", "hometown"]:
                args_dict["name_format"] = 1
            args_dict["format"] = 40
            args_dict["blur"] = 1
            args_dict["random_blur"] = True
            args_dict["font"] = "arial.ttf"
            if field == 'id_number':
                args_dict['font'] = 'OCR B Std Regular.otf'
            args_dict["case"] = ''
            if field == 'issue_date':
                args_dict["font"] = "arialbi.ttf"
                args_dict["format"] = 98
                args_dict["alignment"] = 1
                args_dict["width"] = 1470
                args_dict["stroke_fill"] = "#0f0f0f"
                args_dict["text_color"] = "#292c2b"
    else:
        args_dict["stroke_width"] = 0
        if field in ["address", "hometown"]:
            args_dict["name_format"] = 1
        args_dict["format"] = 93
        args_dict["blur"] = 1
        args_dict["random_blur"] = False
        args_dict["font"] = 'palatino-linotype.ttf'
        args_dict["stroke_fill"] = "#000618"
        args_dict["text_color"] = "#000618"
    return args_dict


def gen_text(args_dict, field, strings, fonts, index):
    string_count = len(strings)
    p = Pool(args_dict["thread_count"])
    for _ in tqdm(
            p.imap_unordered(
                FakeTextDataGenerator.generate_from_tuple,
                zip([field] * string_count,
                    [i for i in index],
                    strings,
                    [fonts[rnd.randrange(0, len(fonts))] for _ in range(0, string_count)],
                    [args_dict["output_dir"]] * string_count,
                    [args_dict["format"]] * string_count,
                    [args_dict["extension"]] * string_count,
                    [args_dict["skew_angle"]] * string_count,
                    [args_dict["random_skew"]] * string_count,
                    [args_dict["blur"]] * string_count,
                    [args_dict["random_blur"]] * string_count,
                    [args_dict["background"]] * string_count,
                    [args_dict["distorsion"]] * string_count,
                    [args_dict["distorsion_orientation"]] * string_count,
                    [args_dict["handwritten"]] * string_count,
                    [args_dict["name_format"]] * string_count,
                    [args_dict["width"]] * string_count,
                    [args_dict["alignment"]] * string_count,
                    [args_dict["text_color"]] * string_count,
                    [args_dict["orientation"]] * string_count,
                    [args_dict["space_width"]] * string_count,
                    [args_dict["character_spacing"]] * string_count,
                    [args_dict["margins"]] * string_count,
                    [args_dict["fit"]] * string_count,
                    [args_dict["output_mask"]] * string_count,
                    [args_dict["word_split"]] * string_count,
                    [args_dict["image_dir"]] * string_count,
                    [args_dict["stroke_width"]] * string_count,
                    [args_dict["stroke_fill"]] * string_count,
                    [args_dict["image_mode"]] * string_count,
                ),
            ),
            total=args_dict["count"],
    ):
        pass
    p.terminate()

    # if args_dict["name_format"] == 2:
    #     # Create file with filename-to-label connections
    #     with open(
    #             os.path.join(args_dict["output_dir"], "labels.txt"), "w", encoding="utf8"
    #     ) as f:
    #         for i in range(string_count):
    #             file_name = str(i) + "." + args_dict["extension"]
    #             if args_dict["space_width"] == 0:
    #                 file_name = file_name.replace(" ", "")
    #             f.write("{} {}\n".format(file_name, strings[i]))


def read_data(file_path, field):
    df = pd.read_csv(file_path, sep='\t', header=None, dtype={1:str})
    info = df[df[0] == field][1].values
    return info


def remake_location(locations, num):
    location1 = []
    location2 = []
    counter = []
    if not os.path.exists('label/'): os.makedirs('label/')
    for i, loc in enumerate(locations[:num]):
        temp_loc = loc.split(",")
        if len(loc) <= 25 or len(temp_loc) < 2:
            location1.append(loc)
            with open('label/cmt09_address_annotation.txt', 'a') as f:
                f.write("cmt09/address_{:05d}_0.jpg\t{}\n".format(i, loc))
        else:
            k = random.randint(1, len(temp_loc)-1)
            loc1 = ",".join(s for s in temp_loc[:k]).strip()
            if len(loc1) < 4:
                loc1 = ",".join(s for s in temp_loc[:(k+1)]).strip()
                loc2 = ','.join(s for s in temp_loc[(k+1):]).strip()
            else:
                loc2 = ','.join(s for s in temp_loc[k:]).strip()
            location1.append(loc1)
            location2.append(loc2)
            counter.append(i)
            with open('label/cmt09_address_annotation.txt', 'a') as f:
                f.write("cmt09/address_{:05d}_0.jpg\t{}\n".format(i, loc1))
                f.write("cmt09/address_{:05d}_1.jpg\t{}\n".format(i, loc2))
    return location1, location2, counter


def run(id_type, text_data_path):
    """
        Description: Main function
    """
    if id_type == 'cccd':
        list_field = ["name", "id_number", "dob", "address", "hometown", "issue_date"]
    else:
        list_field = ['address']
    for field in list_field:
        try:
            print("Generate images for field: {}...".format(field))
            info = read_data(text_data_path, field)
            # Argument init
            args_dict = init_args(id_type, field, len(info))

            # Create the directory if it does not exist.
            try:
                os.makedirs(args_dict["output_dir"])
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

            # Creating word list
            if args_dict["dict"]:
                lang_dict = []
                if os.path.isfile(args_dict["dict"]):
                    with open(args_dict["dict"], "r", encoding="utf8", errors="ignore") as d:
                        lang_dict = [l for l in d.read().splitlines() if len(l) > 0]
                else:
                    sys.exit("Cannot open dict")
            else:
                lang_dict = load_dict(args_dict["language"])

            # Create font (path) list
            fonts = [os.path.join(args_dict["font_dir"], args_dict["font"])]

            # Creating synthetic sentences (or word)
            strings = []
            string1 = []
            counter = []

            if args_dict["use_wikipedia"]:
                strings = create_strings_from_wikipedia(args_dict["length"], args_dict["count"], args_dict["language"])
                # strings = create_strings_from_file(args_dict["input_file"], args_dict["count"])
            elif args_dict["random_sequences"]:
                strings = create_strings_randomly(
                    args_dict["length"],
                    args_dict["random"],
                    args_dict["count"],
                    args_dict["include_letters"],
                    args_dict["include_numbers"],
                    args_dict["include_symbols"],
                    args_dict["language"],
                )
                # Set a name format compatible with special characters automatically if they are used
                if args_dict["include_symbols"] or True not in (
                    args_dict["include_letters"],
                    args_dict["include_numbers"],
                    args_dict["include_symbols"],
                ):
                    args_dict["name_format"] = 2
            else:
                strings = create_strings_from_dict(
                    args_dict["length"], args_dict["random"], args_dict["count"], lang_dict
                )

            if field in ["name", "id_number", "dob"]:
                strings = info
            elif field == 'issue_date':
                strings = format_date(info)
            else:
                strings, string1, counter = remake_location(info, 5000)
            if args_dict["language"] == "ar":
                from arabic_reshaper import ArabicReshaper

                arabic_reshaper = ArabicReshaper()
                strings = [
                    " ".join([arabic_reshaper.reshape(w) for w in s.split(" ")[::-1]])
                    for s in strings
                ]
            if args_dict["case"] == "upper":
                strings = [x.upper() for x in strings]
            if args_dict["case"] == "lower":
                strings = [x.lower() for x in strings]

            string_count = len(strings)
            if field in ["name", "dob", "issue_date"]:
                gen_text(args_dict, field, strings, fonts, range(0, len(strings)))
            elif field == 'id_number':
                args_dict['format'] = 50
                args_dict["stroke_fill"] = "#d35b4e"
                args_dict["text_color"] = "#d35b4e"
                # strings = [s.replace("", " ")[:-1] for s in strings]
                gen_text(args_dict, field, strings, fonts, range(0, len(strings)))
            else:
                if id_type == 'cmt':
                    list_fonts = ['palatino-linotype.ttf', 'Trixi Pro Regular.ttf']
                    fonts = [os.path.join(args_dict["font_dir"], cmt_font) for cmt_font in list_fonts]
                args_dict["name_format"] = 1
                gen_text(args_dict, field, strings, fonts, range(0, len(strings)))
                args_dict["name_format"] = 2
                gen_text(args_dict, field, string1, fonts, counter)
            # if args_dict["name_format"] == 3:
            #     # Create file with filename-to-label connections
            #     with open(
            #         os.path.join(args_dict["output_dir"], "labels.txt"), "w", encoding="utf8"
            #     ) as f:
            #         for i in range(string_count):
            #             file_name = str(i) + "." + args_dict["extension"]
            #             if args_dict["space_width"] == 0:
            #                 file_name = file_name.replace(" ", "")
            #             f.write("{} {}\n".format(file_name, strings[i]))
        except Exception as e:
            print(e)


if __name__ == "__main__":
    run('cmt', 'texts/cccd_labels.csv')
