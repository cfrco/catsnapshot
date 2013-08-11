# CatSnapShot 
A tool using rsync to backup and manage in Python.

## Features
* Use `rsync` and  `-a` , `--delete` , `--link-dest` (,`-vP`) options.
* JSON format config file.
* Use plain text file as database(snaplog).
* Use `label` as main element to manage `snapshot`.
* Can limit the number of `snapshot` with specific `label`.
* Work with `dbader/schedule` to take snapshot automatically.(need a few codes now)

## Usage
See `example/config.json` for config file,and  
See `example/backup.py` for auto-backup script(with `dbader/schedule`)

## TODO
See `TODO`

## Author
* CatCfrco (z82206.cat [at] gmail.com)
