def chunk(l,n):
    for i in range(0,len(l),n):
        yield l[i:i+n]

def hex_to_words(hexstring):
    words = []
    pos = 0
    for word in hexstring.split():
        if word.endswith(":"):
            pos = int(word[:-1],16)
            continue
        words.append(int(word,16))
    return words

def words_to_hex(words):
    hexlines = []
    word_format = "{0:0>4x}"
    for pos,group in enumerate(chunk(words,8)):
        hexline = word_format.format(pos*8) + ": " + \
                " ".join((word_format.format(x) for x in group))
        hexlines.append(hexline)
    return '\n'.join(hexlines) + '\n'
