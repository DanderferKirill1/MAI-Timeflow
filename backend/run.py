from app import create_app

app = create_app()

# все пути переписаны в routes, приложение создается в __init__.py

if __name__ == "__main__":
    app.run(debug=True)
