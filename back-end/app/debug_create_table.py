from app.core.database import Base, engine
from app.models.users import User
from app.models.tickets import Ticket

print("Tables connues par SQLAlchemy :")
print(Base.metadata.tables.keys())

Base.metadata.create_all(bind=engine)
print("create_all() exécuté")
