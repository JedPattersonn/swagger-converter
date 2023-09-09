from flask import Flask, request, jsonify
from flask_cors import CORS
from converter import Converter
import json

app = Flask(__name__)
CORS(app)

@app.route('/convert', methods=['POST'])
def convert_swagger():
    try:
        v2_doc = request.get_json()
        
        if not v2_doc:
            return jsonify({"error": "Invalid input, expected a JSON payload"}), 400

        v2_doc_str = json.dumps(v2_doc)
        v3_doc = Converter.main(v2_doc_str)
        
        return jsonify(v3_doc)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
