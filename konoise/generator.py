from .segments import change_vowels, disattach_letters
from .phoneme import phonetic_change
from .yamin import yamin_jungum

from multiprocessing import Pool, cpu_count
from tqdm import tqdm

import re
import random
from functools import partial


def split_sentence(text):
    return re.split('(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)


def _generate(text, candidates, rng, prob):
    return rng.choice(candidates)(text, prob=prob)


class NoiseGenerator(object):
    def __init__(self, num_cores=None):
        self.rng = random.Random()
        self.pooler = Pool(processes=num_cores if num_cores else cpu_count())
        self.functions = {
            'disattach-letters': disattach_letters,
            'change-vowels': change_vowels,
            'palatalization': partial(phonetic_change, func='palatalization'),
            'linking': partial(phonetic_change, func='linking'),
            'liquidization': partial(phonetic_change, func='liquidization'),
            'nasalization': partial(phonetic_change, func='nasalization'),
            'assimilation': partial(phonetic_change, func='assimilation'),
            'yamin-jungum': yamin_jungum,
        }

        self.delis = {
            'total': ('', ''),
            'sentence': (split_sentence,' '),
            'newline': (lambda s: s.split('\n'), '\n')
        }

    def generate(self, text, methods='disattach-letters', prob=1., delimeter='newline', verbose=1) -> str:
        assert delimeter in self.delis, 'Not Defined Delimeter!'
        if isinstance(methods, str):
            methods = methods.split(',')
            if 'all' in methods:
                methods = list(self.functions.keys())

        candidates = [self.functions[f] for f in methods if self.functions]
        self.rng.shuffle(candidates)

        if not candidates:
            raise KeyError(f"There are no funtions available(Functions:{','.join(list(self.functions.keys()))})")

        text = self.delis[delimeter][0](text)
        new_text = self.run_multiprocessing(partial(_generate, candidates=candidates, rng=self.rng, prob=prob), text, verbose=verbose)
        n_iters=0
        while text == new_text:
            if 10 < n_iters:
                break
            for candidate in candidates:
                new_text = self.run_multiprocessing(partial(_generate, candidates=[candidate], rng=self.rng, prob=prob), text, verbose=0)
                if text != new_text:
                    break
            n_iters+=1
        return self.delis[delimeter][1].join(new_text)

    def run_multiprocessing(self, func, argument_list, verbose=1):
        if verbose:
            return [r for r in tqdm(self.pooler.imap(
                func=func, iterable=argument_list), total=len(argument_list))]
        else:
            return [r for r in self.pooler.imap(func=func, iterable=argument_list)]
