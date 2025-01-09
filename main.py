from hegram.app import app
import sys

if __name__ == "__main__":
    app.run_server(debug=True, port=7777, dev_tools_hot_reload=True)
