consonant = ('ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ')
vowel = ('ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ')
final_consonant = (' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ')

composed = [consonant, vowel, final_consonant]


def disassemble(char):
    char = ord(char)
    if char < 44032 or 55203 < char:
        return chr(char), '', ''
    b = char - 44032
    c = b // 588
    v = (b - 588 * c) // 28
    fc = b - 588 * c - 28 * v
    return consonant[c], vowel[v], final_consonant[fc]


def assemble(vlist):
    if vlist[1] and vlist[2]:
        number = sum([composed[i].index(v)*n for i, (v, n) in enumerate(zip(vlist, [588, 28, 1]))])
        return chr(number + 44032)
    return vlist[0]
