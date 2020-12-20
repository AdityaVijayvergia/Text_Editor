from text_editor import TextEditor
import timeit

class EditorBenchmarker:
    simple_editor_case = """
from __main__ import TextEditor
import random
s = TextEditor("{}")"""

    editor_cut_paste = """
for n in range({}):
    if n%2 == 0:
        s.cut(100, 300)
    else:
        s.paste(200)"""

    editor_copy_paste = """
for n in range({}):
    if n%2 == 0:
        s.copy(100, 300)
    else:
        s.paste(200)"""

    editor_get_text = """
for n in range({}):
    s.get_text()"""

    editor_mispellings = """
for n in range({}):
    s.misspellings()"""

    editor_all_operations = """
for n in range({}):
    if n%4 == 0:
        s.cut(100, 300)
    elif n%3 == 0:
        s.paste(200)
    elif n%2 == 0:
        s.copy(100, 300)
    else:
        s.paste(200)"""

    editor_random_operations = """
for n in range({}):
    i = random.randint(0,4)
    if i == 0:
        s.cut(100, 300)
    elif i == 1:
        s.paste(200)
    elif i == 2:
        s.copy(100, 300)
    else:
        s.paste(200)"""

    def __init__(self, cases, N):
        self.cases = cases
        self.N = N
        self.editor_cut_paste = self.editor_cut_paste.format(N)
        self.editor_copy_paste = self.editor_copy_paste.format(N)
        self.editor_get_text = self.editor_get_text.format(N)
        self.editor_mispellings = self.editor_mispellings.format(N)
        self.editor_random_operations = self.editor_random_operations.format(N)

    def benchmark(self):
        for case in self.cases:
            # print("Evaluating case: {}".format(case))
            new_editor = self.simple_editor_case.format(case)
            cut_paste_time = timeit.timeit(stmt=self.editor_cut_paste,setup=new_editor,number=1)
            print("{} cut paste operations took {} s".format(self.N, cut_paste_time))
            copy_paste_time = timeit.timeit(stmt=self.editor_copy_paste,setup=new_editor,number=1)
            print("{} copy paste operations took {} s".format(self.N, copy_paste_time))
            random_op_time = timeit.timeit(stmt=self.editor_random_operations,setup=new_editor,number=1)
            print("{} random operations took {} s".format(self.N, random_op_time))
            get_text_time = timeit.timeit(stmt=self.editor_get_text,setup=new_editor,number=1)
            print("{} text retrieval operations took {} s".format(self.N, get_text_time))
            mispellings_time = timeit.timeit(stmt=self.editor_mispellings,setup=new_editor,number=1)
            print("{} mispelling operations took {} s".format(self.N, mispellings_time))
            


def main():
    text = '12345 678 '*1024*1024
    # 10 mb of data

    b = EditorBenchmarker([text], 100)
    b.benchmark()


if __name__=='__main__':
    main()