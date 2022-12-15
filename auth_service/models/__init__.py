from .schemas import User
from .setup import SessionLocal, Base, engine, get_database

from internal import  hash_password
import json
import uuid as uuid_pkg

from decouple import config

# Setup default admin user
def setup_admin():
    """ Setup default admin user """
    
    db = next(get_database())
    
    # Check if admin user exists
    if db.query(User).filter(User.username == config("DEFAULT_ADMIN_USERNAME")).first() is not None:
        return      
    

    # Create admin user
    print("Creating default admin user")

    try:
        base_permissions = json.load(open(config("PATH_TO_BASE_PERMISSIONS"), "r"))
        base_permissions["is_admin"] = True
    except FileNotFoundError:
        raise FileNotFoundError(f"Base permissions file not found. Please create a file {config('PATH_TO_BASE_PERMISSIONS')} and try again.")
    except Exception as e:
        raise e
    
    hashed_password = hash_password(config("DEFAULT_ADMIN_PASSWORD"))
    uuid = uuid_pkg.uuid4()
    new_user = User(username=config("DEFAULT_ADMIN_USERNAME"), password=hashed_password, permissions=base_permissions, uuid=uuid)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
