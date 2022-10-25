import sys

class_access_flags = [
    ['ACC_PUBLIC', 0x0001],
    ['ACC_FINAL', 0x0010],
    ['ACC_SUPER', 0x0020],
    ['ACC_INTERFACE', 0x0200],
    ['ACC_ABSTRACT', 0x0400],
    ['ACC_SYNTHETIC', 0x1000],
    ['ACC_ANNOTATION', 0x2000],
    ['ACC_ENUM', 0x4000]
]

field_access_flags = [
    ['ACC_PUBLIC', 0x0001],
    ['ACC_PRIVATE', 0x0002],
    ['ACC_PROTECTED', 0x0004],
    ['ACC_STATIC', 0x0008],
    ['ACC_FINAL', 0x0010],
    ['ACC_VOLATILE', 0x0040],
    ['ACC_TRANSIENT', 0x0080],
    ['ACC_SYNTHETIC', 0x1000],
    ['ACC_ENUM', 0x4000]
]

method_access_flags = [
    ['ACC_PUBLIC', 0x0001],
    ['ACC_PRIVATE', 0x0002],
    ['ACC_PROTECTED', 0x0004],
    ['ACC_STATIC', 0x0008],
    ['ACC_FINAL', 0x0010],
    ['ACC_SYNCHRONIZED', 0x0020],
    ['ACC_BRIDGE', 0x0040],
    ['ACC_VARARGS', 0x0080],
    ['ACC_NATIVE', 0x0100],
    ['ACC_ABSTRACT', 0x0400],
    ['ACC_STRICT', 0x0800],
    ['ACC_SYNTHETIC', 0x1000]
]

def dprint(d, indent):
    is_dict = type(d) is dict
    if len(d) == 0:
        if is_dict:
            print('{},')
        else:
            print('[],')
        return
    if is_dict:
        print(' {')
    else:
        print(' [')
    if is_dict:
        for (key, value) in d.items():
            print(indent * ' ', end='')
            if type(value) is dict or type(value) is list:
                print(f'\'{key}\': ', end='')
                dprint(value, indent+4)
            else:
                print(f'\'{key}\': {value},')
    else:
        for value in d:
            print(indent * ' ', end='')
            if type(value) is dict or type(value) is list:
                dprint(value, indent+4)
            else:
                print(f'{value},')
    if is_dict:
        print((indent - 4) * ' ', '},' if indent - 4 != 0 else '}')
    else:
        print((indent - 4) * ' ', '],' if indent - 4 != 0 else ']')

def prettyprint(d):
    type_map = {
        'B': 'byte',
        'C': 'char',
        'D': 'double',
        'F': 'float',
        'I': 'int',
        'J': 'long',
        'S': 'short',
        'Z': 'boolean',
        'V': 'void'
    }
    access_flags = {
        'ACC_PUBLIC': 'public',
        'ACC_PRIVATE': 'private',
        'ACC_PROTECTED': 'protected',
        'ACC_STATIC': 'static',
        'ACC_FINAL': 'final',
        'ACC_SYNCHRONIZED': 'synchronized',
        'ACC_BRIDGE': 'bridge',
        'ACC_VARARGS': 'varargs',
        'ACC_NATIVE': 'native',
        'ACC_ABSTRACT': 'abstract',
        'ACC_STRICT': 'strict',
        'ACC_SYNTHETIC': 'synthetic'
    }
    constant_pool = d['constant_pool']
    obj = dict()
    this_class = constant_pool[constant_pool[d['this_class'] - 1]['name_index'] - 1]['bytes'].decode('utf-8').split('/')
    obj['package'] = '.'.join(this_class[:-1])
    obj['class_name'] = this_class[-1]
    obj['super_class'] = constant_pool[constant_pool[d['super_class'] - 1]['name_index'] - 1]['bytes'].decode('utf-8').replace('/', '.')
    obj['interfaces'] = []
    for interface in d['interfaces']:
        index = interface['name_index']
        obj['interfaces'].append(constant_pool[index - 1]['bytes'].decode('utf-8').replace('/', '.'))
    obj['fields'] = []
    for field in d['fields']:
        dc = dict()
        name_index = field['name_index']
        descriptor_index = field['descriptor_index']
        dc['name'] = constant_pool[name_index - 1]['bytes'].decode('utf-8')
        dc['type'] = constant_pool[descriptor_index - 1]['bytes'].decode('utf-8')
        obj['fields'].append(dc)
    obj['methods'] = []
    for method in d['methods']:
        dc = dict()
        name_index = method['name_index']
        descriptor_index = method['descriptor_index']
        dc['name'] = constant_pool[name_index - 1]['bytes'].decode('utf-8')
        dc['type'] = constant_pool[descriptor_index - 1]['bytes'].decode('utf-8').replace('/', '.')
        dc['flags'] = method['access_flags']
        signature = constant_pool[descriptor_index - 1]['bytes'].decode('utf-8').replace('/', '.')
        sig = signature.replace('(', '').replace(')', '').split(';')
        fns = ''
        for flag in dc['flags']:
            fns += access_flags[flag]
            fns += ' '
        rt = sig[-1]
        arrays = 0
        while rt[0] == '[':
            arrays += 1
            rt = rt[1:]
        if rt[0] == 'L':
            rt = rt[1:]
            fns += rt
        else:
            fns += type_map[rt] if rt in type_map else rt
        fns += '[]' * arrays
        fns += ' '
        fns += dc['name'] + '('
        for i in range(len(sig[:-1])):
            parameter = sig[i]
            arrays = 0
            while parameter[0] == '[':
                arrays += 1
                parameter = parameter[1:]
            if i != 0:
                fns += ', '
            if parameter[0] == 'L':
                fns += parameter[1:]
            else:
                fns += type_map[parameter] if parameter in type_map else parameter
            fns += '[]' * arrays
        fns += ')'
        dc['function_signature'] = fns
        obj['methods'].append(dc)
    dprint(obj, 4)


