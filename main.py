from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

app = FastAPI()

# Инициализация базы данных SQLite и SQLAlchemy
SQLALCHEMY_DATABASE_URL = "sqlite:///./items.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель базы данных
class ItemModel(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Создание таблицы
Base.metadata.create_all(bind=engine)

# Pydantic-схемы для валидации входящих данных
class ItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: float

class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None

class ItemResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    created_at: datetime

    class Config:
        from_attributes = True 



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD операции
def get_item_create(name: str, price: float, description: str = None) -> ItemCreate:
    return ItemCreate(name=name, description=description, price=price)

def get_item_update(
    name: str | None = None,
    price: float | None = None,
    description: str | None = None
) -> ItemUpdate:
    return ItemUpdate(name=name, description=description, price=price)

# 1. Создание нового Item
@app.post("/items/", response_model=ItemResponse)
def create_item(item: ItemCreate = Depends(get_item_create), db: Session = Depends(get_db)):
    db_item = ItemModel(name=item.name, description=item.description, price=item.price)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# 2. Получение списка всех Item
@app.get("/items/", response_model=list[ItemResponse])
def read_items(db: Session = Depends(get_db)):
    items = db.query(ItemModel).all()
    return items

# 3. Получение отдельного Item по ID
@app.get("/items/{item_id}", response_model=ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# 4. Обновление существующего Item
@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item( item_id: int, item: ItemUpdate = Depends(get_item_update), db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if item.name is not None:
        db_item.name = item.name
    if item.description is not None:
        db_item.description = item.description
    if item.price is not None:
        db_item.price = item.price

    db.commit()
    db.refresh(db_item)
    return db_item

# 5. Удаление Item
@app.delete("/items/{item_id}", response_model=ItemResponse)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return db_item
