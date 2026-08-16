from pydantic import BaseModel, Field

class RecordCreate(BaseModel):
    # The pattern ensures ONLY upper and lowercase letters are allowed
    status: str = Field(..., min_length=1, pattern="^[a-zA-Z]+$", description="The current status (letters only)")
    
    metric: float = Field(..., gt=0, description="The metric value, must be strictly positive")

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, description="Must be at least 3 characters")
    password: str = Field(..., min_length=6, description="Must be at least 6 characters")