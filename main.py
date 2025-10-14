from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, date

app = FastAPI(title="Hierarchical Data Explorer API")

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")

# Data structure
DATA_DIR = "data"

def load_json_file(filename: str) -> List[Dict]:
    """Load data from JSON file"""
    try:
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_json_file(filename: str, data: List[Dict]) -> bool:
    """Save data to JSON file"""
    try:
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False

def get_next_id(data: List[Dict]) -> int:
    """Get next available ID"""
    if not data:
        return 1
    return max(item["id"] for item in data) + 1

# Pydantic models for request validation
class CustomerCreate(BaseModel):
    name: str
    industry: str
    status: str
    created_date: str

class ProjectCreate(BaseModel):
    name: str
    budget: float
    status: str
    start_date: str
    customer_id: int

class QuoteCreate(BaseModel):
    name: str
    amount: float
    status: str
    valid_until: str
    project_id: int

class FreightRequestCreate(BaseModel):
    name: str
    vendor_id: int
    status: str
    weight: float
    priority: str
    estimated_delivery: str
    quote_id: int

# Update models for editing existing items
class CustomerUpdate(BaseModel):
    name: Optional[str]
    industry: Optional[str]
    status: Optional[str]

class ProjectUpdate(BaseModel):
    name: Optional[str]
    budget: Optional[float]
    status: Optional[str]
    start_date: Optional[str]

class QuoteUpdate(BaseModel):
    name: Optional[str]
    amount: Optional[float]
    status: Optional[str]
    valid_until: Optional[str]

class FreightRequestUpdate(BaseModel):
    name: Optional[str]
    vendor_id: Optional[int]
    status: Optional[str]
    weight: Optional[float]
    priority: Optional[str]
    estimated_delivery: Optional[str]

# API Endpoints
@app.get("/api/customers")
async def get_customers():
    """Get all customers (excluding deleted)"""
    customers = load_json_file("customers.json")
    return [c for c in customers if not c.get("is_deleted", False)]

@app.get("/api/projects/{customer_id}")
async def get_projects(customer_id: int):
    """Get projects for a specific customer (excluding deleted)"""
    projects = load_json_file("projects.json")
    return [p for p in projects if p["customer_id"] == customer_id and not p.get("is_deleted", False)]

@app.get("/api/quotes/{project_id}")
async def get_quotes(project_id: int):
    """Get quotes for a specific project (excluding deleted)"""
    quotes = load_json_file("quotes.json")
    return [q for q in quotes if q["project_id"] == project_id and not q.get("is_deleted", False)]

@app.get("/api/freight-requests/{quote_id}")
async def get_freight_requests(quote_id: int):
    """Get freight requests for a specific quote (excluding deleted)"""
    freight_requests = load_json_file("freight_requests.json")
    vendors = load_json_file("vendors.json")

    # Enrich with vendor names
    vendor_map = {v["id"]: v["name"] for v in vendors}

    result = []
    for fr in freight_requests:
        if fr["quote_id"] == quote_id and not fr.get("is_deleted", False):
            fr_copy = fr.copy()
            fr_copy["vendor_name"] = vendor_map.get(fr["vendor_id"], "Unknown Vendor")
            result.append(fr_copy)

    return result

@app.get("/api/vendors")
async def get_vendors():
    """Get all vendors"""
    return load_json_file("vendors.json")

# POST endpoints for CRUD operations
@app.post("/api/customers", response_model=Dict[str, Any])
async def create_customer(customer: CustomerCreate):
    """Create a new customer"""
    try:
        customers = load_json_file("customers.json")

        # Validate required fields
        if not customer.name.strip():
            raise HTTPException(status_code=400, detail="Customer name is required")

        # Create new customer
        new_customer = {
            "id": get_next_id(customers),
            "name": customer.name.strip(),
            "industry": customer.industry,
            "status": customer.status,
            "created_date": customer.created_date
        }

        customers.append(new_customer)

        if save_json_file("customers.json", customers):
            return {"success": True, "data": new_customer}
        else:
            raise HTTPException(status_code=500, detail="Failed to save customer")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/projects", response_model=Dict[str, Any])
async def create_project(project: ProjectCreate):
    """Create a new project"""
    try:
        # Validate customer exists
        customers = load_json_file("customers.json")
        customer_exists = any(c["id"] == project.customer_id for c in customers)
        if not customer_exists:
            raise HTTPException(status_code=400, detail="Customer not found")

        projects = load_json_file("projects.json")

        # Validate required fields
        if not project.name.strip():
            raise HTTPException(status_code=400, detail="Project name is required")

        # Create new project
        new_project = {
            "id": get_next_id(projects),
            "name": project.name.strip(),
            "budget": project.budget,
            "status": project.status,
            "start_date": project.start_date,
            "customer_id": project.customer_id
        }

        projects.append(new_project)

        if save_json_file("projects.json", projects):
            return {"success": True, "data": new_project}
        else:
            raise HTTPException(status_code=500, detail="Failed to save project")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/quotes", response_model=Dict[str, Any])
