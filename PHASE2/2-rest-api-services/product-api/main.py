""" Cisco M2S2 Demo 01: beginner Product CRUD API (in-memory storage).  """

from typing import Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from starlette.exceptions import HTTPException as StarletteHTTPException

from pydantic import BaseModel, Field 

app = FastAPI(
    title="Product API",
    version="1.0.0",
    description="Beginner CRUD API used in the Cisco AI Apprenticeship FastAPI lab.",
)

# Pydantic models
class ProductBase(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(ge=0)
    in_stock: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    price: Optional[float] = Field(default=None, ge=0)
    in_stock: Optional[bool] = None 


class Product(ProductBase):
    id: int


products: dict[int, Product] = {
    1: Product(id=1, name="Keyboard", price=30.0, in_stock=True),
    2: Product(id=2, name="Mouse", price=15.0, in_stock=True),
}
next_id = 3


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    code = "DEVICE_NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR"
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": code, "message": str(exc.detail), "status": exc.status_code}}
    )



# Implemment the home page
@app.get("/")
def home():
    return {"message": "API is running"}




# Implement the /products endpoint
@app.get("/products")
def list_products():
    return list(products.values())

# Implement the single product details endpoint
@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    product = products.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# Implement new product creation endpoint
@app.post("/products", status_code=status.HTTP_201_CREATED,response_model=Product )
def create_product( request_payload:  ProductCreate):
    global next_id
    product = Product(id=next_id, **request_payload.model_dump())
    products[next_id] = product
    next_id += 1
    return product

# Implement replace existing product endpoint
@app.put("/products/{product_id}", response_model=Product)
def replace_product(product_id: int, payload: ProductCreate):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    product = Product(id=product_id, **payload.model_dump())
    products[product_id] = product
    return product

# Implement updating existing product endpoint
@app.patch("/products/{product_id}", response_model=Product)
def update_product(product_id: int, payload: ProductUpdate):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = products.get(product_id)
    updates = payload.model_dump(exclude_unset=True)
    product = existing.model_copy(update=updates)

    # Validate the assembled product, including any explicitly supplied nulls.
    product = Product.model_validate(product.model_dump())
    products[product_id] = product
    return product



# Implement delete  product endpoint
@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    del products[product_id]

    return Response(status_code=status.HTTP_204_NO_CONTENT)


