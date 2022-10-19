# jinspector
jinspector - a simple, not ready for anything java class decompiler (of some sort)

I did this just because I was curious about the structure of java class files.

This thing is not ready for anything and probably infested with bugs but it can parse and decompile simple class files (like the one included in this repo).

Run with:
```
python main.py <classfile>
```

This outputs the class name, package name, methods and a few other things.

Run with the `-raw` argument to just get everything the script found (not pretty or sorted in any way).
