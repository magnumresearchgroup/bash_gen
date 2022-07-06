# bash_gen: A Python Bash Command Generator

## Requirements
<details><summary>Show details</summary>
<p>

* beautifulsoup4==4.7.1
* json5==0.9.5

</p>
</details>

## Background
This repository contains a python tool for scraping the linux man pages found at man7.org, and using the information scraped to generate bash commands based on the syntactical structure, flags, and argument types provided.

This repository allows you to synthesize an entire dataset of valid bash commands. Together with a transformer-based backtranslation model, we were able to create a dataset of thousands of natural language, bash-command pairs to further the advancement of machine translation models.

## Quick-Start Guide

Getting started is very simple and quick. Below find an example of generating all potential commands for the find and grep utilities. 
git
```
from bash_gen.generator import Generator

UTILITIES = ['find', 'grep']

gen = Generator(utilities=UTILITIES) # initialize the generator
cmds = gen.generate_all_commands() # get a list of generated commands
```

## Validation

It is important to note that not all commands generated will be valid. This is where the `validate_commands()` method in `generator.py` becomes important. Ensure you read all documentation and only run this method in a controlled environment to prevent unexpected behavior.

## Examples

Although basic functionality is relatively straightforward, several examples provided in the `examples` folder demonstrate more advanced functionality, like generation of piped commands.

## Files

`syntax.json` and `utility_map.json`
<br><br>
These files are included in the repository for easy access, but can also be customized and created by using the WebScraper class from scraper.py. Ensure that when you are running the generator class, these files lie within the same directory as the file you are invoking the class with.
<br><br>
`scraper.py`
<br><br>
This file contains the WebScraper class, which is responsible for scraping the argument types and utility syntax for given utilities in the man pages. This class has been used to create the static files mentioned above, but in the instance you want to add support for another utility not mentioned or change the syntax or naming conventions for any utility, you will need to use this class.
<br><br>
`generator.py`
<br><br>
This is where the generation actually happens. In the instance that you want to match a particular distribution, make sure you pass in the `max_commands` parameter when using the `generate_commands` method.

## References

* [Magnum-NLC2CMD](https://github.com/magnumresearchgroup/Magnum-NLC2CMD)
* [OpenNMT-py](https://github.com/OpenNMT/OpenNMT-py)
* [Bashlex](https://github.com/idank/bashlex)
* [Clai](https://github.com/IBM/clai)
* [Tellina](https://github.com/TellinaTool/nl2bash)