async def create_quote(quote: QuoteCreate):
    """Create a new quote"""
    try:
        # Validate project exists
        projects = load_json_file("projects.json")
        project_exists = any(p["id"] == quote.project_id for p in projects)
        if not project_exists:
            raise HTTPException(status_code=400, detail="Project not found")

        quotes = load_json_file("quotes.json")

        # Validate required fields
        if not quote.name.strip():
            raise HTTPException(status_code=400, detail="Quote name is required")

        # Create new quote
        new_quote = {
            "id": get_next_id(quotes),
            "name": quote.name.strip(),
            "amount": quote.amount,
            "status": quote.status,
            "valid_until": quote.valid_until,
            "project_id": quote.project_id
        }

        quotes.append(new_quote)

        if save_json_file("quotes.json", quotes):
            return {"success": True, "data": new_quote}
        else:
            raise HTTPException(status_code=500, detail="Failed to save quote")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/freight-requests", response_model=Dict[str, Any])
async def create_freight_request(freight_request: FreightRequestCreate):
    """Create a new freight request"""
    try:
        # Validate quote exists
        quotes = load_json_file("quotes.json")
        quote_exists = any(q["id"] == freight_request.quote_id for q in quotes)
        if not quote_exists:
            raise HTTPException(status_code=400, detail="Quote not found")

        # Validate vendor exists
        vendors = load_json_file("vendors.json")
        vendor_exists = any(v["id"] == freight_request.vendor_id for v in vendors)
        if not vendor_exists:
            raise HTTPException(status_code=400, detail="Vendor not found")

        freight_requests = load_json_file("freight_requests.json")

        # Validate required fields
        if not freight_request.name.strip():
            raise HTTPException(status_code=400, detail="Freight request name is required")

        # Create new freight request
        new_freight_request = {
            "id": get_next_id(freight_requests),
            "name": freight_request.name.strip(),
            "vendor_id": freight_request.vendor_id,
            "status": freight_request.status,
            "weight": freight_request.weight,
            "priority": freight_request.priority,
            "estimated_delivery": freight_request.estimated_delivery,
            "quote_id": freight_request.quote_id
        }

        freight_requests.append(new_freight_request)

        if save_json_file("freight_requests.json", freight_requests):
            return {"success": True, "data": new_freight_request}
        else:
            raise HTTPException(status_code=500, detail="Failed to save freight request")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# PUT endpoints for updates
@app.put("/api/customers/{customer_id}", response_model=Dict[str, Any])
async def update_customer(customer_id: int, customer: CustomerUpdate):
    """Update an existing customer"""
    try:
        customers = load_json_file("customers.json")

        # Find customer index
        customer_index = -1
        for i, c in enumerate(customers):
            if c["id"] == customer_id and not c.get("is_deleted", False):
                customer_index = i
                break

        if customer_index == -1:
            raise HTTPException(status_code=404, detail="Customer not found")

        # Update customer fields (only update provided fields)
        updated_customer = customers[customer_index].copy()
        if customer.name is not None:
            if not customer.name.strip():
                raise HTTPException(status_code=400, detail="Customer name cannot be empty")
            updated_customer["name"] = customer.name.strip()
        if customer.industry is not None:
            updated_customer["industry"] = customer.industry
        if customer.status is not None:
            updated_customer["status"] = customer.status

        customers[customer_index] = updated_customer

        if save_json_file("customers.json", customers):
            return {"success": True, "data": updated_customer}
        else:
            raise HTTPException(status_code=500, detail="Failed to update customer")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.put("/api/projects/{project_id}", response_model=Dict[str, Any])
