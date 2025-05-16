import logging
from app import create_app

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

logging.info("back start")

app = create_app()

if __name__ == "main":
    app.run(host="127.0.0.1", port=5000, debug=True)
