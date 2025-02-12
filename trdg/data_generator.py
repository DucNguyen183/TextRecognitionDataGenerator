import os
import random as rnd
import cv2
from PIL import Image, ImageFilter
from numpy import asarray
from trdg import computer_text_generator, background_generator, distorsion_generator
import numpy as np


try:
    from trdg import handwritten_text_generator
except ImportError as e:
    print("Missing modules for handwritten text generation.")


def change_brightness(img, value=None):
    if value == None:
        value = rnd.randrange(30, 90, 5)
    img = asarray(img)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    # lim = 255 - value
    # v[v > lim] = 255
    # v[v <= lim] += value
    v = cv2.add(v, value)
    v[v > 255] = 255
    v[v < 0] = 0
    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    img = Image.fromarray(img)
    return img


def add_noise(image):
    img = asarray(image)
    row, col, ch = img.shape
    s_vs_p = 0.4
    amount = 0.01
    out = np.copy(img)
    # Salt mode
    num_salt = np.ceil(amount * img.size * s_vs_p)
    coords = [np.random.randint(0, i - 1, int(num_salt))
              for i in img.shape]
    out[tuple(coords)] = 1

    # Pepper mode
    num_pepper = np.ceil(amount * img.size * (1. - s_vs_p))
    coords = [np.random.randint(0, i - 1, int(num_pepper))
              for i in img.shape]
    out[tuple(coords)] = 0
    image = Image.fromarray(out)
    return image


