from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    # В production используйте production WSGI server
    # Например: gunicorn, uWSGI, waitress
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True  # Включаем многопоточность для обработки нескольких запросов
    )