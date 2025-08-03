from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    membership_type = Column(String, default="Standart")
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)

    messages = relationship("Message", back_populates="owner")
    # ... (diğer User sınıfı içeriği aynı kalacak)


class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship("Message", back_populates="chat")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=True)  # Yeni eklenen alan
    session_id = Column(String, nullable=True)  # AI chat oturumu için eski alan (kademeli kaldırılacak)
    user_input = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    stress_score = Column(Float, default=0.5) # YENİ EKLENEN SATIR

    owner = relationship("User", back_populates="messages")
    chat = relationship("Chat", back_populates="messages")
    # ... (diğer Message sınıfı içeriği aynı kalacak)

class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    is_group = Column(Integer, nullable=False)  # 0: false, 1: true
    members = relationship("ChatRoomMember", back_populates="room")
    messages = relationship("ChatMessage", back_populates="room")

class ChatRoomMember(Base):
    __tablename__ = "chat_room_members"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room = relationship("ChatRoom", back_populates="members")
    user = relationship("User")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User")

##durum güncelleme