class FakeTextDataGenerator(object):
    @classmethod
    def generate_from_tuple(cls, t):
        """
            Same as generate, but takes all parameters as one tuple
        """

        cls.generate(*t)

    @classmethod
    def generate(cls,field,index,text,font,out_dir,size,extension,skewing_angle,random_skew,
                 blur,random_blur,background_type,distorsion_type,distorsion_orientation,
                 is_handwritten,name_format,width,alignment,text_color,orientation,space_width,
                 character_spacing,margins,fit,output_mask,word_split,image_dir,stroke_width=0,
                 stroke_fill="#282828",image_mode="RGB",
    ):
        image = None

        margin_top, margin_left, margin_bottom, margin_right = margins
        horizontal_margin = margin_left + margin_right
        vertical_margin = margin_top + margin_bottom

        ##########################
        # Create picture of text #
        ##########################
        if is_handwritten:
            if orientation == 1:
                raise ValueError("Vertical handwritten text is unavailable")
            image, mask = handwritten_text_generator.generate(text, text_color)
        else:
            image, mask = computer_text_generator.generate(text,font,text_color,size,orientation,
                                                           space_width,character_spacing,fit,word_split,
                                                           stroke_width, stroke_fill,)
        random_angle = rnd.randint(0 - skewing_angle, skewing_angle)

        rotated_img = image.rotate(
            skewing_angle if not random_skew else random_angle, expand=1
        )

        rotated_mask = mask.rotate(
            skewing_angle if not random_skew else random_angle, expand=1
        )

        #############################
        # Apply distorsion to image #
        #############################
        if distorsion_type == 0:
            distorted_img = rotated_img  # Mind = blown
            distorted_mask = rotated_mask
        elif distorsion_type == 1:
            distorted_img, distorted_mask = distorsion_generator.sin(
                rotated_img,
                rotated_mask,
                vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2),
            )
        elif distorsion_type == 2:
            distorted_img, distorted_mask = distorsion_generator.cos(
                rotated_img,
                rotated_mask,
                vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2),
            )
        else:
            distorted_img, distorted_mask = distorsion_generator.random(
                rotated_img,
                rotated_mask,
                vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2),
            )

        ##################################
        # Resize image to desired format #
        ##################################

        # Horizontal text
        if orientation == 0:
            new_width = int(
                distorted_img.size[0]
                * (float(size - vertical_margin) / float(distorted_img.size[1]))
            )
            resized_img = distorted_img.resize(
                (new_width, size - vertical_margin), Image.ANTIALIAS
            )
            resized_mask = distorted_mask.resize((new_width, size - vertical_margin), Image.NEAREST)
            background_width = width if width > 0 else new_width + horizontal_margin
            background_height = size
        # Vertical text
        elif orientation == 1:
            new_height = int(
                float(distorted_img.size[1])
                * (float(size - horizontal_margin) / float(distorted_img.size[0]))
            )
            resized_img = distorted_img.resize(
                (size - horizontal_margin, new_height), Image.ANTIALIAS
            )
            resized_mask = distorted_mask.resize(
                (size - horizontal_margin, new_height), Image.NEAREST
            )
            background_width = size
            background_height = new_height + vertical_margin
        else:
            raise ValueError("Invalid orientation")

        #############################
        # Generate background image #
        #############################
        if background_type == 0:
            background_img = background_generator.gaussian_noise(background_height, background_width)
        elif background_type == 1:
            background_img = background_generator.plain_white(background_height, background_width)
        elif background_type == 2:
            background_img = background_generator.quasicrystal(background_height, background_width)
        else:
            background_img = background_generator.image(background_height, background_width, image_dir)
            background_img = change_brightness(background_img, value=rnd.randrange(0,30,5))
        background_mask = Image.new("RGB", (background_width, background_height), (0, 0, 0))

        #############################
        # Place text with alignment #
        #############################
        resized_img = add_noise(resized_img)
        resized_img = resized_img.filter(ImageFilter.BLUR)
        new_text_width, _ = resized_img.size
        issue_loc = [(325, 50), (310, 42), (320, 58), (311, 45)]
        if alignment == 0 or width == -1:
            background_img.paste(resized_img, (margin_left, margin_top), resized_img)
            background_mask.paste(resized_mask, (margin_left, margin_top))
        elif alignment == 1:
            list_img = os.listdir(image_dir)
            l = len(list_img)
            m = rnd.randint(0, l-1)
            img_path = image_dir + "/" + list_img[m]
            init_img = Image.open(img_path)
            bg_width, bg_height = init_img.size
            background_img = background_generator.image(bg_height-10, bg_width-5, image_dir)
            background_img = change_brightness(background_img, value=rnd.randrange(10,30,5))
            background_mask = Image.new("RGB", (bg_width, bg_height), (0, 0, 0))
            k = rnd.randint(0, 3)
            background_img.paste(resized_img,issue_loc[k],resized_img,)
            background_mask.paste(resized_mask,(int(background_width / 2 - new_text_width / 2), margin_top),)
        else:
            background_img.paste(
                resized_img,
                (background_width - new_text_width - margin_right, margin_top),
                resized_img,
            )
            background_mask.paste(
                resized_mask,
                (background_width - new_text_width - margin_right, margin_top),
            )

        #######################
        # Apply gaussian blur #
        #######################

        # gaussian_filter = ImageFilter.GaussianBlur(
        #     radius=blur if not random_blur else rnd.randint(1, blur)
        # )
        # final_image = background_img.filter(gaussian_filter)
        # final_mask = background_mask.filter(gaussian_filter)
        
        ############################################
        # Change image mode (RGB, grayscale, etc.) #
        ############################################
        
        final_image = background_img.convert(image_mode)
        final_mask = background_mask.convert(image_mode)

        #####################################
        # Generate name for resulting image #
        #####################################
        # We remove spaces if space_width == 0
        if space_width == 0:
            text = text.replace(" ", "")
        if name_format == 0:
            image_name = "{}_{:05d}.{}".format(field, index, extension)
            mask_name = "{}_{}_mask.png".format(text, str(index))
        elif name_format == 1:
            image_name = "{}_{:05d}_0.{}".format(field, index, extension)
            mask_name = "{}_{}_mask.png".format(str(index), text)
        elif name_format == 2:
            image_name = "{}_{:05d}_1.{}".format(field, index, extension)
            mask_name = "{}_{}_mask.png".format(str(index), text)
        elif name_format == 3:
            image_name = "{}.{}".format(str(index), extension)
            mask_name = "{}_mask.png".format(str(index))
        else:
            print("{} is not a valid name format. Using default.".format(name_format))
            image_name = "{}_{}.{}".format(text, str(index), extension)
            mask_name = "{}_{}_mask.png".format(text, str(index))

        # Save the image
        if out_dir is not None:
            final_image.save(os.path.join(out_dir, image_name))
            if output_mask == 1:
                final_mask.save(os.path.join(out_dir, mask_name))
        else:
            if output_mask == 1:
                return final_image, final_mask
            return final_image
