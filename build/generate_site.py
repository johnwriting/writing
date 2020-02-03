#! /usr/bin/env python
import os
import subprocess
from html.parser import HTMLParser
import jinja2

CONTENT_PATH = '../content'
INTERMEDIATE_HTML_PATH = 'generated/'
PIECE_TEMPLATE_PATH = '../site/templates/piece.html.template'
DESTINATION_HTML_PATH = '../site/html/content'

# create a subclass and override the handler methods


class MyHTMLParser(HTMLParser):
    start_position = (0, 0)
    end_position = (0, 0)

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.start_position = (self.getpos()[0], self.getpos()[1]+6)

    def handle_endtag(self, tag):
        if tag == "body":
            self.end_position = (self.getpos()[0], self.getpos()[1])

    def handle_data(self, data):
        pass


class Piece():
    def __init__(self, title, body):
        self.title = title
        self.body = body


def _extract_file_selection(file, start_position, end_position):
    output = ""
    with open(file) as f:
        text = f.readlines()

    # This is so extremely stupid I am ashamed
    for line_index, line in enumerate(text):
        line_index_one_indexed = line_index + 1
        if line_index_one_indexed == start_position[0]:
            output += line[start_position[1]:]
        elif line_index_one_indexed == end_position[0]:
            output += line[:end_position[1]]
        elif line_index_one_indexed > start_position[0] and line_index_one_indexed < end_position[0]:
            output += line
    return output


def _generate_intermediate_html(input_markdown, output_html):
    subprocess.run(["md-to-html", "--input", input_markdown,
                    "--output", output_html], check=True)


def _generate_destination_html_from_template(intermediate_html, destination_html):
    # instantiate the parser and fed it some HTML
    parser = MyHTMLParser()
    html_string = open(intermediate_html).read()
    parser.feed(html_string)
    print("Grabbing the text between {} and {}".format(
        parser.start_position, parser.end_position))
    extracted_body = _extract_file_selection(
        intermediate_html, parser.start_position, parser.end_position).strip()
    print("Extracted body: \n{}".format(extracted_body))

    piece = Piece("Test Title", extracted_body)
    template = open(PIECE_TEMPLATE_PATH).read()
    rendered_html = jinja2.Template(template).render(piece=piece)

    with open(os.path.join(destination_html), "w") as f:
        f.write(rendered_html)


if __name__ == "__main__":
    output_files = []

    for r, d, f in os.walk(CONTENT_PATH):
        for markdown_filename in f:
            if '.md' in markdown_filename:
                input_markdown = os.path.join(r, markdown_filename)
                input_markdown_no_extension = markdown_filename[:markdown_filename.find(
                    '.md')]
                intermediate_output_html = os.path.join(
                    INTERMEDIATE_HTML_PATH, "{}.html".format(input_markdown_no_extension))
                destination_html = os.path.join(
                    DESTINATION_HTML_PATH, "{}.html".format(input_markdown_no_extension))

                _generate_intermediate_html(
                    input_markdown, intermediate_output_html)
                _generate_destination_html_from_template(
                    intermediate_output_html, destination_html)
