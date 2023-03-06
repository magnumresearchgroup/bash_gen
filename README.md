# bash_gen: A Python Bash Command Generator

[chatGPT achieved an accuracy score of 80.6% on the test set under zeroshot conditions]: https://arxiv.org/abs/2302.07845

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

Here we provide the python script for generating bash command with chatGPT and also the corresponding English in `chatGPT_generate.py`

## Rethinking NL2CMD in the age of ChatGPT 

There is a widespread belief among experts that the field of natural language processing (NLP) is currently experiencing a paradigm shift as a result of the introduction of LLM (Large Language Models), with chatGPT being the leading example of this new technology. With this new technology, many tasks that previously relied on fine-tuning pre-trained models can now be achieved through prompt engineering, which involves identifying the appropriate instructions to direct the language model (LLM) for specific tasks. To evaluate the effectiveness of chatGPT, we conducted tests on the original NL2BASH dataset, and the results were exceptional. Specifically, we found that **[chatGPT achieved an accuracy score of 80.6% on the test set under zeroshot conditions]**. Although there are concerns about the possibility of data leakage in LLM-based translation due to the vast amount of internet text in the pre-training data, we have confidence in the performance of chatGPT, given its consistent ability to achieve scores of 80% or higher across all training, testing, and evaluation datasets. 

<p align="center">
<img width="500" alt="pipeline" src="https://user-images.githubusercontent.com/31392274/223152672-4704ed94-83d1-4ff2-93d2-14dab48ab748.png">
</p>

We have conducted further exploration into the potential of streamlining our data generation pipeline with the assistance of ChatGPT, as shown in Figure. In order to generate Bash commands, we utilized the prompt Generate bash command and do not include example. We set the ”temperature” parameter to 1 for maximum variability. These generated commands were then subjected to a de-duplication script, resulting in a surprisingly low duplicate rate of 6% despite prompting the system 44671 times. Subsequently, the data were validated using the same bash parsing tool previously mentioned, and 41.7% of the generated bash commands were deemed valid. The preprocessed bash commands were combined with the prompt Translate to English, yielding a paired English-Bash dataset with a size of 17050. We set the temperature parameter to 0 for reproduciblity. 

In order to assess the quality of this generated dataset, we tested the performance of augmenting the original dataset with the generated version NL2CMD: An Updated Workflow for Natural Language to Bash Commands Translation 31 and found no performance drop. We further tested this approach by setting the temperature parameter to 1 to introduce more variability, which yielded different English sentences for each Bash command, serving as a useful data augmentation tool. 

This suggests that the ChatGPT-generated dataset is of higher quality than our previous pipeline. Furthermore, the performance of training on generated data and evaluating on NL2Bash was greatly improved, with the score increasing from -13% to approximately 10%. It is important to note that this is only a preliminary exploration into using ChatGPT as a data generation tool, and our observations represent a lower-bound on the potential benefits of this method. 

What is particularly groundbreaking about this approach is the efficiency with which it was implemented. Whereas the previous pipeline took two months to build, the ChatGPT streamlined version was completed in just three days. We have made our code and dataset available on Github. Notably, the distribution of generated utilities displayed a much smaller long tail effect, suggesting that it more accurately captures the command usage distribution.

## References

If you use this repository, please consider citing:

```
@article{Fu2021ATransform,
  title={A Transformer-based Approach for Translating Natural Language to Bash Commands},
  author={Quchen Fu and Zhongwei Teng and Jules White and Douglas C. Schmidt},
  journal={2021 20th IEEE International Conference on Machine Learning and Applications (ICMLA)},
  year={2021},
  pages={1241-1244}
}
```
```
@article{fu2023nl2cmd,
  title={NL2CMD: An Updated Workflow for Natural Language to Bash Commands Translation},
  author={Fu, Quchen and Teng, Zhongwei and Georgaklis, Marco and White, Jules and Schmidt, Douglas C},
  journal={Journal of Machine Learning Theory, Applications and Practice},
  pages={45--82},
  year={2023}
}
```

* [Magnum-NLC2CMD](https://github.com/magnumresearchgroup/Magnum-NLC2CMD)
* [OpenNMT-py](https://github.com/OpenNMT/OpenNMT-py)
* [Bashlex](https://github.com/idank/bashlex)
* [Clai](https://github.com/IBM/clai)
* [Tellina](https://github.com/TellinaTool/nl2bash)
