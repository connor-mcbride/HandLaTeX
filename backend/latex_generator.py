import json
import subprocess
import os


class LatexGenerator:
    def __init__(self, filename='notes.tex'):
        script_dir = os.path.dirname(__file__)
        json_path = os.path.join(script_dir, 'training_data', 'latex_conversion.json')

        with open(json_path, 'r') as file:
            self.conversions = json.load(file)

        self.packages = set()
        self.notes = []
        self.filename = filename
        self.preamble = (
            "\\documentclass[12pt,oneside]{article}\n"
            "\\usepackage[margin=1in]{geometry}\n"
        )
        self.epilogue = (
            "\\end{document}"
        )

    def add_symbols(self, symbols):
        for symbol in symbols:
            symbol_info = self.conversions[symbol]
            if symbol_info['mathmode']:
                self.notes.append('$' + symbol_info['command'] + '$')
            else:
                self.notes.append(symbol_info['command'])

            if 'package' in symbol_info:
                self.packages.add(symbol_info['package'])

        self.generate_file()

    def generate_file(self):
        file_text = self.preamble
        for package in self.packages:
            file_text += '\\usepackage{' + package + '}\n'

        file_text += '\\begin{document}\n'
        file_text += ' '.join(self.notes) + '\n'
        file_text += '\\end{document}'

        script_dir = os.path.dirname(__file__)
        json_path = os.path.join(script_dir, 'latex_file', self.filename)
        with open(json_path, 'w') as file:
            file.write(file_text)

        os.chdir('latex_file')
        subprocess.run(['latexmk'])
        os.chdir('..')
        subprocess.run(['code', self.filename])
