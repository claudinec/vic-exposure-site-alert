import os

def make_dir(path):
    """Creates the directory if it doesn't exist.
    
    If the path is a file instead, raise an error.
    """
    cwd = os.getcwd()
    with os.scandir(cwd) as cdir:
        if (path not in cdir):
            os.mkdir(path)
        elif (is_file(path)):
            # error
        else:
            # should be fine