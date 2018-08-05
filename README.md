# CyTag

### A collection of surface-level natural language processing tools for Welsh

*CyTag* is a collection of surface-level natural language processing tools for Welsh, including:

* text segmenter (*cy_textsegmenter*)
* sentence splitter (*cy_sentencesplitter*)
* tokeniser (*cy_tokeniser*)
* part-of-speech (POS) tagger (*cy_postagger*)

As well as being run individually, the `CyTag.py` script allows for all of the tools to be run in sequence as a complete pipeline (the default option) or for a customised pipeline to be specified. Please see further sections of this file for more information on running the individual tools, the full default pipeline, or customised pipelines.

*CyTag* has been developed at Cardiff University as part of the [CorCenCC](http://www.corcencc.org) project.


## Dependencies

*CyTag* has been developed and tested on [Ubuntu](https://www.ubuntu.com/), and so these instructions should be followed with this in mind.

*CyTag* is written in [Python](https://www.python.org/), and so a recent version of *python3* should be downloaded before using the tools. Downloads for *python* can be found at https://www.python.org/downloads/ (version 3.5.1 recommended).

The following *python* libraries will be needed to run various *CyTag* components. *CyTag* will check for them and will stop running if they are missing:
* [lxml](https://lxml.de/)
* [progress](https://github.com/verigak/progress)
* [NumPy](http://www.numpy.org/)

*CyTag* depends on having a working version of VISL's [Constraint Grammar v3](http://visl.sdu.dk/cg3.html) (a.k.a. CG-3). For Ubuntu/Debian, a pre-built CG-3 package can be easily installed from a ready-made nightly repository:

```bash
wget https://apertium.projectjj.com/apt/install-nightly.sh -O - | sudo bash
sudo apt-get install cg3
```

See http://visl.sdu.dk/cg3/chunked/installation.html for installation instructions for other platforms.


## Usage

With *python* and *CG-3* installed, *CyTag* can then be run from the command line.

In all examples, `*PATH*` refers to the path leading from the current directory to the directory in which the *CyTag* folder is located.


## Passing input files to CyTag

In *Linux*, the following command will run the full, default pipeline over two input files, named `file1.txt` and `file2.txt`:

```bash
python3 *PATH*/CyTag/CyTag.py -i file1.txt file2.txt -n cytag_test -d cytag_test_2018-08-03 -f all
```

### Required arguments

#### -i/--input

The Welsh input file or files to be processed. 

### Optional arguments

#### -n/--name

A name to be used for the saved output text and files.

#### -d/--dir

A folder to be created in `*PATH*/CyTag/outputs/` and into which the output files from running *CyTag* will be saved.

#### -c/--component

Specify a specific part of the *CyTag* pipeline to run to. By default, the entire pipeline (text segmenter -> sentence splitter -> tokeniser -> part-of-speech tagger) is run. Currently supported components include: 'seg', 'sent', 'tok', 'pos'.

#### -f/--format

A file format to print output to. Currently supported formats include: 'tsv', 'xml', 'all'.


## Passing a string of text to CyTAG

Alternatively, a single text string (enclosed in quotation marks) can be passed as an argument to *CyTag*, which will run the full pipeline up to the POS tagger and return TSV values for each token to the standard output:

```bash
python3 *PATH*/CyTag/CyTag.py "Dw i'n hoffi coffi. Dw i eisiau bwyta'r cynio hefyd!"
```


## Taking input text from standard input

*CyTag* also accepts Welsh text passed via standard input. For example, in *Linux*:

```bash
echo "Dw i'n hoffi coffi. Dw i eisiau bwyta'r cynio hefyd!" | python3 *PATH*/CyTag/CyTag.py
```

```bash
cat example.txt | python3 *PATH*/CyTag/CyTag.py
```

```bash
python3 *PATH*/CyTag/CyTag.py < example.txt
```


## Contact

Questions about *CyTag* can be directed to: 
* Steve Neale <<steveneale3000@gmail.com>> <<NealeS2@cardiff.ac.uk>>
* Kevin Donnelly <<kevin@dotmon.com>>
* Dawn Knight <<KnightD5@cardiff.ac.uk>>


## License

*CyTag* is available under the GNU General Public License (v3), a copy of which is included with this repository.
