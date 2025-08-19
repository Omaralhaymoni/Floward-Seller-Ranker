import os, sys

def main():

    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)

    from streamlit.web.cli import main as st_main
    sys.argv = [
        "streamlit", "run", "app.py",
        "--server.headless=true",
        "--browser.serverAddress=localhost",
        "--server.port=8501",
    ]
    st_main()

if __name__ == "__main__":
    main()
