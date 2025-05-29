import truststore
from dotenv import load_dotenv

# Load environment variables.
# Recommended only during development.
load_dotenv()

# https://github.com/sethmlarson/truststore
# https://github.com/boto/boto3/issues/4061#issuecomment-2860045574
truststore.inject_into_ssl()
