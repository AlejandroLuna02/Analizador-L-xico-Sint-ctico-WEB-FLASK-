import os
import re
from flask import Flask, request, render_template

app = Flask(__name__)
CARPETA_CODIGO = 'codigo_archivos/'
if not os.path.exists(CARPETA_CODIGO):
    os.makedirs(CARPETA_CODIGO)
app.config['CARPETA_CODIGO'] = CARPETA_CODIGO

def parse_codigo(code):
    result = []
    reserved_words = {'int', 'for', 'if', 'else', 'while', 'return', 'system.out.println'}
    lines = code.split('\n')
    for line_number, line in enumerate(lines, start=1):
        index = 0
        while index < len(line):
            word_found = False
            for word in reserved_words:
                if line[index:].startswith(word) and (index + len(word) == len(line) or not line[index + len(word)].isalnum()):
                    result.append((line_number, index, 'Reserved Word', word))
                    index += len(word)
                    word_found = True
                    break
            if word_found:
                continue

            character = line[index]
            if character in [';', '{', '}', '(', ')']:
                type_char = 'Semicolon' if character == ';' else 'Brace' if character in ['{', '}'] else 'Parenthesis'
                result.append((line_number, index, type_char, character))
                index += 1
            elif character.isdigit():
                result.append((line_number, index, 'Number', character))
                index += 1
            else:
                index += 1
    return result

def parse_estructura(code):
    analysis_result = []
    exact_keyword = 'system.out.println'
    lines = code.split('\n')
    for line_num, line_content in enumerate(lines, start=1):
        clean_line = line_content.strip()
        if clean_line.startswith('system.out.'):
            if clean_line.startswith(exact_keyword):
                analysis_result.append((line_num, exact_keyword, True))
            else:
                analysis_result.append((line_num, clean_line.split('(')[0], False))
        elif 'system' in clean_line or '.out' in clean_line:
            analysis_result.append((line_num, clean_line.split('(')[0], False))
        else:
            if 'for' in clean_line:
                match = re.match(r'\s*for\s*\(\s*int\s+\w+\s*=\s*\d+\s*;\s*\w+\s*(<|>|<=|>=)\s*\d+\s*;\s*\w+(\+\+|--)\s*\)\s*{', clean_line)
                if not match:
                    analysis_result.append((line_num, 'For', False))
                else:
                    analysis_result.append((line_num, 'For', True))
    return analysis_result

@app.route('/', methods=['GET', 'POST'])
def index():
    codigo = ""
    resultado_codigo = []
    resultado_estructura = []
    if request.method == 'POST':
        if 'clear' in request.form:
            return render_template('index.html', code='', lexical_result=[], syntactic_result=[])
        if 'file' in request.files and request.files['file'].filename != '':
            archivo = request.files['file']
            ruta_archivo = os.path.join(app.config['CARPETA_CODIGO'], archivo.filename)
            archivo.save(ruta_archivo)
            with open(ruta_archivo, 'r') as f:
                codigo = f.read()
        elif 'code' in request.form and request.form['code'].strip() != '':
            codigo = request.form['code']
        resultado_codigo = parse_codigo(codigo)
        resultado_estructura = parse_estructura(codigo)
    return render_template('index.html', code=codigo, lexical_result=resultado_codigo, syntactic_result=resultado_estructura)

if __name__ == '__main__':
    app.run(debug=True)
