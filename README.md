# CatSnapshot
A tool using rsync to backup and manage in Python.

## Features
* Use `rsync` and  `-a` , `--delete` , `--link-dest` (,`-v`) options.
* JSON format config file.
* Use plain text file as database(snaplog).
* Use `label` as main element to manage `snapshot`.
* Can limit the number of `snapshot` with specific `label`.
* Work with `dbader/schedule` to take snapshot automatically.
* Work with Plug&Play storage device (`check-path` and `feqcheck`)

## WARNING
* There are many problems should be resolved.
* There is no any guarantee.

## Install
#### Install Dependencies

    $ sudo pip install schedule python-dateutil    

## Usage
See `example/config.json` and `example/full.json` for config file,and  
See `example/backup.py` for auto-backup script(with `dbader/schedule`)

Or, use `catsnapshot.py`

    $ python catsnapshot.py -h # get help
    $ python catsnapshot.py example/config.json


## TODO
See `TODO`

## Author
* CatCfrco (z82206.cat [at] gmail.com)
