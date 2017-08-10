import os
import re
from subprocess import call
import unicodedata

from flask import Flask, request, redirect, flash, render_template
from werkzeug.utils import secure_filename

import nltk

app = Flask(__name__)
app.secret_key = 'some_secret'


@app.route('/')
def index():
    return render_template('index.html')


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


def read_pdf(file):
    output = f'/tmp/{file}.txt'
    call(['pdftotext', '-layout', f'/tmp/{file}', output])
    with open(output) as f:
        return remove_accents(f.read()).lower().split('\x0c')  # pagebreaks


def make_rules(raw):
    raw = remove_accents(raw).lower()
    rules = [r for r in raw.splitlines() if len(r) > 0]

    words = raw
    for s in '+()|':
        words = words.replace(s, ' ')
    words = words.split()

    replacements = {w: f"presence['{w}']" for w in words}

    def replace(match):
        return replacements[match.group(0)]

    rulers = [re.sub('|'.join(f'\\b{re.escape(s)}\\b' for s in replacements),
                     replace, r) for r in rules]

    rulers = [r.replace('|', ' or ').replace('+', ' and ') for r in rulers]

    def matcher(tokens):
        env = {'presence': {w: w in tokens for w in words}}
        return [eval(r, env) for r in rulers]

    return rules, matcher


@app.route('/upload', methods=['POST'])
def upload_file():
    lang = request.form['lang']
    rules, matcher = make_rules(request.form['rules'])

    if len(rules) == 0:
        flash('No rules specified', 'warning')
        return redirect('/')

    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect('/')

    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'warning')
        return redirect('/')

    if file.filename[-4:] != '.pdf':
        flash('Invalid format, only PDF files are supported', 'danger')
        return redirect('/')

    filename = secure_filename(file.filename)
    file.save(os.path.join('/tmp', filename))
    pages = read_pdf(filename)
    presence = [matcher(nltk.word_tokenize(p, language=lang)) for p in pages]
    results = {
        r: [j+1 for j, m in enumerate(presence) if m[i]]
        for i, r in enumerate(rules)
    }
    return render_template('results.html', results=results)
