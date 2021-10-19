# bash_gen: A Python Bash Command Generator

## Background
This repository contains a python tool for scraping the linux man pages found at man7.org, and using the information scraped to generate bash commands based on the syntactical structure, flags, and argument types provided.
## Getting Started

```
from bash_gen.generator import Generator

UTILITIES = ['find', 'grep']

gen = Generator(utilities=UTILITIES) # initialize the generator
cmds = gen.generate_all_commands() # get a list of generated commands
```

## Files

<strong> syntax.json </strong> and <strong>utility_map.json</strong>
<br>
These files are included in the repository for easy access, but can also be customized and created by using the WebScraper class from scraper.py. Ensure that when you are running the generator class, these files lie within the same directory as the file you are invoking the class with.
<br>
<br>
<strong>scraper.py</strong>
<strong>generator.py</strong>