# jinspector
jinspector - a simple, not ready for anything java class decompiler (of some sort)

I did this just because I was curious about the structure of java class files.

This thing is not ready for anything and probably infested with bugs but it can parse and decompile simple class files (like the one included in this repo).

Run with:
```
python main.py <classfile>
```

This outputs the class name, package name, methods and a few other things.

For the class file in this repo for example, it outputs this:

```
{
    'package': com.llj.TestProject,
    'class_name': TestProject,
    'super_class': java.lang.Object,
    'interfaces': [],
    'fields': [],
    'methods':  [
         {
            'name': <init>,
            'type': ()V,
            'flags':  [
                ACC_PUBLIC,
             ],
            'function_signature': public void <init>(),
         },
         {
            'name': main,
            'type': ([Ljava.lang.String;)V,
            'flags':  [
                ACC_PUBLIC,
                ACC_STATIC,
             ],
            'function_signature': public static void main(java.lang.String[]),
         },
         {
            'name': returnInt,
            'type': (Ljava.lang.String;Ljava.lang.String;)I,
            'flags':  [
                ACC_PUBLIC,
                ACC_STATIC,
             ],
            'function_signature': public static int returnInt(java.lang.String, java.lang.String),
         },
     ],
 }
```

Run with the `-raw` argument to just get everything the script found (not pretty or sorted in any way).
