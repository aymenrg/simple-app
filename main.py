from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import database
import pandas as pd
from fastapi.responses import Response
import pandas as pd
import schemas
from fastapi.responses import Response, FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from datetime import datetime, timedelta, timezone

# This commands SQLAlchemy to physically create the tables in PostgreSQL
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Data Processing API")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# The master key used to sign the VIP passes (Never share this in production!)
SECRET_KEY = "my_super_secret_development_key"
ALGORITHM = "HS256"

# This tells FastAPI where the login route is
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_token_from_cookie(request: Request):
    """Bouncer that extracts the JWT from the HTTP-Only cookie."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated. Please log in.")
    
    # Remove the 'Bearer ' prefix to get the raw token string
    return token.split(" ")[1] if "Bearer" in token else token

def get_password_hash(password: str):
    return pwd_context.hash(password)

# A helper function to open and close the database connection safely
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def serve_frontend():
    """Serves the visual HTML user interface to the web browser."""
    return FileResponse("index.html")

@app.get("/styles.css")
def serve_css():
    """Serves the responsive stylesheet."""
    return FileResponse("styles.css")

@app.get("/app.js")
def serve_js():
    """Serves the modular JavaScript logic."""
    return FileResponse("app.js")

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """Registers a new user and hashes their password."""
    
    # 1. Check if the username is already taken
    existing_user = db.query(database.User).filter(database.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 2. Mathematically scramble the password
    hashed_pwd = get_password_hash(user.password)
    
    # 3. Save the new user to PostgreSQL
    new_user = database.User(username=user.username, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    
    return {"message": f"User {user.username} created successfully"}

@app.post("/login")
def login(
    response: Response, 
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(database.get_db)
):
    """Authenticates a user and sets an HTTP-Only Cookie."""
    user = db.query(database.User).filter(database.User.username == form_data.username).first()
    
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    expire_time = datetime.now(timezone.utc) + timedelta(hours=1)
    token_data = {"sub": user.username, "exp": expire_time}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    # --- NEW SECURITY LOGIC ---
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,   # JavaScript cannot read this cookie
        secure=False,    # Set to True in production (requires HTTPS)
        samesite="lax",  # Protects against CSRF attacks
        max_age=3600     # Expires in 1 hour
    )
    
    return {"message": "Successfully logged in and cookie set"}

@app.post("/records", status_code=status.HTTP_201_CREATED)
def create_record(
    record: schemas.RecordCreate, 
    db: Session = Depends(database.get_db),
    token: str = Depends(get_token_from_cookie) # <-- THE NEW LOCK
):
    """Injects data into the database (Requires Cookie JWT)"""
    new_record = database.Record(status=record.status, metric=record.metric)
    db.add(new_record)
    db.commit()
    return {"message": "Record successfully added"}


@app.get("/summary")
def generate_summary(
    db: Session = Depends(get_db),
    token: str = Depends(get_token_from_cookie) # <-- ADD THE LOCK HERE
):
    records = db.query(database.Record).all()
    
    if not records:
        return {"message": "Database is empty."}
        
    # Load the data into a Pandas DataFrame for easy math
    df = pd.DataFrame([{"status": r.status, "metric": r.metric} for r in records])
    
    return {
        "status": "success",
        "total_records": len(df),
        "total_metric_sum": float(df["metric"].sum()),
        "average_metric": float(df["metric"].mean())
    }

@app.get("/export")
def download_clean_csv(
    db: Session = Depends(get_db),
    token: str = Depends(get_token_from_cookie) # <-- ADD THE LOCK HERE
):
    records = db.query(database.Record).all()
    
    if not records:
        return {"message": "No data to export."}
    
    # Format the data into clean, presentable columns
    df = pd.DataFrame([{
        "Record ID": r.id, 
        "Current Status": r.status.capitalize(), 
        "Metric Value": r.metric
    } for r in records])
    
    # Convert the DataFrame to a clean CSV string without the index numbers
    csv_data = df.to_csv(index=False)
    
    # Force the user's web browser to download it as a file named "clean_data.csv"
    return Response(
        content=csv_data, 
        media_type="text/csv", 
        headers={"Content-Disposition": 'attachment; filename="clean_data.csv"'}
    )