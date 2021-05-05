[![Code style: black](https://img.shields.io/badge/Code%20Style-black-000000.svg)](https://github.com/ambv/black)
[![Docstrings: Google](https://img.shields.io/badge/Docstrings-Google-green)](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings)
[![Discord](https://img.shields.io/discord/245189311681527808.svg?label=Networking&logo=discord)](https://discord.me/networking)
[![PyLint](https://img.shields.io/badge/Linting-PyLint-orange.svg)](https://github.com/PyCQA/pylint)

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

## Example 1

Download of a text file.

### Client

```
yta@box $ tftp
tftp> get 127.0.0.1:file.txt
Received 2809 bytes in 0.0 seconds
tftp>
```

### Server

```
Received OpCode: RRQ
Serve 127.0.0.1:55176:file.txt -> 49152
Done! 127.0.0.1:55176:file.txt -> 49152
```

## Example 2

Download of a large video file, with concurrent requests for other files.

### Client 1

```
tftp> get 127.0.0.1:mac.mp4
Received 1173828708 bytes in 112.2 seconds
```

### Client 2

```
tftp> get 127.0.0.1:tongue.webm
Received 1531958 bytes in 0.2 seconds
tftp> get 127.0.0.1:file.txt
Received 2809 bytes in 0.0 seconds
```

### Server

```
Received OpCode: RRQ
Serve 127.0.0.1:65059:mac.mp4 -> 49154
   Tx mac.mp4 32.0mb	-> 49154
   Tx mac.mp4 64.0mb	-> 49154
   Tx mac.mp4 96.0mb	-> 49154
   Tx mac.mp4 128.0mb	-> 49154
   Tx mac.mp4 160.0mb	-> 49154
   Tx mac.mp4 192.0mb	-> 49154
Received OpCode: RRQ
Serve 127.0.0.1:58964:tongue.webm -> 49155
Done! 127.0.0.1:58964:tongue.webm -> 49155
   Tx mac.mp4 224.0mb	-> 49154
   Tx mac.mp4 256.0mb	-> 49154
   Tx mac.mp4 288.0mb	-> 49154
   Tx mac.mp4 320.0mb	-> 49154
Received OpCode: RRQ
Serve 127.0.0.1:58966:file.txt -> 49156
Done! 127.0.0.1:58966:file.txt -> 49156
   Tx mac.mp4 352.0mb	-> 49154
   Tx mac.mp4 384.0mb	-> 49154
   Tx mac.mp4 416.0mb	-> 49154
   Tx mac.mp4 448.0mb	-> 49154
   Tx mac.mp4 480.0mb	-> 49154
   Tx mac.mp4 512.0mb	-> 49154
   Tx mac.mp4 544.0mb	-> 49154
   Tx mac.mp4 576.0mb	-> 49154
   Tx mac.mp4 608.0mb	-> 49154
   Tx mac.mp4 640.0mb	-> 49154
   Tx mac.mp4 672.0mb	-> 49154
   Tx mac.mp4 704.0mb	-> 49154
   Tx mac.mp4 736.0mb	-> 49154
   Tx mac.mp4 768.0mb	-> 49154
   Tx mac.mp4 800.0mb	-> 49154
   Tx mac.mp4 832.0mb	-> 49154
   Tx mac.mp4 864.0mb	-> 49154
   Tx mac.mp4 896.0mb	-> 49154
   Tx mac.mp4 928.0mb	-> 49154
   Tx mac.mp4 960.0mb	-> 49154
   Tx mac.mp4 992.0mb	-> 49154
   Tx mac.mp4 1024.0mb	-> 49154
   Tx mac.mp4 1056.0mb	-> 49154
   Tx mac.mp4 1088.0mb	-> 49154
Done! 127.0.0.1:65059:mac.mp4 -> 49154
```