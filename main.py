from fastapi import FastAPI, Depends
from database import Base, engine, SessionLocal
from models.user import User
from models.repository import Repository
from models.file import File
from models.commit import Commit
from auth import hash_password, verify_password, create_token
from auth_middleware import get_current_user

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

Base.metadata.create_all(bind=engine)


# ---------------- USER AUTH ---------------- #

@app.post("/register")
def register(username: str, email: str, password: str):

    db = SessionLocal()

    hashed = hash_password(password)

    user = User(
        username=username,
        email=email,
        password=hashed
    )

    db.add(user)
    db.commit()

    return {"message": "user created"}


@app.post("/login")
def login(username: str, password: str):

    db = SessionLocal()

    user = db.query(User).filter(User.username == username).first()

    if not user:
        return {"message": "user not found"}

    if not verify_password(password, user.password):
        return {"message": "invalid password"}

    token = create_token({"user": user.username})

    return {"token": token}


# ---------------- REPOSITORIES ---------------- #

@app.post("/repository")
def create_repo(name: str, user: str = Depends(get_current_user)):

    db = SessionLocal()

    user_obj = db.query(User).filter(User.username == user).first()

    if not user_obj:
        return {"message": "user not found"}

    repo = Repository(
        name=name,
        owner_id=user_obj.id
    )

    db.add(repo)
    db.commit()

    return {"message": "repository created"}


@app.get("/my-repositories")
def get_repos(user: str = Depends(get_current_user)):

    db = SessionLocal()

    user_obj = db.query(User).filter(User.username == user).first()

    repos = db.query(Repository).filter(Repository.owner_id == user_obj.id).all()

    return repos


@app.get("/repository/{repo_id}")
def get_repo(repo_id: int):

    db = SessionLocal()

    repo = db.query(Repository).filter(Repository.id == repo_id).first()

    if not repo:
        return {"message": "repository not found"}

    return repo


@app.put("/repository/{repo_id}")
def update_repo(repo_id: int, name: str, user: str = Depends(get_current_user)):

    db = SessionLocal()

    repo = db.query(Repository).filter(Repository.id == repo_id).first()

    if not repo:
        return {"message": "repository not found"}

    repo.name = name
    db.commit()

    return {"message": "repository updated"}


@app.delete("/repository/{repo_id}")
def delete_repo(repo_id: int, user: str = Depends(get_current_user)):

    db = SessionLocal()

    repo = db.query(Repository).filter(Repository.id == repo_id).first()

    if not repo:
        return {"message": "repository not found"}

    db.delete(repo)
    db.commit()

    return {"message": "repository deleted"}


# ---------------- FILE SYSTEM ---------------- #

@app.post("/repositories/{repo_id}/files")
def add_file(repo_id: int, filename: str, code: str):

    db = SessionLocal()

    repo = db.query(Repository).filter(Repository.id == repo_id).first()

    if not repo:
        return {"message": "repository not found"}

    file = File(
        repository_id=repo_id,
        filename=filename,
        code_content=code
    )

    db.add(file)
    db.commit()

    return {"message": "file added"}

@app.get("/repositories/{repo_id}/files")
def get_files(repo_id: int):

    db = SessionLocal()

    files = db.query(File).filter(File.repository_id == repo_id).all()

    return files


# ---------------- COMMITS ---------------- #

@app.post("/repositories/{repo_id}/commit")
def create_commit(repo_id: int, message: str, user_id: int):

    db = SessionLocal()

    commit = Commit(
        repository_id=repo_id,
        message=message,
        author_id=user_id
    )

    db.add(commit)
    db.commit()

    return {"message": "commit created"}


@app.get("/repositories/{repo_id}/commits")
def get_commits(repo_id: int):

    db = SessionLocal()

    commits = db.query(Commit).filter(Commit.repository_id == repo_id).all()

    return commits


# ---------------- ROOT ---------------- #

@app.get("/")
def home():
    return {"message": "Backend running with database"}