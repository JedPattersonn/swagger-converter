from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from converter import Converter
import json
import redis
from decouple import config
from urllib.parse import urlparse
import sentry_sdk
from sentry_sdk import capture_exception
from sentry_sdk.integrations.flask import FlaskIntegration
import psycopg2

sentry_sdk.init(
    dsn="https://49a1a41b45c948689562808601f5d48b@o1072423.ingest.sentry.io/4505851487715328",
    integrations=[FlaskIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['CORS_HEADERS'] = 'Content-Type'


POSTGRES_URL = config('POSTGRES_URL')
POSTGRES_USER = config('POSTGRES_USER')
POSTGRES_HOST = config('POSTGRES_HOST')
POSTGRES_PASSWORD = config('POSTGRES_PASSWORD')
POSTGRES_DATABASE = config('POSTGRES_DATABASE')

connection = psycopg2.connect(
    dbname=POSTGRES_DATABASE,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST
)
cursor = connection.cursor()


@app.route('/convert', methods=['POST'])
@cross_origin()
def convert_swagger():
    try:
        v2_doc = request.get_json()
        
        if not v2_doc:
            return jsonify({"error": "Invalid input, expected a JSON payload"}), 400

        v2_doc_str = json.dumps(v2_doc)
        v3_doc = Converter.main(v2_doc_str)

        cursor.execute("UPDATE stats SET conversion_count = conversion_count + 1 WHERE id = 1;")
        connection.commit()


        response = jsonify(v3_doc)

        return response
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": e}), 500


    
@app.route('/stats', methods=['GET'])
def get_conversion_stats():
    cursor.execute("SELECT conversion_count FROM stats WHERE id = 1;")
    count = cursor.fetchone()[0]
    return jsonify({"conversion_count": count if count else 0})


if __name__ == "__main__":
    try:
        app.run(debug=True)
    finally:
        cursor.close()
        connection.close()