async def update_project(project_id: int, project: ProjectUpdate):
    """Update an existing project"""
    try:
        projects = load_json_file("projects.json")

        # Find project index
        project_index = -1
        for i, p in enumerate(projects):
            if p["id"] == project_id and not p.get("is_deleted", False):
                project_index = i
                break

        if project_index == -1:
            raise HTTPException(status_code=404, detail="Project not found")

        # Update project fields
        updated_project = projects[project_index].copy()
        if project.name is not None:
            if not project.name.strip():
                raise HTTPException(status_code=400, detail="Project name cannot be empty")
            updated_project["name"] = project.name.strip()
        if project.budget is not None:
            if project.budget < 0:
                raise HTTPException(status_code=400, detail="Budget cannot be negative")
            updated_project["budget"] = project.budget
        if project.status is not None:
            updated_project["status"] = project.status
        if project.start_date is not None:
            updated_project["start_date"] = project.start_date

        projects[project_index] = updated_project

        if save_json_file("projects.json", projects):
            return {"success": True, "data": updated_project}
        else:
            raise HTTPException(status_code=500, detail="Failed to update project")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.put("/api/quotes/{quote_id}", response_model=Dict[str, Any])
async def update_quote(quote_id: int, quote: QuoteUpdate):
    """Update an existing quote"""
    try:
        quotes = load_json_file("quotes.json")

        # Find quote index
        quote_index = -1
        for i, q in enumerate(quotes):
            if q["id"] == quote_id and not q.get("is_deleted", False):
                quote_index = i
                break

        if quote_index == -1:
            raise HTTPException(status_code=404, detail="Quote not found")

        # Update quote fields
        updated_quote = quotes[quote_index].copy()
        if quote.name is not None:
            if not quote.name.strip():
                raise HTTPException(status_code=400, detail="Quote name cannot be empty")
            updated_quote["name"] = quote.name.strip()
        if quote.amount is not None:
            if quote.amount < 0:
                raise HTTPException(status_code=400, detail="Amount cannot be negative")
            updated_quote["amount"] = quote.amount
        if quote.status is not None:
            updated_quote["status"] = quote.status
        if quote.valid_until is not None:
            updated_quote["valid_until"] = quote.valid_until

        quotes[quote_index] = updated_quote

        if save_json_file("quotes.json", quotes):
            return {"success": True, "data": updated_quote}
        else:
            raise HTTPException(status_code=500, detail="Failed to update quote")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.put("/api/freight-requests/{freight_request_id}", response_model=Dict[str, Any])
async def update_freight_request(freight_request_id: int, freight_request: FreightRequestUpdate):
    """Update an existing freight request"""
    try:
        freight_requests = load_json_file("freight_requests.json")

        # Find freight request index
        fr_index = -1
        for i, fr in enumerate(freight_requests):
            if fr["id"] == freight_request_id and not fr.get("is_deleted", False):
                fr_index = i
                break

        if fr_index == -1:
            raise HTTPException(status_code=404, detail="Freight request not found")

        # Validate vendor if provided
        if freight_request.vendor_id is not None:
            vendors = load_json_file("vendors.json")
            vendor_exists = any(v["id"] == freight_request.vendor_id for v in vendors)
            if not vendor_exists:
                raise HTTPException(status_code=400, detail="Vendor not found")

        # Update freight request fields
        updated_fr = freight_requests[fr_index].copy()
        if freight_request.name is not None:
            if not freight_request.name.strip():
                raise HTTPException(status_code=400, detail="Freight request name cannot be empty")
            updated_fr["name"] = freight_request.name.strip()
        if freight_request.vendor_id is not None:
            updated_fr["vendor_id"] = freight_request.vendor_id
        if freight_request.status is not None:
            updated_fr["status"] = freight_request.status
        if freight_request.weight is not None:
            if freight_request.weight < 0:
                raise HTTPException(status_code=400, detail="Weight cannot be negative")
            updated_fr["weight"] = freight_request.weight
        if freight_request.priority is not None:
            updated_fr["priority"] = freight_request.priority
        if freight_request.estimated_delivery is not None:
            updated_fr["estimated_delivery"] = freight_request.estimated_delivery

        freight_requests[fr_index] = updated_fr

        if save_json_file("freight_requests.json", freight_requests):
            return {"success": True, "data": updated_fr}
        else:
            raise HTTPException(status_code=500, detail="Failed to update freight request")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# DELETE endpoints for soft delete with cascade
