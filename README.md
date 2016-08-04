Export music library to playlists
=================================

Export banshee music libraries to individual playlists.

Maintaining music in a music library progamm like [banshee](http://banshee.fm/) comes with many benefits. However,
the great disadvantage is that playing, finding and maintaining the music will always be tied to the program when
starting to do it. The music library is not easily shared across computers, let alone compatible across platforms or
mobile devices that cannot be synched by the music library program.

One prominent issue with [banshee](http://banshee.fm/) is that it does not allow batch export of playlists. Once
starting to use [banshee](http://banshee.fm/), playlists cannot be shared easily. [banshee](http://banshee.fm/) stores
its music library in a SQL database. This script reads the database and exports the contained playlists in individual
playlist files compatible with almost any media player.

**Note:** The script was written with [banshee](http://banshee.fm/) in mind. Nevertheless, there is **no restriction**
on only exporting [banshee](http://banshee.fm/) libraries. I am not aware whether [banshee](http://banshee.fm/) uses a
music-library-typical structure for SQL database. This script might very well work with other music libraries as
well. This is not tested.

Requirements
------------

- [Python 2.7](https://www.python.org/download/releases/2.7/)
- [Sqlite3](https://www.sqlite.org)

Usage
-----

1. Clone or [download](../../archive/master.zip) this repository.
2. Start the terminal and navigate to the script.
3. You may have to set the script to executable.

```bash
$ chmod +x exportPlaylists.py
```

Running the script with the default settings is straight forward.

```bash
$ ./exportPlaylists.py
```

The help command shows available options for advanced usage

```bash
$ ./exportPlaylists.py --help
usage: exportPlaylists.py [-h] [-db DATABASE] [-outdir FILEPATH]
                          [-postfix POSTFIX] [-ext EXTENSION] [-clearDir]
                          [-keepDuplicates] [-order {pos,id,path}]

Export playlists from database

optional arguments:
  -h, --help            show this help message and exit
  -db DATABASE          path to music library (SQL database) (default:
                        '~/.config/banshee-1/banshee.db')
  -outdir FILEPATH      target directory in which to place playlists (default:
                        '~/playlists/')
  -postfix POSTFIX      append custom postfix to all playlist names (default:
                        '')
  -ext EXTENSION        playlist file extension (default: 'm3u')
  -clearDir             clear target directory before inserting playlists
  -keepDuplicates       keep duplicate song in playlists
  -order {pos,id,path}  sort playlists by 'order'. Leave out to disable
                        sorting
```
