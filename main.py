from fastapi import FastAPI, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
import database
import pandas as pd
from fastapi.responses import Response
import pandas as pd

# This commands SQLAlchemy to physically create the tables in PostgreSQL
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Data Processing API")

# A helper function to open and close the database connection safely
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/records")
def add_record(status: str, metric: float, db: Session = Depends(get_db)):
    """Allows users to actively modify the live database."""
    new_record = database.Record(status=status, metric=metric)
    db.add(new_record)
    db.commit()
    return {"message": "Database modified successfully"}


@app.get("/summary")
def generate_summary(db: Session = Depends(get_db)):
    """Processes the live database and returns a calculated summary."""
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
def download_clean_csv(db: Session = Depends(get_db)):
    """Formats the data into a cleaner CSV and initiates a browser download."""
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