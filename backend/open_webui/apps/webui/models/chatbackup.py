import time
from typing import Optional
from sqlalchemy import Column, String, Text, JSON, BigInteger, Boolean
from open_webui.apps.webui.internal.db import Base, get_db, engine
from pydantic import BaseModel, ConfigDict

class ChatBackup(Base):
    __tablename__ = "chatbackup"
    # Add extend_existing=True to the table definition
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True)
    user_id = Column(String)
    title = Column(Text)
    chat = Column(JSON)
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)
    share_id = Column(Text, unique=True, nullable=True)
    archived = Column(Boolean, default=False)
    pinned = Column(Boolean, default=False, nullable=True)
    meta = Column(JSON, server_default="{}")
    folder_id = Column(Text, nullable=True)

class ChatBackupModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    chat: dict
    created_at: int
    updated_at: int
    share_id: Optional[str] = None
    archived: bool = False
    pinned: Optional[bool] = False
    meta: dict = {}
    folder_id: Optional[str] = None

def create_tables():
    Base.metadata.create_all(bind=engine)

create_tables()

class ChatBackupTable:
    def insert_chat_backup(self, chat_data: dict) -> Optional[ChatBackupModel]:
        with get_db() as db:
            backup = ChatBackupModel(**chat_data)
            result = ChatBackup(**backup.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            return ChatBackupModel.model_validate(result) if result else None

ChatBackups = ChatBackupTable()
