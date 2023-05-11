import socket
from contextlib import closing
import threading, webbrowser, time
import mistune
import bleach
import html
import re
from mistune.renderers import HTMLRenderer

# * Set up the port
def find_free_port():
    """ Find a free port on localhost. """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
    
def auto_opentab_delay(port):
    """ Open a new tab in the browser after a delay. """
    def open(): time.sleep(2)
    webbrowser.open_new_tab(f'http://localhost:{port}')
    t = threading.Thread(target=open)
    t.daemon = True; t.start()

def hide_middle_chars(s):
    if len(s) <= 8:
        return s
    else:
        head = s[:4]
        tail = s[-4:]
        hidden = "*" * (len(s) - 8)
        return head + hidden + tail




class CustomRenderer(HTMLRenderer):
    def render_block_code(self, text, lang=None):
        if not lang:
            return '<pre><code style="white-space: pre-wrap;">%s</code></pre>\n' % mistune.escape(text)
        return '<pre><code class="lang-%s" style="white-space: pre-wrap;">%s</code></pre>\n' % (lang, mistune.escape(text))


def remove_code_blocks(text):
    # Remove inline code
    inline_code_pattern = r'`[^`]+`'
    text = re.sub(inline_code_pattern, '', text)

    # Remove code blocks
    code_block_pattern = r'```[\s\S]*?```'
    text = re.sub(code_block_pattern, '', text)

    # Remove leading spaces to avoid treating them as code blocks
    text = '\n'.join([line.lstrip() for line in text.split('\n')])
    
    return text


def generate_side_by_side_html(chunk_summaries):
    """ Generate the side-by-side HTML for the summary and the source document."""

    renderer = CustomRenderer()
    markdown = mistune.create_markdown(renderer=renderer)

    side_by_side_html = "<table style='width: 100%; border-collapse: collapse;'>"
    for element in chunk_summaries:
        chunk_content = element["chunk_content"]
        summary = element["chunk_summary"]

        chunk_content = remove_code_blocks(chunk_content)
        summary = remove_code_blocks(summary)

        chunk_content_html = markdown(chunk_content)
        summary_html = markdown(summary)

        side_by_side_html += "<tr>"
        side_by_side_html += f"<td style='width: 50%; padding: 10px; border: 1px solid #ccc; word-wrap: break-word;'>{chunk_content_html}</td>"
        side_by_side_html += f"<td style='width: 50%; padding: 10px; border: 1px solid #ccc; word-wrap: break-word;'>{summary_html}</td>"
        side_by_side_html += "</tr>"
    side_by_side_html += "</table>"

    return side_by_side_html

