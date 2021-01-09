#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import yaml
import traceback
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from flask import Flask, jsonify, request, Response, send_from_directory
from waitress import serve

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "fgi"))

import fgi
from fgi.base import cook_game
from fgi.generate import Generator
from fgi.renderers.game import RendererGame

gen = Generator(["--no-sitemap", "--no-searchdb", "--data-dir-prefix", "fgi", "-"])
gen.prepare()
lctx = gen.lctx.copy()
gen.base_l10n["infobar"] ="Generated by FGI validator (BETA)" 
lctx["lang"] = "c"
lctx["ui"] = gen.base_l10n
lctx["rr"] = "https://furrygames.top/"
renderer = RendererGame(gen, lctx)

app = Flask(__name__)
schemas = dict()

def result(error, data, ctype='text/plain; charset=utf-8'):
    return Response(data, 200, {
        "Content-Type": ctype
    })

@app.route('/validate/game', methods=['POST'])
def _validate():
    try:
        body = request.form
        schema = body["schema"] + ".schema.yaml"
        if schema not in schemas:
            return result(True, "No such schema")

        data = body["data"]

        try:
            game = yaml.safe_load(data) 
            validate(game, schemas[schema])
        except ValidationError as e:
            return result(False, str(e))
        except yaml.YAMLError as e:
            return result(False, str(e))

        if schema == "game":
            game["id"] = "__VALIDATOR_GAME"
            game["tr"] = dict()
            game["mtime"] = 1

            try:
                cook_game(game, gen.tagmgr, gen.mfac)
                html = renderer.render_game(game["id"], game)
            except e:
                return result(False, str(e))

            return result(False, html, ctype="text/html; charset=utf-8")
        else:
            return result(False, "Check passed.")
    except:
        print(traceback.format_exc())
        return result(True, "invalid argument or our internal error")

@app.route('/', methods=['GET'])
def _root():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    for i in os.listdir("fgi/schemas/"):
        with open(os.path.join("fgi", "schemas", i)) as f:
            schema = yaml.safe_load(f)
            schemas[i] = schema

    serve(app=app, host='0.0.0.0', port=int(os.getenv('PORT')))
