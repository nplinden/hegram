from hegram.occurences import occurences
from hegram.definitions import definitions
from hegram.app import app
import sys

if __name__ == '__main__':
    if len(sys.argv) == 1:
        app.run_server(debug=True, port=7777, dev_tools_hot_reload=True)