class Decompiler:

    obj = {}
    f = None

    def __init__(self, raw):
        self.f = open(sys.argv[1], 'rb')
        self.read_magic()
        self.f.close()
        if raw:
            dprint(self.obj, 0)
        else:
            prettyprint(self.obj)

    def read1(self):
        return int.from_bytes(self.f.read(1), 'big')

    def read2(self):
        return int.from_bytes(self.f.read(2), 'big')

    def read4(self):
        return int.from_bytes(self.f.read(4), 'big')

    def read_magic(self):
        self.obj['magic'] = self.f.read(4)
        if self.obj['magic'] != b'\xca\xfe\xba\xbe':
            print('unknown format (wrong magic)')
            sys.exit(1)
        self.read_version()

    def read_version(self):
        self.obj['minor_version'] = self.read2()
        self.obj['major_version'] = self.read2()
        self.read_constant_pool()

    def read_constant_pool(self):
        self.obj['constant_pool_count'] = self.read2()
        self.obj['constant_pool'] = []
        for i in range(self.obj['constant_pool_count'] - 1):
            constant = dict()
            constant['tag'] = self.read1()
            match constant['tag']:
                case 7:
                    constant['name_index'] = self.read2()
                case 9:
                    constant['class_index'] = self.read2()
                    constant['name_and_type_index'] = self.read2()
                case 10:
                    constant['class_index'] = self.read2()
                    constant['name_and_type_index'] = self.read2()
                case 11:
                    constant['class_index'] = self.read2()
                    constant['name_and_type_index'] = self.read2()
                case 8:
                    constant['string_index'] = self.read2()
                case 12:
                    constant['name_index'] = self.read2()
                    constant['descriptor_index'] = self.read2()
                case 1:
                    constant['length'] = self.read2()
                    constant['bytes'] = self.f.read(constant['length'])
                case _:
                    print(f'unknown tag {constant["tag"]} (not yet implemented)')
                    sys.exit(1)
            self.obj['constant_pool'].append(constant)
        self.read_access_flags()

    def read_access_flags(self):
        access_flags = self.read2()
        self.obj['access_flags'] = []
        for flag in class_access_flags:
            if access_flags & flag[1] != 0:
                self.obj['access_flags'].append(flag[0])
        self.read_this_class()

    def read_this_class(self):
        self.obj['this_class'] = self.read2()
        self.read_super_class()

    def read_super_class(self):
        self.obj['super_class'] = self.read2()
        self.read_interfaces()

    def read_interfaces(self):
        self.obj['interfaces_count'] = self.read2()
        self.obj['interfaces'] = []
        for i in range(self.obj['interfaces_count']):
            interface = dict()
            interface['tag'] = self.read1()
            interface['name_index'] = self.read2()
        self.read_fields()

    def read_fields(self):
        self.obj['fields_count'] = self.read2()
        self.obj['fields'] = []
        for i in range(self.obj['fields_count']):
            field = dict()
            field_access_flag = self.read2()
            field['access_flags'] = []
            for flag in field_access_flags:
                if field_access_flag & flag[1] != 0:
                    field['access_flags'].append(flag[0])
            field['name_index'] = self.read2()
            field['descriptor_index'] = self.read2()
            field['attributes_count'] = self.read2()
            field['attributes'] = []
            for j in range(field['attributes_count']):
                attribute = dict()
                attribute['attribute_name_index'] = self.read2()
                attribute['attribute_length'] = self.read4()
                attribute['info'] = []
                for k in range(field['attribute_length']):
                    attribute['info'].append(self.read1())
                field['attributes'].append(attribute)
            self.obj['fields'].append(field)
        self.read_methods()

    def read_methods(self):
        self.obj['methods_count'] = self.read2()
        self.obj['methods'] = []
        for i in range(self.obj['methods_count']):
            method = dict()
            method['access_flags'] = []
            method_access_flag = self.read2()
            for flag in method_access_flags:
                if method_access_flag & flag[1] != 0:
                    method['access_flags'].append(flag[0])
            method['name_index'] = self.read2()
            method['descriptor_index'] = self.read2()
            method['attributes_count'] = self.read2()
            method['attributes'] = []
            for j in range(method['attributes_count']):
                attribute = dict()
                attribute['attribute_name_index'] = self.read2()
                attribute['attribute_length'] = self.read4()
                attribute['info'] = []
                for k in range(attribute['attribute_length']):
                    attribute['info'].append(self.read1())
                method['attributes'].append(attribute)
            self.obj['methods'].append(method)
        self.read_attributes()

    def read_attributes(self):
        self.obj['attributes_count'] = self.read2()
        self.obj['attributes'] = []
        for i in range(self.obj['attributes_count']):
            attribute = dict()
            attribute['attribute_name_index'] = self.read2()
            attribute['attribute_length'] = self.read4()
            attribute['info'] = []
            for j in range(attribute['attribute_length']):
                attribute['info'].append(self.read1())
            self.obj['attributes'].append(attribute)


if __name__ == '__main__':
    Decompiler('-raw' in sys.argv)
