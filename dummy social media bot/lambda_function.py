import json
import logging
from pathlib import Path
import jwt
from content_handler import ContentGenerator  # Import for reference, but we'll use dynamic loading
from user_handler import UserHandler  # Import for reference, but we'll use dynamic loading

SECRET_KEY = "my-secure-secret-key-12345"

def load_class(module: str, class_name: str):
    module_ref = __import__(module)
    return getattr(module_ref, class_name)

def call_method(class_obj, method_name, context: dict):
    method = getattr(class_obj, method_name)
    return method(context)

def verify_bearer_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

def lambda_handler(event, context):
    logging.basicConfig(level=logging.DEBUG)
    try:
        # Handle CORS preflight request
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                },
                "body": ""
            }

        path = event.get("path", "").strip("/")
        path_parts = [part.strip() for part in path.split("/")]
        logging.debug("Path components: %s", path_parts)

        module_key = path_parts[0] if len(path_parts) > 0 else None
        api_key = path_parts[1] if len(path_parts) > 1 else None

        # Token verification for non-login requests
        claims = None
        if not (module_key == "user" and api_key == "login"):
            headers = event.get("headers", {})
            auth_header = headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                raise Exception("Authorization header is missing or invalid")

            token = auth_header.split(" ")[1]
            claims = verify_bearer_token(token)

        # Loading API mappings from the file
        api_mapping_file = Path(__file__).absolute().parent / "api-mapping.json"
        with open(api_mapping_file, "r") as f:
            api_mapping = json.load(f)

        if not module_key or module_key not in api_mapping:
            raise Exception(f"Module '{module_key}' not found in API mapping.")

        module_config = api_mapping[module_key]

        if not api_key or api_key not in module_config:
            raise Exception(f"API '{api_key}' not found in module '{module_key}'.")

        apis = module_config[api_key]
        http_method = event.get("httpMethod", "").upper()
        selected_api = None

        # Finding the correct API method to call
        for api in apis:
            if api["request_method"].upper() == http_method and api["path"] == "/".join(path_parts[2:]):
                selected_api = api
                break

        if not selected_api:
            raise Exception(f"No matching API found for path: {path} and method: {http_method}")

        # Get the class and method to call from the API mapping
        package_name = selected_api["package"]
        class_name = selected_api["class"]
        method_name = selected_api["method"]

        # Dynamically load the class and call the method
        handler_class = load_class(package_name, class_name)
        handler_instance = handler_class()
        context = {"request": event, "claims": claims} if 'claims' in locals() else {"request": event}
        response = call_method(handler_instance, method_name, context)

        # Return the response to the client
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
            "body": json.dumps(response),
        }

    except Exception as e:
        logging.error("Error processing request.", exc_info=True)
        return {
            "statusCode": 401,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
            },
            "body": json.dumps({"error": str(e)})
        }