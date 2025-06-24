#!/bin/bash

# Get the local IP address
IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

echo "Starting servers for mobile access..."
echo "Your local IP is: $IP"
echo ""

# Update frontend .env with current IP
sed -i '' "s|REACT_APP_API_BASE_URL=.*|REACT_APP_API_BASE_URL=http://$IP:8000/api|" frontend/.env

# Kill existing servers
echo "Stopping existing servers..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

# Start backend with CORS for both localhost and IP
echo "Starting backend on 0.0.0.0:8000..."
cd backend && FLASK_HOST=0.0.0.0 CORS_ORIGINS="http://localhost:3000,http://$IP:3000" python3 app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend on port 3000..."
cd ../frontend && npm start &
FRONTEND_PID=$!

echo ""
echo "Servers starting..."
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Access from mobile at: http://$IP:3000"
echo "Swipe products at: http://$IP:3000/products/swipe"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait and handle shutdown
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait