import os

from git import Repo

class File:

    def untracked_file(relative_path):
        return File(relative_path, False, False, False, '?')

    def from_diff(diff, staged):
        return File(diff.a_path, True, staged, diff.renamed_file, diff.change_type)

    def __init__(self, relative_path, tracked, staged, renamed, change_type):
        super().__init__()
        self.__relative_path = relative_path
        self.__tracked = tracked
        self.__staged = staged
        self.__renamed = renamed
        self.__change_type = change_type

    def get_relative_path(self):
        return self.__relative_path

    def is_tracked(self):
        return self.__tracked

    def is_staged(self):
        return self.__staged

    def is_renamed(self):
        return self.__renamed

    def get_change_type(self):
        return self.__change_type


class Stage:

    def __init__(self, directory):
        super().__init__()
        self.__repo = Repo(directory)

    def active_branch_name(self):
        return self.__repo.active_branch.name

    def status(self):
        result = self.__staged_files() + self.__unstaged_files() + self.__untracked_files()
        #result.sort(key= lambda file: os.path.basename(file.get_relative_path()))
        result.sort(key= lambda file: file.get_relative_path())
        return result

    def __staged_files(self):
        return [File.from_diff(diff, True) for diff in self.__repo.index.diff(self.__repo.head.commit)]

    def __unstaged_files(self):
        return [File.from_diff(diff, False) for diff in self.__repo.index.diff(None)]

    def __untracked_files(self):
        return [File.untracked_file(f) for f in self.__repo.untracked_files]

    def stash_all(self):
        pass

    def pop_stash(self):
        pass

    def ignore(self, untracked_file):
        pass

    def checkout(self, diff):
        pass