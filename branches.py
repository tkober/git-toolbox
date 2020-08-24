import argparse
import os
from utils.git import Repository

class UI():

    def __init__(self, branches):
        self.__branches = branches


def parseArguments():
    argparser = argparse.ArgumentParser(
        prog='branches',
        description='Gives you an interactive overview of all branches'
    )
    argparser.add_argument(
        'PATH', nargs="?",
        help='The path to the git repository that shall be used. If no path is provided the current working directory will be used.'
    )
    return argparser.parse_args()


if __name__ == '__main__':
    args = parseArguments()

    if args.PATH:
        repositoryDirectory = os.path.abspath(args.PATH)
    else:
        repositoryDirectory = os.getcwd()
    repo = Repository(repositoryDirectory)

    print(repo.getBranches())