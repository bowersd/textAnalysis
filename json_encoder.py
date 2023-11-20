#from https://stackoverflow.com/questions/42710879/write-two-dimensional-list-to-json-file (accessed 2023-11-20)
from _ctypes import PyObj_FromPtr  # see https://stackoverflow.com/a/15012814/355230
import json
import re


class NoIndent(object):
    """ Value wrapper. """
    def __init__(self, value):
        if not isinstance(value, (list, tuple)):
            raise TypeError('Only lists and tuples can be wrapped')
        self.value = value

class MyEncoder(json.JSONEncoder):
    FORMAT_SPEC = '@@{}@@'  # Unique string pattern of NoIndent object ids.
    regex = re.compile(FORMAT_SPEC.format(r'(\d+)'))  # compile(r'@@(\d+)@@')

    def __init__(self, **kwargs):
        # Keyword arguments to ignore when encoding NoIndent wrapped values.
        ignore = {'cls', 'indent'}

        # Save copy of any keyword argument values needed for use here.
        self._kwargs = {k: v for k, v in kwargs.items() if k not in ignore}
        super(MyEncoder, self).__init__(**kwargs)

    def default(self, obj):
        return (self.FORMAT_SPEC.format(id(obj)) if isinstance(obj, NoIndent)
                    else super(MyEncoder, self).default(obj))

    def iterencode(self, obj, **kwargs):
        format_spec = self.FORMAT_SPEC  # Local var to expedite access.

        # Replace any marked-up NoIndent wrapped values in the JSON repr
        # with the json.dumps() of the corresponding wrapped Python object.
        for encoded in super(MyEncoder, self).iterencode(obj, **kwargs):
            match = self.regex.search(encoded)
            if match:
                id = int(match.group(1))
                no_indent = PyObj_FromPtr(id)
                json_repr = json.dumps(no_indent.value, **self._kwargs)
                # Replace the matched id string with json formatted representation
                # of the corresponding Python object.
                encoded = encoded.replace(
                            '"{}"'.format(format_spec.format(id)), json_repr)

            yield encoded

if __name__ == "__main__":
    # Example of using it to do get the results you want.

    alfa = [('a','b','c'), ('d','e','f'), ('g','h','i')]
    data = [(1,2,3), (2,3,4), (4,5,6)]

    data_struct = {
        'data': [NoIndent(elem) for elem in data],
        'alfa': [NoIndent(elem) for elem in alfa],
    }

    print(json.dumps(data_struct, cls=MyEncoder, sort_keys=True, indent=4))

    # Test custom JSONEncoder with json.dump()
    with open('data_struct.json', 'w') as fp:
        json.dump(data_struct, fp, cls=MyEncoder, sort_keys=True, indent=4)
        fp.write('\n')  # Add a newline to very end (optional).

