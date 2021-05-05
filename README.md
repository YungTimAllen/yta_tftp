[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Docstrings: Google](https://img.shields.io/badge/Docstrings-Google-green)](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings)
[![Discord](https://img.shields.io/discord/245189311681527808.svg?label=Networking&logo=discord)](https://discord.me/networking)

# yta_tftp - A Python3 TFTP Server

This is a POC solution from my exploring struct.un/pack and sockets. I've tried to keep it simple, and everything is 
reasonably documented.

* Is a Package you can import and run (See main.py for an example)
* Only uses native python packages (Doesn't use Scapy)
* Serves files from the working directory only
* Is threaded using ephemeral source ports for reply sockets (Can handle loads of transfers at once)
* Has been tested for multiple concurrent transfers exceeding 1GB in size

## Gotchas

* Only supports RRQ (Read Requests) from calling clients
* If the expected file to serve is missing, it will break
* Do not use this to host anything serious - you do so at your own risk

## Example

### Client

```
yta@box $ tftp
tftp> get 127.0.0.1:file.txt
Received 2809 bytes in 0.0 seconds
tftp>
```

### Server

```
Received  TFTPOpcodes.RRQ
Serve 127.0.0.1:62590:file.txt -> 49152
Done! 127.0.0.1:62590:file.txt -> 49152
```
