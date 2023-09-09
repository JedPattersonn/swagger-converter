import json
import sentry_sdk

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

class Converter:

    def convert_v2_to_v3(swagger_v2_doc):
        try:
            swagger_v3_doc = {
                "openapi": "3.0.0",
            }
            

            # Copy the info and servers (previously host, basePath in v2)
            if 'info' in swagger_v2_doc:
                swagger_v3_doc['info'] = swagger_v2_doc['info']

            if 'host' in swagger_v2_doc and 'basePath' in swagger_v2_doc:
                swagger_v3_doc['servers'] = [{"url": f"{swagger_v2_doc['host']}{swagger_v2_doc['basePath']}"}]

            # Paths transformation
            if 'paths' in swagger_v2_doc:
                paths = {}
                for path, methods in swagger_v2_doc['paths'].items():
                    transformed_methods = {}
                    for method, details in methods.items():
                        # Handling consumes for POST, PUT, PATCH
                        if method in ["post", "put", "patch"] and 'consumes' in details and 'parameters' in details:
                            body_parameters = [param for param in details['parameters'] if param['in'] == 'body']
                            if body_parameters:
                                param = body_parameters[0]
                                details['requestBody'] = {
                                    "content": {
                                        details['consumes'][0]: {
                                            "schema": param['schema']
                                        }
                                    }
                                }
                                details['parameters'].remove(param)
                            del details['consumes']
                        elif 'consumes' in details:
                            del details['consumes']
                        
                        # Adjusting parameters
                        if 'parameters' in details:
                            for param in details['parameters']:
                                if 'type' in param:
                                    param['schema'] = {
                                        "type": param['type']
                                    }
                                    del param['type']

                        # Transforming responses
                        if 'responses' in details:
                            details['responses'] = Converter.transform_responses_v2_to_v3(details['responses'])

                        transformed_methods[method] = details
                    paths[path] = transformed_methods
                swagger_v3_doc['paths'] = paths

            # Components (previously definitions in v2)
            if 'definitions' in swagger_v2_doc:
                swagger_v3_doc['components'] = {
                    "schemas": swagger_v2_doc['definitions']
                }

            return swagger_v3_doc
        except Exception as e:
            print(e)

    def transform_responses_v2_to_v3(responses_v2, default_content_type='application/json'):
        responses_v3 = {}
        for status, response in responses_v2.items():
            v3_response = {"description": response.get("description", "")}
            
            # If there's a schema, we'll wrap it under 'content'
            if "schema" in response:
                v3_response["content"] = {
                    default_content_type: {
                        "schema": response["schema"]
                    }
                }
            
            responses_v3[status] = v3_response

        return responses_v3

    def main(swagger_v2_json_str):
        v2_doc = json.loads(swagger_v2_json_str)
        v3_doc = Converter.convert_v2_to_v3(v2_doc)
        return json.dumps(v3_doc, indent=2)

    # Example usage:
    # json_string_v2 = '{"info": {...}, ...}'  # Replace this with your actual JSON string
    # result = main(json_string_v2)
    # print(result)
