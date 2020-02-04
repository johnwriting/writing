#! /usr/bin/env python
import cgi
import os
import subprocess
from html.parser import HTMLParser
import jinja2
import markdown


CONTENT_PATH = '../content'
PIECE_TEMPLATE_PATH = '../site/templates/piece.html.template'
INDEX_TEMPLATE_PATH = '../site/templates/index.html.template'
DESTINATION_HTML_PATH = '../docs'

# create a subclass and override the handler methods


class MyHTMLParser(HTMLParser):
    start_position = (0, 0)
    end_position = (0, 0)
    getting_title = False
    title = ""

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.start_position = (self.getpos()[0], self.getpos()[1]+6)
            return
        if tag == "h1":
            self.getting_title = True

    def handle_endtag(self, tag):
        if tag == "body":
            self.end_position = (self.getpos()[0], self.getpos()[1])

    def handle_data(self, data):
        if self.getting_title:
            self.title = data
            self.getting_title = False


class Piece():
    def __init__(self, title, body, html_path):
        self.title = title
        self.body = body
        self.html_path = html_path


def _extract_text_selection(text, start_position, end_position):
    output = ""

    # This is so extremely stupid I am ashamed
    for line_index, line in enumerate(text.split('\n')):
        line_index_one_indexed = line_index + 1
        if line_index_one_indexed == start_position[0]:
            output += line[start_position[1]:]
        elif line_index_one_indexed == end_position[0]:
            output += line[:end_position[1]]
        elif line_index_one_indexed > start_position[0] and line_index_one_indexed < end_position[0]:
            output += line
    return output


def _generate_intermediate_html(input_markdown):
    input_markdown_string = open(input_markdown, encoding="utf8").read()
    return markdown.markdown(input_markdown_string, output_format="html5")


def _extract_piece(intermediate_html, filename):
    parser = MyHTMLParser()
    parser.feed(intermediate_html)
    return Piece(parser.title, intermediate_html, filename)


def _generate_destination_html_from_template(piece, pieces, destination_html):
    template = open(PIECE_TEMPLATE_PATH).read()
    rendered_html = jinja2.Template(
        template).render(piece=piece, pieces=pieces)

    with open(os.path.join(destination_html), "w", encoding="utf8") as f:
        f.write(rendered_html)


def _generate_homepage_from_template(pieces, destination_html):
    template = open(INDEX_TEMPLATE_PATH).read()
    rendered_html = jinja2.Template(template).render(pieces=pieces)

    with open(os.path.join(destination_html), "w", encoding="utf8") as f:
        f.write(rendered_html)


if __name__ == "__main__":
    pieces = []

    for r, d, f in os.walk(CONTENT_PATH):
        for markdown_filename in f:
            if '.md' in markdown_filename:
                input_markdown = os.path.join(r, markdown_filename)
                input_markdown_no_extension = markdown_filename[:markdown_filename.find(
                    '.md')]
                piece_html_filename = "{}.html".format(
                    input_markdown_no_extension)

                intermediate_output_html = _generate_intermediate_html(
                    input_markdown)

                print("Generated html: {}".format(intermediate_output_html))
                piece = _extract_piece(
                    intermediate_output_html, piece_html_filename)
                pieces.append(piece)

    for piece in pieces:
        destination_html = os.path.join(
            DESTINATION_HTML_PATH, piece.html_path)

        _generate_destination_html_from_template(
            piece, pieces, destination_html)

    _generate_homepage_from_template(
        pieces, os.path.join(DESTINATION_HTML_PATH, "index.html"))
