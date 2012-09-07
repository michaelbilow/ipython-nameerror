ipython-nameerror
=================

I'm getting a NameError that strikes me (and at least one person who know more than I do
[http://stackoverflow.com/questions/12304847/ipython-parallel-computing-namespace-issues])
as weird. Any help is appreciated; I'm completely naive at this, so I apologize if
this is challenging to work with.

The code can be executed with 4 engines (yielding a NameError) using the commands

$ ipcluster start --n=4
$ python wrapper_wrapper.py

It was run on Windows 7, 32-bit Python 2.7.3, IPython 0.13