@app.delete("/api/customers/{customer_id}", response_model=Dict[str, Any])
async def delete_customer(customer_id: int):
    """Soft delete a customer and cascade to all child items"""
    try:
        customers = load_json_file("customers.json")
        projects = load_json_file("projects.json")
        quotes = load_json_file("quotes.json")
        freight_requests = load_json_file("freight_requests.json")

        # Find and mark customer as deleted
        customer_found = False
        for c in customers:
            if c["id"] == customer_id and not c.get("is_deleted", False):
                c["is_deleted"] = True
                c["deleted_at"] = datetime.now().isoformat()
                customer_found = True
                break

        if not customer_found:
            raise HTTPException(status_code=404, detail="Customer not found")

        # Cascade delete to projects
        for p in projects:
            if p["customer_id"] == customer_id and not p.get("is_deleted", False):
                p["is_deleted"] = True
                p["deleted_at"] = datetime.now().isoformat()

        # Cascade delete to quotes
        for q in quotes:
            project_ids = [p["id"] for p in projects if p["customer_id"] == customer_id]
            if q["project_id"] in project_ids and not q.get("is_deleted", False):
                q["is_deleted"] = True
                q["deleted_at"] = datetime.now().isoformat()

        # Cascade delete to freight requests
        for fr in freight_requests:
            quote_ids = [q["id"] for q in quotes if any(p["customer_id"] == customer_id for p in projects if p["id"] == q["project_id"])]
            if fr["quote_id"] in quote_ids and not fr.get("is_deleted", False):
                fr["is_deleted"] = True
                fr["deleted_at"] = datetime.now().isoformat()

        # Save all files
        success = (
            save_json_file("customers.json", customers) and
            save_json_file("projects.json", projects) and
            save_json_file("quotes.json", quotes) and
            save_json_file("freight_requests.json", freight_requests)
        )

        if success:
            return {"success": True, "message": "Customer and all related items deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete customer")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/api/projects/{project_id}", response_model=Dict[str, Any])
async def delete_project(project_id: int):
    """Soft delete a project and cascade to all child items"""
    try:
        projects = load_json_file("projects.json")
        quotes = load_json_file("quotes.json")
        freight_requests = load_json_file("freight_requests.json")

        # Find and mark project as deleted
        project_found = False
        for p in projects:
            if p["id"] == project_id and not p.get("is_deleted", False):
                p["is_deleted"] = True
                p["deleted_at"] = datetime.now().isoformat()
                project_found = True
                break

        if not project_found:
            raise HTTPException(status_code=404, detail="Project not found")

        # Cascade delete to quotes
        for q in quotes:
            if q["project_id"] == project_id and not q.get("is_deleted", False):
                q["is_deleted"] = True
                q["deleted_at"] = datetime.now().isoformat()

        # Cascade delete to freight requests
        for fr in freight_requests:
            quote_ids = [q["id"] for q in quotes if q["project_id"] == project_id]
            if fr["quote_id"] in quote_ids and not fr.get("is_deleted", False):
                fr["is_deleted"] = True
                fr["deleted_at"] = datetime.now().isoformat()

        # Save all files
        success = (
            save_json_file("projects.json", projects) and
            save_json_file("quotes.json", quotes) and
            save_json_file("freight_requests.json", freight_requests)
        )

        if success:
            return {"success": True, "message": "Project and all related items deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete project")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/api/quotes/{quote_id}", response_model=Dict[str, Any])
async def delete_quote(quote_id: int):
    """Soft delete a quote and cascade to all child items"""
    try:
        quotes = load_json_file("quotes.json")
        freight_requests = load_json_file("freight_requests.json")

        # Find and mark quote as deleted
        quote_found = False
        for q in quotes:
            if q["id"] == quote_id and not q.get("is_deleted", False):
                q["is_deleted"] = True
                q["deleted_at"] = datetime.now().isoformat()
                quote_found = True
                break

        if not quote_found:
            raise HTTPException(status_code=404, detail="Quote not found")

        # Cascade delete to freight requests
        for fr in freight_requests:
            if fr["quote_id"] == quote_id and not fr.get("is_deleted", False):
                fr["is_deleted"] = True
                fr["deleted_at"] = datetime.now().isoformat()

        # Save all files
        success = (
            save_json_file("quotes.json", quotes) and
            save_json_file("freight_requests.json", freight_requests)
        )

        if success:
            return {"success": True, "message": "Quote and all related items deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete quote")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/api/freight-requests/{freight_request_id}", response_model=Dict[str, Any])
async def delete_freight_request(freight_request_id: int):
    """Soft delete a freight request"""
    try:
        freight_requests = load_json_file("freight_requests.json")

        # Find and mark freight request as deleted
        fr_found = False
        for fr in freight_requests:
            if fr["id"] == freight_request_id and not fr.get("is_deleted", False):
                fr["is_deleted"] = True
                fr["deleted_at"] = datetime.now().isoformat()
                fr_found = True
                break

        if not fr_found:
            raise HTTPException(status_code=404, detail="Freight request not found")

        if save_json_file("freight_requests.json", freight_requests):
            return {"success": True, "message": "Freight request deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete freight request")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main HTML page"""
    try:
        with open("index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error: index.html not found</h1>", 404

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)