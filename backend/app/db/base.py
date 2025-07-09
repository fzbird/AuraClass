from sqlalchemy.ext.declarative import declarative_base

# 创建基础模型类
Base = declarative_base()

# Import all models here to ensure they are registered with SQLAlchemy
# 仅导入确认存在的模型
from app.models.user import User  # noqa
from app.models.role import Role  # noqa
from app.models.student import Student  # noqa
from app.models.quant_item import QuantItem  # noqa
from app.models.quant_item_category import QuantItemCategory  # noqa
from app.models.quant_record import QuantRecord  # noqa
from app.models.notification import Notification  # noqa
from app.models.ai_conversation import AIConversation, AIMessage  # noqa
from app.models.uploads import Upload  # noqa
from app.models.classes import Classes  # noqa

