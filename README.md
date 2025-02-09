# sync-alt

Sync alt text of images across HTML files.

The original use case for this program is Twitter archives,
specifically ones created by [Darius Kazemi’s Twitter archiver](https://tinysubversions.com/twitter-archive/make-your-own/).
These archives are missing the alt text for the images included in the tweets.
You can add the alt text manually, but due to the format of the archive,
a tweet and its images can be included in many HTML files (if it’s part of a thread).
This program synchronizes the alt text between those copies:
you manually add it to one of the images,
and the program copies it to all the other copies of that same image.

The base version of the program doesn’t make many assumptions about the HTML format,
so it should also be possible to use it for other scenarios,
if you find that useful.

## Installation

I don’t know much about Python application packaging, but this should work in a venv:

```sh
pip install git+https://github.com/lucaswerkmeister/sync-alt
```

Other than that, I don’t know. pipx might work?

## Usage

This project includes two programs, `sync-alt` and `sync-alt-twitter`.
Both follow the same pattern:

```sh
sync-alt source-directory/ target-directory/
sync-alt-twitter path/to/twitter/backups/status path/to/twitter/backups/status-fixed
```

The whole source directory is copied to the target directory;
any `.html` files inside are adjusted (other files are copied unchanged).
`sync-alt` can be used for arbitrary HTML files,
and will sync the alt text between any images with the same `src=` attribute
(hopefully the `src=` uniquely identifies the image – it’s just compared as a string, not taking into account the current file’s directory or anything).
`sync-alt-twitter` expects HTML files created by the Twitter archiver mentioned above
(if you give it other HTML files, it will probably crash)
and takes some additional care to not mix up alt text between images from different tweets.
You can also write an alternate version that uses a different function to decide
which images should have their alt texts synchronized –
see the `keyer` argument of the `scan_directory()` function in the source code for details.

After running the program, you should inspect the output files / target directory
to see if everything looks alright and the program didn’t break anything.
If you’re happy with the result, go ahead and use it:

```sh
mv path/to/twitter/backups/status path/to/twitter/backups/status-orig
mv path/to/twitter/backups/status-fixed path/to/twitter/backups/status
```

## License

[Blue Oak Model License 1.0.0](https://blueoakcouncil.org/license/1.0.0).
