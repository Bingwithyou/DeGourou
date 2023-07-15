# DeGourou (DeDRM + libgourou)

_Automate the process of getting decrypted ebook from [InternetArchive](https://archive.org/) without the need for [Adobe Digital Editions](https://www.adobe.com/in/solutions/ebook/digital-editions/download.html) and [Calibre](https://calibre-ebook.com/)._

---

## News

Now You can use this on [Replit](https://replit.com/@bipinkrish/DeGourou) without worrying about the integrity/security or any other dependencies of this tool, but you need to know the [usage](#usage) so read the [examples](#examples) below

---

## Things you need

* ACSM file from the book page you borrowded from Internet Archive
* Adobe Account (optional) (dummy account recommended)
* InternetArchive Account (optional)
* Python v3.x.x Installed with pip (not required for normal users)

---

## Usage

```
usage: DeGourou.py [-h] [-f [F]] [-u [U]] [-t [T]] [-o [O]] [-la] [-li] [-e [E]] [-p [P]] [-lo]

Download and Decrypt an encrypted PDF or EPUB file.

optional arguments:
  -h, --help  show this help message and exit
  -f [F]      path to the ACSM file
  -u [U]      book url from InternetArchive
  -t [T]      book file type/format/extension for book url (defaults to PDF)
  -o [O]      output file name
  -la         login to your ADE account.
  -li         login to your InternetArchive.
  -e [E]      email/username
  -p [P]      password
  -lo         logout from all
```

---

## Guide

*By default it uses dummy account for ADE, you can also use your own account*
### For Normal Users

1. Download binary file according to your operating system from [Releases Section](https://github.com/bipinkrish/DeGourou/releases)
2. Run the binary according to operating system

    A. Windows user's can just open Command Prompt and use based on the [USAGE](https://github.com/bipinkrish/DeGourou#usage)

    B. Linux user's need to change the file permission and then can run

    ```
    chmod 777 DeGourou-linux
    ./DeGourou-linux
    ```

    Make sure you have installed `openssl` by using the command

    ```
    sudo apt-get install libssl-dev
    ```

    C. MacOS user's accordingly with name ```DeGourou.bin```

### For Developers

1. Clone the repositary or Download zip file and extract it
2. Install requirements using pip
3. Run "DeGourou.py" file


```
git clone https://github.com/bipinkrish/DeGourou.git
cd DeGourou
pip install -r requirements.txt
python DeGourou.py
```

---
## Examples


* #### Loging in your InternetArchive account

```
.\DeGourou-windows.exe -li -e abc@email.com -p myemailpassword
```
* #### To download from URL (only if your are logged in):

```
.\DeGourou-windows.exe -u https://archive.org/details/identifier
```

* #### To download from ACSM file

```
.\DeGourou-windows.exe -f URLLINK.acsm
```

---

## Advices

* Apply for [Print Disability access](https://docs.google.com/forms/d/e/1FAIpQLScSBbT17HSQywTm-fQawOK7G4dN-QPbDWNstdfvysoKTXCjKA/viewform) for encountering minimal errors while downloading from URL

* For rare books, you only able to borrow for 1hr, so to get the ACSM file from it, you have to use this below link, once after you clicked borrow
  
  https://archive.org/services/loans/loan/?action=media_url&format=pdf&redirect=1&identifier=XXX
  
  replace XXX with the identifier of the book, you can also change the format from "pdf" to "epub"

---
## Credits

This project is based on the following projects:

* [DeDrm Tools for eBooks](https://github.com/apprenticeharper/DeDRM_tools), by Apprentice Harper et al.
* [Standalone Version of DeDrm Tools](https://github.com/noDRM/DeDRM_tools), by noDRM
* [libgourou - a free implementation of Adobe's ADEPT protocol](https://indefero.soutade.fr//p/libgourou/), by Grégory Soutadé
* [Calibre ACSM Input plugin](https://github.com/Leseratte10/acsm-calibre-plugin), by Leseratte10

---

## Copyright Notices

<details>
  <summary>ACSM Input Plugin for Calibre - Copyright (c) 2021-2023 Leseratte10</summary>

```
ACSM Input Plugin for Calibre - Copyright (c) 2021-2023 Leseratte10
ACSM Input Plugin for Calibre / acsm-calibre-plugin
Formerly known as "DeACSM"
Copyright (c) 2021-2023 Leseratte10

This software is based on a Python reimplementation of the C++ library 
"libgourou" by Grégory Soutadé which is under the LGPLv3 or later 
license (http://indefero.soutade.fr/p/libgourou/).

I have no idea whether a reimplementation in another language counts 
as "derivative use", so just in case it does, I'm putting this project 
under the GPLv3 (which is allowed in the LGPLv3 license) to prevent any 
licensing issues. 

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

See the "LICENSE" file for a full copy of the GNU GPL v3.

========================================================================

libgourou:
Copyright 2021 Grégory Soutadé

This file is part of libgourou.

libgourou is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

libgourou is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License
along with libgourou. If not, see <http://www.gnu.org/licenses/>.
```
</details>