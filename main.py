import struct
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

def main():
    f = open(sys.argv[1], 'rb')
    obj = dict()
    obj['magic'] = f.read(4)
    if obj['magic'] != b'\xca\xfe\xba\xbe':
        print('unknown format (at least not java class format (magic wrong))')
    obj['minor_version'] = int.from_bytes(f.read(2), 'big')
    obj['major_version'] = int.from_bytes(f.read(2), 'big')
    obj['constant_pool_count'] = int.from_bytes(f.read(2), 'big')
    obj['constant_pool'] = []
    for i in range(obj['constant_pool_count'] - 1):
        constant = dict()
        constant['tag'] = int.from_bytes(f.read(1), 'big')
        match constant['tag']:
            case 7:
                constant['name_index'] = int.from_bytes(f.read(2), 'big')
            case 9:
                constant['class_index'] = int.from_bytes(f.read(2), 'big')
                constant['name_and_type_index'] = int.from_bytes(f.read(2), 'big')
            case 10:
                constant['class_index'] = int.from_bytes(f.read(2), 'big')
                constant['name_and_type_index'] = int.from_bytes(f.read(2), 'big')
            case 11:
                constant['class_index'] = int.from_bytes(f.read(2), 'big')
                constant['name_and_type_index'] = int.from_bytes(f.read(2), 'big')
            case 8:
                constant['string_index'] = int.from_bytes(f.read(2), 'big')
            case 12:
                constant['name_index'] = int.from_bytes(f.read(2), 'big')
                constant['descriptor_index'] = int.from_bytes(f.read(2), 'big')
            case 1:
                constant['length'] = int.from_bytes(f.read(2), 'big')
                constant['bytes'] = f.read(constant['length'])
            case _:
                print(f'unknown tag {constant["tag"]}')
                sys.exit(1)
        obj['constant_pool'].append(constant)
    access_flags = int.from_bytes(f.read(2), 'big')
    obj['access_flags'] = []
    for flag in class_access_flags:
        if access_flags & flag[1] != 0:
           obj['access_flags'].append(flag[0])
    obj['this_class'] = int.from_bytes(f.read(2), 'big')
    obj['super_class'] = int.from_bytes(f.read(2), 'big')
    obj['interfaces_count'] = int.from_bytes(f.read(2), 'big')
    obj['interfaces'] = []
    for i in range(obj['interfaces_count']):
        interface = dict()
        interface['tag'] = int.from_bytes(f.read(1), 'big')
        interface['name_index'] = int.from_bytes(f.read(2), 'big')
    obj['fields_count'] = int.from_bytes(f.read(2), 'big')
    obj['fields'] = []
    for i in range(obj['fields_count']):
        field = dict()
        field_access_flag = int.from_bytes(f.read(2), 'big')
        field['access_flags'] = []
        for flag in field_access_flags:
            if field_access_flag & flag[1] != 0:
                field['access_flags'].append(flag[0])
        field['name_index'] = int.from_bytes(f.read(2), 'big')
        field['descriptor_index'] = int.from_bytes(f.read(2), 'big')
        field['attributes_count'] = int.from_bytes(f.read(2), 'big')
        field['attributes'] = []
        for j in range(field['attributes_count']):
            attribute = dict()
            attribute['attribute_name_index'] = int.from_bytes(f.read(2), 'big')
            attribute['attribute_length'] = int.from_bytes(f.read(4), 'big')
            attribute['info'] = []
            for k in range(field['attribute_length']):
                attribute['info'].append(int.from_bytes(f.read(1), 'big'))
            field['attributes'].append(attribute)
        obj['fields'].append(field)
    obj['methods_count'] = int.from_bytes(f.read(2), 'big')
    obj['methods'] = []
    for i in range(obj['methods_count']):
        method = dict()
        method['access_flags'] = []
        method_access_flag = int.from_bytes(f.read(2), 'big')
        for flag in method_access_flags:
            if method_access_flag & flag[1] != 0:
                method['access_flags'].append(flag[0])
        method['name_index'] = int.from_bytes(f.read(2), 'big')
        method['descriptor_index'] = int.from_bytes(f.read(2), 'big')
        method['attributes_count'] = int.from_bytes(f.read(2), 'big')
        method['attributes'] = []
        for j in range(method['attributes_count']):
            attribute = dict()
            attribute['attribute_name_index'] = int.from_bytes(f.read(2), 'big')
            attribute['attribute_length'] = int.from_bytes(f.read(4), 'big')
            attribute['info'] = []
            for k in range(attribute['attribute_length']):
                attribute['info'].append(int.from_bytes(f.read(1), 'big'))
            method['attributes'].append(attribute)
        obj['methods'].append(method)
    obj['attributes_count'] = int.from_bytes(f.read(2), 'big')
    obj['attributes'] = []
    for i in range(obj['attributes_count']):
        attribute = dict()
        attribute['attribute_name_index'] = int.from_bytes(f.read(2), 'big')
        attribute['attribute_length'] = int.from_bytes(f.read(4), 'big')
        attribute['info'] = []
        for j in range(attribute['attribute_length']):
            attribute['info'].append(int.from_bytes(f.read(1), 'big'))
        obj['attributes'].append(attribute)
    f.close()
    if '-raw' in sys.argv:
        dprint(obj, 4)
    else:
        prettyprint(obj)

if __name__ == '__main__':
    main()
