from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    return FileResponse("static/index.html")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            await connection.send_json(data)


manager = ConnectionManager()


@app.post("/polls")
def create_poll(poll: schemas.PollCreate, db: Session = Depends(get_db)):
    db_poll = models.Poll(question=poll.question)
    db.add(db_poll)
    db.commit()
    db.refresh(db_poll)

    for opt in poll.options:
        db_option = models.Option(text=opt.text, poll_id=db_poll.id)
        db.add(db_option)

    db.commit()
    return {"message": "Poll created", "poll_id": db_poll.id}


@app.get("/polls/{poll_id}", response_model=schemas.PollBase)
def get_poll(poll_id: int, db: Session = Depends(get_db)):
    poll = db.query(models.Poll).filter(models.Poll.id == poll_id).first()
    return poll


@app.post("/vote")
async def vote(vote: schemas.Vote, db: Session = Depends(get_db)):

    new_option = (
        db.query(models.Option).filter(models.Option.id == vote.option_id).first()
    )

    if not new_option:
        return {"error": "Invalid option"}

    new_option.votes += 1

    if vote.previous_option_id:
        prev_option = (
            db.query(models.Option)
            .filter(models.Option.id == vote.previous_option_id)
            .first()
        )

        if prev_option and prev_option.votes > 0:
            prev_option.votes -= 1

    db.commit()

    await manager.broadcast(
        {"type": "update", "option_id": new_option.id, "votes": new_option.votes}
    )

    if vote.previous_option_id:
        await manager.broadcast(
            {
                "type": "update",
                "option_id": vote.previous_option_id,
                "votes": prev_option.votes,
            }
        )

    return {"message": "Vote updated"}


@app.get("/polls", response_model=list[schemas.PollBase])
def get_all_polls(db: Session = Depends(get_db)):
    return db.query(models.Poll).all()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
