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
        '-e',
        '--empty',
        help="Commit message will not be prefilled.",
        action="store_true"
    )
    argparser.add_argument(
        '-p',
        '--push',
        help="After successful commit the current branch is immediately pushed to the default remote.",
        action="store_true"
    )
    argparser.add_argument(
        '-n',
        '--no-verify',
        help="Verify hooks will be bypassed. This effects both commit and possible push hooks.",
        action="store_true"
    )
    args = argparser.parse_args()
    return args

def commit(content='', noVerify=False):
    tmpFilePath = os.path.expanduser('~/.tmp_commit_template')
    tmpFile = open(tmpFilePath, 'w')
    tmpFile.write(content)
    tmpFile.close()

    command = ['git', 'commit', '-t', tmpFilePath]
    returnCode = call(command)

    os.remove(tmpFilePath)

    return returnCode == 0

def push(noVerify=False):
    command = ['git', 'push']
    if noVerify:
        command.append('--no-verify')

    returnCode = call(command)

    return returnCode == 0

if __name__ == '__main__':
    args = parseArguments()

    commitSuccessful = False
    if args.empty:
        commitSuccessful = commit(noVerify=args.no_verify)

    else:
        repository_directory = os.getcwd()
        stage = Stage(repository_directory)

        name = stage.active_branch_name().split('/')[-1]
        ticket = '-'.join(name.split('-')[:2])

        if ticket in ['master', 'develop', 'main']:
            commitSuccessful = commit(noVerify=args.no_verify)
        else:
            commitSuccessful = commit('{} '.format(ticket), args.no_verify)


    if commitSuccessful and args.push:
        push(args.no_verify)