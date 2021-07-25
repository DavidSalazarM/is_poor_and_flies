from fastapi import FastAPI, File, UploadFile, status, HTTPException
import shutil
import glob, os
from models import Music
from database import SessionLocal, engine
import eyed3
from starlette.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
path_mp3 = "/home/david/IsPoorAndFlies/mp3/"

origins = [
    "http://127.0.0.1:8000/songs/",
    "http://localhost:3000",
]

@app.post("/uploadfile/", status_code=status.HTTP_201_CREATED)
def create_upload_file(file: UploadFile = File(...)):
    os.chdir(path_mp3)
    buffer = open(file.filename, "wb") 
    shutil.copyfileobj(file.file, buffer)
    audio=eyed3.load((file.filename))
    def value():
        try:
            year = audio.tag.getBestDate()._year
            return year
        except AttributeError:
            return None

    with SessionLocal() as db: 
        music = Music(
            song = file.filename,
            title = audio.tag.title,
            artist = audio.tag.artist,
            album = audio.tag.album,
            year = value()
            )
        db.add(music)
        db.commit()
        db.refresh(music)

    return music


@app.get("/songs/", status_code=200)
def read_songs():
    with SessionLocal() as db:
        music = db.query(Music).all()
    return music


@app.get("/song/{song_id}", status_code=200)
def read_song(song_id: int):
    with SessionLocal() as db:
        song = db.query(Music).filter(Music.id == song_id).one()
        if song is None:
            raise HTTPException(status_code=404, detail="music not found")
        return song


@app.get("/song/{song_id}/file", status_code=200)
def read_song(song_id: int):
    with SessionLocal() as db:
        song = db.query(Music).filter(Music.id == song_id).one()
        if song is None:
            raise HTTPException(status_code=404, detail="music not found")
        return FileResponse(path=path_mp3 + song.song, 
        media_type='application/octet-stream',
        filename=song.song)


@app.post("/song/{song_id}/like", status_code=200)
def like_a_song(song_id: int):
    with SessionLocal() as db:
        song = db.query(Music).filter(Music.id == song_id).one()
        if song is None:
            raise HTTPException(status_code=404, detail="music not found")
        else:
            song.liked = not song.liked
            db.add(song)
            db.commit()
            db.refresh(song)
            return song
       
 
        

    


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StorgePrevioler:
    def __init__(self,direccion):
        self.direccion = direccion


    def get_files(self):
        os.chdir(self.direccion)
        files_path = [x for x in glob.glob("*.mp3")]
        return files_path

       

if __name__ == "__main__":
    
    algo = StorgePrevioler("/home/david/Música")  
    print(algo.get_files())
  


