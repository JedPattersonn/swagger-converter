from flask import Flask, request, jsonify
from flask_cors import CORS
from converter import Converter
import json
import redis
from decouple import config
from urllib.parse import urlparse
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

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

KV_URL = config('KV_URL')
KV_REST_API_URL = config('KV_REST_API_URL')
KV_REST_API_TOKEN = config('KV_REST_API_TOKEN')
KV_REST_API_READ_ONLY_TOKEN = config('KV_REST_API_READ_ONLY_TOKEN')

parsed_redis_url = urlparse(KV_URL)
redis_client = redis.StrictRedis(host=parsed_redis_url.hostname, 
                                 port=parsed_redis_url.port, 
                                 password=parsed_redis_url.password, 
                                 db=0, 
                                 decode_responses=True)


@app.route('/convert', methods=['POST'])
def convert_swagger():
    try:
        v2_doc = request.get_json()
        
        if not v2_doc:
            return jsonify({"error": "Invalid input, expected a JSON payload"}), 400

        v2_doc_str = json.dumps(v2_doc)
        v3_doc = Converter.main(v2_doc_str)

        redis_client.incr('conversion_count')

        response = jsonify(v3_doc)
        response.headers.add('Access-Control-Allow-Origin', '*')


        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/stats', methods=['GET'])
def get_conversion_stats():
    count = redis_client.get('conversion_count')
    return jsonify({"conversion_count": int(count) if count else 0})


if __name__ == "__main__":
    app.run(debug=True)
