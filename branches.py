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
    return argparser.parse_args()


if __name__ == '__main__':
    args = parseArguments()

    repositoryDirectory = os.getcwd()
    repo = Repository(repositoryDirectory)

    print(repo.getBranches())