from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
def health_check():
    """Check if API is running"""
    return {"status": "healthy"}
