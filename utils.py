import socket
from contextlib import closing
import threading, webbrowser, time
import mistune

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


def generate_side_by_side_html(chunk_summaries):
    """ Generate the side-by-side HTML for the summary and the source document."""
    markdown = mistune.create_markdown()

    side_by_side_html = "<table style='width: 100%; border-collapse: collapse;'>"
    for element in chunk_summaries:
        chunk_content = element["chunk_content"]
        summary = element["chunk_summary"]

        html = "<p>" + chunk_content.replace("\n\n", "</p><p>").replace("\n", "<br>") + "</p>"
        summary_html = markdown(summary)

        side_by_side_html += "<tr>"
        side_by_side_html += f"<td style='width: 50%; padding: 10px; border: 1px solid #ccc;'>{html}</td>"
        side_by_side_html += f"<td style='width: 50%; padding: 10px; border: 1px solid #ccc;'>{summary_html}</td>"
        side_by_side_html += "</tr>"
    side_by_side_html += "</table>"

    return side_by_side_html

def generate_side_by_side_markdown(chunk_summaries):
    """ Generate the side-by-side markdown for the summary and the source document."""
    
    side_by_side_markdown = "| Source Document | Summary |\n"
    side_by_side_markdown += "| --- | --- |\n"

    for element in chunk_summaries:
        chunk_content = element["chunk_content"]
        summary = element["chunk_summary"]

        markdown_chunk_content = "<p>" + chunk_content.replace("\n\n", "</p><p>").replace("\n", "<br>") + "</p>"
        markdown_summary = summary.replace("\n\n", "\n\n\n").replace("\n", "  \n")

        side_by_side_markdown += f"| {markdown_chunk_content} | {markdown_summary} |\n"

    
    return side_by_side_markdown