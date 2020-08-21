import argparse
import os
from utils.git import Stage
from subprocess import call

def parseArguments():
    argparser = argparse.ArgumentParser(
        prog='commit',
        description='Runs git-commit with commit message that is prefilled with the ticket number.'
    )
    argparser.add_argument(
        '-s',
        '--simple',
        help="Commit message will not be prefilled",
        action="store_true"
    )
    args = argparser.parse_args()
    return args

def commit(content=''):
    tmpFilePath = os.path.expanduser('~/.tmp_commit_template')
    tmpFile = open(tmpFilePath, 'w')
    tmpFile.write(content)
    tmpFile.close()

    command = ['git', 'commit', '-t', tmpFilePath]
    returnCode = call(command)

    os.remove(tmpFilePath)

    return returnCode == 0

if __name__ == '__main__':
    args = parseArguments()

    commitSuccessful = False
    if args.simple:
        commitSuccessful = commit()

    else:
        repository_directory = os.getcwd()
        stage = Stage(repository_directory)

        name = stage.active_branch_name().split('/')[-1]
        ticket = '-'.join(name.split('-')[:2])

        if ticket in ['master', 'develop']:
            commitSuccessful = commit()
        else:
            commitSuccessful = commit('{}'.format(ticket))


    if commitSuccessful:
        print('okay')
    else:
        print('nooo')