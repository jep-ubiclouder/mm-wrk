import StringIO
import binascii


def decode(text, k=16):
    nl = len(text)
    val = int(binascii.hexlify(text[-1]), 16)
    if val > k:
        raise ValueError('Input is not padded or padding is corrupt')

    l = nl - val
    return text[:l]


def encode(text, k=16):
    l = len(text)
    output = StringIO.StringIO()
    val = k - (l % k)
    for _ in xrange(val):
        output.write('%02x' % val)
    return text + binascii.unhexlify(output.getvalue())

credentials ={'user':'jep@assembdev.com', 'passwd':'ubi$2017', 'security_token':'aMddugz7oc45l1uhqWAE308Z'}
print(encode(credentials))


    