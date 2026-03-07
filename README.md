
# AI Logistics Control Tower

## Backend

cd backend

python3 -m venv venv
source venv/bin/activate

pip install fastapi uvicorn

uvicorn backend.api.main:app --reload


## Frontend

cd frontend

npm install
npm install lucide-react

npm run dev
