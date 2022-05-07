#!/usr/bin/env python

# pylint: disable=missing-module-docstring,missing-function-docstring

import logging
import os

from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont  # type: ignore
from PIL.ImageFont import FreeTypeFont  # type: ignore

logging.basicConfig(level="DEBUG")
logger = logging.getLogger(__name__)

IMAGE_NUMBER = 0
OUTPUT_PATH = "output"


def wrap_text(
    font: FreeTypeFont,
    text: str,
    max_width: int,
) -> str:
    words = text.split()

    lines: list[str] = [""]
    curr_line_width = 0

    for word in words:
        if curr_line_width == 0:
            word_width = font.getlength(word)

            lines[-1] = word
            curr_line_width = word_width
        else:
            new_line_width = font.getlength(f"{lines[-1]} {word}")

            if new_line_width > max_width:
                # Word is too long to fit on the current line
                word_width = font.getlength(word)

                # Put the word on the next line
                lines.append(word)
                curr_line_width = word_width
            else:
                # Put the word on the current line
                lines[-1] = f"{lines[-1]} {word}"
                curr_line_width = new_line_width

    return "\n".join(lines)


def try_fit_text(
    font: FreeTypeFont,
    text: str,
    max_width: int,
    max_height: int,
    line_spacing: int = 4,
) -> Optional[str]:
    words = text.split()

    line_height = font.size

    if line_height > max_height:
        # The line height is already too big
        return None

    lines: list[str] = [""]
    curr_line_width = 0

    for word in words:
        if curr_line_width == 0:
            word_width = font.getlength(word)

            if word_width > max_width:
                # Word is longer than max_width
                return None

            lines[-1] = word
            curr_line_width = word_width
        else:
            new_line_width = font.getlength(f"{lines[-1]} {word}")

            if new_line_width > max_width:
                # Word is too long to fit on the current line
                word_width = font.getlength(word)
                new_num_lines = len(lines) + 1
                new_text_height = (new_num_lines * line_height) + (
                    new_num_lines * line_spacing
                )

                if word_width > max_width or new_text_height > max_height:
                    # Word is longer than max_width, and
                    # adding a new line would make the text too tall
                    return None

                # Put the word on the next line
                lines.append(word)
                curr_line_width = word_width
            else:
                # Put the word on the current line
                lines[-1] = f"{lines[-1]} {word}"
                curr_line_width = new_line_width

    return "\n".join(lines)


def fit_text(
    font: FreeTypeFont,
    text: str,
    max_width: int,
    max_height: int,
    line_spacing: int = 4,
    scale_factor: float = 0.8,
    max_iterations: int = 5,
) -> Tuple[FreeTypeFont, str]:
    """
    Automatically determines text wrapping and appropriate font size.

    :param font:
    :param text:
    :param max_width:
    :param max_height:
    :param scale_factor:
    :param max_iterations:

    :return: The font at the appropriate size and the wrapped text.
    """

    initial_font_size = font.size

    logger.debug('Trying to fit text "%s"', text)

    for i in range(max_iterations):
        trial_font_size = int(initial_font_size * pow(scale_factor, i))
        trial_font = font.font_variant(size=trial_font_size)

        logger.debug("Trying font size %i", trial_font_size)

        wrapped_text = try_fit_text(
            trial_font,
            text,
            max_width,
            max_height,
            line_spacing,
        )

        if wrapped_text:
            logger.debug("Successfully fit text")
            return (trial_font, wrapped_text)

    # Give up and wrap the text at the last size
    logger.debug("Gave up trying to fit text; just wrapping text")
    wrapped_text = wrap_text(trial_font, text, max_width)

    return (trial_font, wrapped_text)


def generate_image(
    image_width: int,
    image_height: int,
    bg_color: str,
    fg_color: str,
    bb_color: str,
    font_name: str,
    font_size: int,
    text: str,
    max_width: int,
    max_height: int,
    line_spacing: int,
    scale_factor: float,
    max_iterations: int,
) -> None:
    # pylint: disable=global-statement
    global IMAGE_NUMBER

    with Image.new(
        mode="RGBA", size=(image_width, image_height), color=bg_color
    ) as image:
        draw = ImageDraw.Draw(image)

        draw.rectangle(
            [
                (image_width - max_width) / 2,
                (image_height - max_height) / 2,
                (image_width + max_width) / 2,
                (image_height + max_height) / 2,
            ],
            fill=None,
            outline=bb_color,
        )

        font = ImageFont.truetype(font_name, font_size)

        (sized_font, wrapped_text) = fit_text(
            font,
            text,
            max_width,
            max_height,
            line_spacing,
            scale_factor,
            max_iterations,
        )

        draw.multiline_text(
            xy=(image_width / 2, image_height / 2),
            text=wrapped_text,
            fill=fg_color,
            font=sized_font,
            anchor="mm",
            spacing=line_spacing,
            align="center",
        )

        output_path = os.path.join(OUTPUT_PATH, f"image-{IMAGE_NUMBER}.png")

        image.save(output_path)

    IMAGE_NUMBER += 1


def main() -> None:
    image_width = 500
    image_height = 500
    bg_color = "white"
    fg_color = "black"
    bb_color = "red"

    font_name = "Montserrat-SemiBold.ttf"
    font_size = 100
    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit"
    max_width = 400
    max_height = 400
    line_spacing = 4
    scale_factor = 0.8
    max_iterations = 5

    text = "Lorem ipsum dolor sit amet, consectetur"

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    max_width = 400
    max_height = 400
    generate_image(
        image_width,
        image_height,
        bg_color,
        fg_color,
        bb_color,
        font_name,
        font_size,
        text,
        max_width,
        max_height,
        line_spacing,
        scale_factor,
        max_iterations,
    )

    max_width = 300
    max_height = 300
    generate_image(
        image_width,
        image_height,
        bg_color,
        fg_color,
        bb_color,
        font_name,
        font_size,
        text,
        max_width,
        max_height,
        line_spacing,
        scale_factor,
        max_iterations,
    )

    max_width = 200
    max_height = 200
    generate_image(
        image_width,
        image_height,
        bg_color,
        fg_color,
        bb_color,
        font_name,
        font_size,
        text,
        max_width,
        max_height,
        line_spacing,
        scale_factor,
        max_iterations,
    )

    max_width = 400
    max_height = 300
    generate_image(
        image_width,
        image_height,
        bg_color,
        fg_color,
        bb_color,
        font_name,
        font_size,
        text,
        max_width,
        max_height,
        line_spacing,
        scale_factor,
        max_iterations,
    )

    max_width = 300
    max_height = 200
    generate_image(
        image_width,
        image_height,
        bg_color,
        fg_color,
        bb_color,
        font_name,
        font_size,
        text,
        max_width,
        max_height,
        line_spacing,
        scale_factor,
        max_iterations,
    )

    max_width = 300
    max_height = 100
    generate_image(
        image_width,
        image_height,
        bg_color,
        fg_color,
        bb_color,
        font_name,
        font_size,
        text,
        max_width,
        max_height,
        line_spacing,
        scale_factor,
        max_iterations,
    )

    max_width = 300
    max_height = 100
    max_iterations = 10
    generate_image(
        image_width,
        image_height,
        bg_color,
        fg_color,
        bb_color,
        font_name,
        font_size,
        text,
        max_width,
        max_height,
        line_spacing,
        scale_factor,
        max_iterations,
    )


if __name__ == "__main__":
    main()
