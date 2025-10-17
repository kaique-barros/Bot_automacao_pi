from flask import Flask, jsonify, request
import json

app = Flask(__name__)

@app.route("/", methods=["POST"])
def imprimir():
  response = {"status": 200}
  return jsonify(response)


@app.route("/pix", methods=["POST"])
def imprimirPix():
  imprime = print(request.json)
  data = request.json
  with open('data.txt', 'a') as outfile:
      outfile.write("\n")
      json.dump(data, outfile)
  return jsonify(imprime)

def iniciar_webhook(webhook_port):
    print(webhook_port)
    app.run(host='0.0.0.0', port=webhook_port)