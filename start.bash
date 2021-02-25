cd /home/pi/Documents/Projects/facial-recognition-visitor-notification-system;
python3 ./api/api.py &
python3 ./main.py &
nodejs ./web-app/app.js &
chromium-browser --start-fullscreen http://localhost:8080
