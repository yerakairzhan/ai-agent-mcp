from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime
import os

# Database URL - use environment variable in Docker
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./products.db")

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class Product(Base):
    """Product model"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    in_stock = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with orders
    orders = relationship("Order", back_populates="product")


class Order(Base):
    """Order model"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with product
    product = relationship("Product", back_populates="orders")


def init_db():
    """Initialize database and create tables"""
    print(f"🔧 Initializing database at: {DATABASE_URL}")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_initial_data():
    """Seed initial product data"""
    db = SessionLocal()

    try:
        # Check if products already exist
        existing = db.query(Product).first()
        if existing:
            print("ℹ️  Database already seeded")
            db.close()
            return

        # Create initial products
        products = [
            Product(
                name="Gaming Laptop",
                price=1299.99,
                category="Electronics",
                in_stock=True
            ),
            Product(
                name="Wireless Mouse",
                price=49.99,
                category="Electronics",
                in_stock=True
            ),
            Product(
                name="Mechanical Keyboard",
                price=129.99,
                category="Electronics",
                in_stock=True
            ),
            Product(
                name="4K Monitor",
                price=399.99,
                category="Electronics",
                in_stock=True
            ),
            Product(
                name="USB-C Hub",
                price=69.99,
                category="Accessories",
                in_stock=False
            )
        ]

        db.add_all(products)
        db.commit()
        print("✅ Database seeded with initial products")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    seed_initial_data()