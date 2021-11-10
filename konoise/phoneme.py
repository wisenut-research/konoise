import random
from .utils import assemble, disassemble

rng = random.Random()

_palatalization_set = {'ㄷ': 'ㅈ', 'ㅌ': 'ㅊ'}
_palatalization_set2 = {'ㄷ': 'ㅊ', 'ㄱ': 'ㅋ'}
_linking_set = {'ㄻ': 'ㄹㅁ', 'ㅄ': 'ㅂㅆ', 'ㄳ': 'ㄱㅅ', 'ㄽ': 'ㄹㅅ', 'ㅊ': ' ㅊ', 'ㅂ': ' ㅂ', 'ㅍ': ' ㅂ', 'ㄷ': ' ㄹ', 'ㄹ': ' ㄹ', 'ㄹㅎ': ' ㄹ'}
_linking_words = ('이', '을', '를', '은', '았', '었', '아', '어')

_liquidization_set = {'ㄴㄹ': 'ㄹㄹ', 'ㄹㄴ': 'ㄹㄹ', 'ㄾㄴ': 'ㄹㄹ'}
_liquidization_exp = {'ㄴㄹㅕㄱ': 'ㄴㄴ'}

_nasalization_set = {'ㅂㅁ': 'ㅁㅁ', 'ㄷㄴ': 'ㄴㄴ', 'ㄱㅁ': 'ㅇㅁ', 'ㄱㄴ': 'ㅇㄴ', 'ㅇㄹ': 'ㅇㄴ', 'ㅁㄹ': 'ㅁㄴ', 'ㄲㄴ': 'ㅇㄴ', 'ㅂㄹ': 'ㅁㄴ', 'ㄱㄹ': 'ㅇㄴ', 'ㅊㄹ': 'ㄴㄴ', 'ㄺㄴ': 'ㅇㄴ', 'ㅍㄴ': 'ㅁㄴ'}
_assimilation_set = {'ㄺㄴ': 'ㅇㄴ'}


def palatalization(fc,nc):
    if (fc[2] in _palatalization_set) and nc[:2] == ['ㅇ', 'ㅣ']:
        nc[0], fc[2] = _palatalization_set[fc[2]], ' '
    if (fc[2] in _palatalization_set2) and nc[0] == 'ㅎ':
        nc[0], fc[2] = _palatalization_set2[fc[2]], ' '
    return fc, nc


def linking(fc,nc):
    if fc[2] in _linking_set and assemble(nc) in _linking_words:
        fc[2], nc[0] = _linking_set[fc[2]]
    return fc,nc


def liquidization(fc,nc):
    key = fc[2] + ''.join(nc)
    if key in _liquidization_exp:
        fc[2], nc[0] = _liquidization_exp[key]
    elif fc[2]+nc[0] in _liquidization_set:
        fc[2], nc[0] = _liquidization_set[fc[-1] + nc[0]]
    return fc,nc


def nasalization(fc,nc):
    key = fc[2] + nc[0]
    if key in _nasalization_set:
        fc[2], nc[0] = _nasalization_set[key]
    return fc, nc


def assimilation(fc,nc):
    key = fc[2] + nc[0]
    if key in _assimilation_set:
        fc[2], nc[0] = _assimilation_set[key]
    return fc, nc


_functions = {
    'palatalization': palatalization,
    'linking': linking,
    'liquidization': liquidization,
    'nasalization': nasalization,
    'assimilation': assimilation,
}


def _cond_base(rng, prob=1.):
    return rng.random() < prob


def _get_weights4funcs(funcs, weights):
    if not weights and len(funcs)!=0:
        weights = [1/len(funcs)]* len(funcs)
    if len(funcs) == len(weights):
        return weights
    else:
        raise ValueError("Please align the number of functions and weights(or leave blank).")


def _select_one(funcs, rng, weights):
    if len(funcs) == 1:
        return funcs[0]
    weights = _get_weights4funcs(funcs, weights)
    return rng.choices(funcs,weights=weights, k=1)[0]


def phonetic_change(text, funcs=['palatalization'], weights=[], prob=0.5):
    decomposed = [list(disassemble(t)) for t in text]
    funcs = [_functions[f] for f in funcs if f in _functions]
    for i in range(len(decomposed)-1):
        if _cond_base(rng, prob):
            decomposed[i], decomposed[i+1] = _select_one(funcs,rng, weights=weights)(decomposed[i], decomposed[i+1])
    return ''.join([assemble(vlist) for vlist in decomposed])