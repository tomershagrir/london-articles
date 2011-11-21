import assistly
import os

# Downloads setuptools if not find it before try to import
try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass

from setuptools import setup

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way. Copied from Django.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

packages = []
data_files = []
assistly_dir = 'assistly'

for dirpath, dirnames, filenames in os.walk(assistly_dir):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]

    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))

    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])    

setup(
    name='python-assistly',
    version=assistly.__version__,
    #url='',
    author=assistly.__author__,
    license=assistly.__license__,
    packages=packages,
    data_files=data_files,
    #requires=['simplejson'],
    )

