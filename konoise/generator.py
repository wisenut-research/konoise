import random
from .spliter import NoSplit, SentenceSplit, ParagraphSplit
from .segments import change_vowels, disattach_letters
from .phoneme import phonetic_change
from .yamin import yamin_jungum
from functools import partial
from typing import Union, Optional, List, Callable, Iterable
from tqdm import tqdm

from multiprocessing import cpu_count, Pool

from .rust_generator import *

RUST_AVAIL_METHODS = {
    "palatalization", "liquidization", "nasalization", "assimilation", "linking", "disattach-letters", "change-vowels", "yamin-jungum"
}


def run_imap_multiprocessing(func:Callable, argument_list: Iterable, num_processes: Optional[int] = None):
    pool = Pool(processes=cpu_count() if num_processes is None else num_processes)
    result_list_tqdm = []

    for result in tqdm(pool.imap(func=func, iterable=argument_list), total=len(argument_list)):
        result_list_tqdm.append(result)

    return result_list_tqdm


class NoiseGenerator:
    def __init__(self):
        self.rng = random.SystemRandom()

        self.spliter = {
            'no': NoSplit(),
            'sentence': SentenceSplit(),
            'paragraph': ParagraphSplit()
        }

        self.noiser = {
            'disattach-letters': disattach_letters,
            'change-vowels': change_vowels,
            'palatalization': partial(phonetic_change, func='palatalization'),
            'linking': partial(phonetic_change, func='linking'),
            'liquidization': partial(phonetic_change, func='liquidization'),
            'nasalization': partial(phonetic_change, func='nasalization'),
            'assimilation': partial(phonetic_change, func='assimilation'),
            'yamin-jungum': yamin_jungum,
        }

    def get_generate_function(self, methods, prob):
        if len(methods) == 1:
            func = methods[0]
            def generate_function(text):
                return func(text)
        else:
            def generate_function(text):
                return self.rng.choice(methods)(text)
        return generate_function

    def generate(self,
                 text: str,
                 methods: str = 'disattach-letters',
                 prob: float = 0.5,
                 delimiter: str = 'no',
                 use_rust_tokenizer=True) -> Union[str, List[str]]:

        methods = methods.split(',')

        if use_rust_tokenizer:
            methods = [partial(get_noise, method=m, prob=prob) if m in RUST_AVAIL_METHODS
                       else partial(self.noiser[m], prob=prob) for m in methods if m in self.noiser]
        else:
            methods = [partial(self.noiser[m], prob=prob) for m in methods if m in self.noiser]

        spliter = self.spliter.get(delimiter)

        assert spliter is not None, "'delimiter' should be one of 'no', 'sentence', and 'paragraph'."
        assert len(methods) > 0, f"method should be one of {list(self.noiser.keys())}."

        splited = spliter.split(text)
        generate_function = self.get_generate_function(methods, prob)

        output = generate_function(splited) if use_rust_tokenizer else run_imap_multiprocessing(generate_function, splited)
        return output[0] if len(output) == 1 else output

    def batch_generate(self,
                       texts: List[str],
                       methods: str = 'disattach-letters',
                       prob: float = 0.5,
                       delimiter: str = 'no',
                       use_rust_tokenizer=True) -> Union[str, List[str]]:

        methods = methods.split(',')
        
        if use_rust_tokenizer:
            methods = [partial(get_noise_batch, method=m, prob=prob) if m in RUST_AVAIL_METHODS
                       else partial(self.noiser[m], prob=prob) for m in methods if m in self.noiser]
        else:
            methods = [partial(self.noiser[m], prob=prob) for m in methods if m in self.noiser]

        spliter = self.spliter.get(delimiter)

        assert spliter is not None, "'delimiter' should be one of 'no', 'sentence', and 'paragraph'."
        assert len(methods) > 0, f"method should be one of {list(self.noiser.keys())}."
        
        splited = [unit for text in texts for unit in spliter.split(text)]
        generate_function = self.get_generate_function(methods, prob)
        
        output = generate_function(splited) if use_rust_tokenizer else run_imap_multiprocessing(generate_function, splited)
        return output[0] if len(output) == 1 else output
