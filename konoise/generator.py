import random
from collections import defaultdict
from .spliter import NoSplit, SentenceSplit, ParagraphSplit
from .utils import partition
from .segments import change_vowels, disattach_letters
from .phoneme import phonetic_change
from .yamin import yamin_jungum
from functools import partial
from typing import Union, List
from .rust_generator import *


_AVAILABLE_METHODS = {
    "palatalization", "liquidization", "nasalization", "assimilation", "linking", "disattach-letters", "change-vowels", "yamin-jungum"
}


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

    def generate(self,
                 text: Union[str, List[str]],
                 methods: str = 'disattach-letters',
                 prob: float = 0.5,
                 delimiter: str = 'no',
                 use_rust_tokenizer=True) -> Union[str, List[str], List[List[str]]]:

        text = [text] if isinstance(text, str) else text
        spliter = self.spliter.get(delimiter)
        assert spliter is not None, "'delimiter' should be one of 'no', 'sentence', and 'paragraph'."

        available_methods = [
            partial(get_noise_batch, method=m, prob=prob) if use_rust_tokenizer
            else lambda xs: [self.noiser[m](x, prob) for x in xs]
            for m in methods.split(',') if m in self.noiser
        ]
        assert len(available_methods) > 0, f"method should be one of {_AVAILABLE_METHODS}."

        texts = [(i, j, e) for i, t in enumerate(text) for j, e in enumerate(spliter.split(t)) if isinstance(e, str)]

        random.shuffle(texts)
        doc_ids, sen_ids, sentences = list(zip(*texts))

        steps = max(int(len(sentences)/len(available_methods)), 1)
        max_len = len(available_methods)-1


        outputs = []
        for m, values in enumerate(partition(sentences, steps)):
            if len(values):
                outputs += available_methods[min(m, max_len)](values)

        output_dict = defaultdict(lambda: defaultdict(str))
        for d, s, o in zip(doc_ids, sen_ids, outputs):
            output_dict[d][s] = o

        return [[e for _, e in sorted(v.items())] for _, v in sorted(output_dict.items())]