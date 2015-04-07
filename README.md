# moa-ppsm sandbox

A sandbox containing all necessary Python scripts and configuration files to
profile and benchmark the `moa-ppsm` MOA extension, developed for the Bachelor's
Degree Final Project.

## NOTE

This sandbox is currently uncomplete: the `lib` folder is missing and no
JAR files are provided, because they are binary files that should not belong
to a Git repository.

The missing and needed files are `moa.jar`, `moa-ppsm.jar` and `sizeofag.jar`.

# Scripts

Python scripts are provided to perform a series of tasks, mainly to automate
many processes such as executions and results data treatment.

Most of the scripts are implemented using the `argparse` module. Please execute
them with the `-h` option to get a usage manual description. Example:

```
$> anonymize.py -h
```
