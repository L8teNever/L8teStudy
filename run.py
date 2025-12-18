from app import create_app

app = create_app()

if __name__ == '__main__':
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
        s.close()
        print(f"\n * \033[92mOn Local Network: http://{IP}:5000\033[0m\n")
    except:
        pass
    app.run(debug=True, host='0.0.0.0', port=5000)
