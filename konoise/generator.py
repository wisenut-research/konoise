import random
from collections import defaultdict
from .spliter import NoSplit, SentenceSplit, ParagraphSplit
from .utils import partition
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
        assert len(available_methods) > 0, f"method should be one of {list(self.noiser.keys())}."

        texts = [ (i, j, e) for i, t in enumerate(text) for j, e in spliter.split(t) if isinstance(e, str)]

        random.shuffle(texts)
        doc_ids, sen_ids, sentences = list(zip(*texts))

        steps = int(len(sentences)/len(available_methods))
        outputs = []
        for m, values in enumerate(partition(sentences, steps)):
            outputs += available_methods[m](values)

        output_dict = defaultdict(lambda:defaultdict(str))
        for d, s, o in zip(doc_ids, sen_ids, outputs):
            output_dict[d][s] = o

        return [[output_dict[d][s] for s in sorted(output_dict[d].keys())] for d in sorted(output_dict.keys())]