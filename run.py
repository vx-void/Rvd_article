from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    # В самом конце run.py, перед запуском
    print("\n=== Зарегистрированные маршруты ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:30} {rule.methods} → {rule.rule}")
    print("==================================\n")