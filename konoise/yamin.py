import random
from .utils import assemble, disassemble

rng = random.Random()
_dict_yamin = {('ㄷ', 'ㅐ', ' '): ('ㅁ', 'ㅓ', ' '), ('ㅁ', 'ㅕ', ' '): ('ㄸ', 'ㅣ', ' '), ('ㄱ', 'ㅟ', ' '): ('ㅋ', 'ㅓ', ' '), ('ㅍ', 'ㅏ', ' '): ('ㄱ', 'ㅘ', ' '),
               ('ㅍ', 'ㅣ', ' '): ('ㄲ', 'ㅢ', ' '), ('ㅇ', 'ㅠ', ' '): ('ㅇ', 'ㅡ', 'ㄲ'), ('ㄱ', 'ㅜ', 'ㅅ'): ('ㄱ', 'ㅡ', 'ㅅ')}


def _cond_base(vlist, rng, prob=1.):
    return vlist[2] != '' and rng.random() < prob


def _cond_yamin(vlist):
    return vlist[:2] in _dict_yamin or vlist in _dict_yamin


def yamin_jungum(text, prob=0.5):
    decomposed = [disassemble(t) for t in text]
    replaced = []
    for de in decomposed:
        rep = de
        if _cond_base(de, rng, prob):
            if de in _dict_yamin:
                rep = _dict_yamin[de]
        replaced.append(rep)
    return ''.join([assemble(r) for r in replaced])


if __name__ == '__main__':
    print(yamin_jungum('이유로', prob=1.))
