# from fastapi import FastAPI, File, UploadFile, HTTPException
# from pydantic import BaseModel
# import json
# import os
# import shutil
# # import google.generativeai as genai
# from ortools.linear_solver import pywraplp
# from fastapi.middleware.cors import CORSMiddleware
# import re




# from groq import Groq
# import base64


# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# # Configure Gemini once at startup


# # genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# DB_FILE = "data.json"

# def initialize_db():
#     if not os.path.exists(DB_FILE):
#         json.dump({"expenses": [], "monthly_budget": 3000.0, "days_in_month": 30}, open(DB_FILE, "w"))

# initialize_db()

# def load_db(): return json.load(open(DB_FILE, "r"))
# def save_db(data): json.dump(data, open(DB_FILE, "w"))

# class Expense(BaseModel):
#     item: str
#     amount: float
#     category: str

# class BudgetUpdate(BaseModel):
#     budget: float

# @app.post("/manual-entry")
# def manual_entry(expense: Expense):
#     data = load_db()
#     data["expenses"].append(expense.model_dump())
#     save_db(data)
#     return {"status": "success"}

# @app.post("/update-budget")
# def update_budget(budget_data: BudgetUpdate):
#     data = load_db()
#     data["monthly_budget"] = budget_data.budget
#     save_db(data)
#     return {"status": "success"}

# @app.post("/reset-all")
# def reset_all():
#     data = {"expenses": [], "monthly_budget": 3000.0, "days_in_month": 30}
#     save_db(data)
#     return {"status": "success"}


# @app.post("/process-receipt")
# async def process_receipt(file: UploadFile = File(...)):
#     file_location = f"temp_{file.filename}"

#     with open(file_location, "wb+") as f:
#         shutil.copyfileobj(file.file, f)

#     try:
#         with open(file_location, "rb") as image_file:
#             image_data = base64.b64encode(image_file.read()).decode("utf-8")

#         ext = file.filename.split(".")[-1].lower()
#         media_type = "image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext}"

#         client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
#         response = client.chat.completions.create(
#             model="meta-llama/llama-4-scout-17b-16e-instruct",
#             messages=[
#                 {
#                     "role": "user",
#                     "content": [
#                         {
#                             "type": "image_url",
#                             "image_url": {"url": f"data:{media_type};base64,{image_data}"}
#                         },
#                         {
#                             "type": "text",
#                             # "text": 'Analyze this receipt. Extract main purchase name, total amount as float, and categorize. Return ONLY JSON: {"item": "Name", "amount": 0.00, "category": "Type"}'
#                             "text": 'Analyze this receipt. Extract ALL individual line items with their prices. Return ONLY a JSON array. If category is visible use it, otherwise use "General". Do NOT include totals, taxes, or subtotals. Format: [{"item": "Name", "amount": 0.00, "category": "Type"}, ...]'
#                         }
#                     ]
#                 }
#             ],
#             max_tokens=200
#         )
#         raw = response.choices[0].message.content

#         # Match array [...] instead of single object {...}
#         json_match = re.search(r'\[.*\]', raw, re.DOTALL)
#         parsed_items = json.loads(json_match.group())

#         # Ensure every item has required fields
#         data = load_db()
#         for item in parsed_items:
#             if "category" not in item or not item["category"]:
#                 item["category"] = "General"
#             if "item" not in item or not item["item"]:
#                 continue  # skip broken entries
#             if "amount" not in item or item["amount"] is None:
#                 continue  # skip items with no price
#             data["expenses"].append(item)

#         save_db(data)

#         return {"status": "success", "extracted": parsed_items, "count": len(parsed_items)}
    

#         # raw = response.choices[0].message.content
#         # json_match = re.search(r'\{.*\}', raw, re.DOTALL)
#         # parsed_data = json.loads(json_match.group())

#         # data = load_db()
#         # data["expenses"].append(parsed_data)
#         # save_db(data)

#         # return {"status": "success", "extracted": parsed_data}



        

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

#     finally:
#         if os.path.exists(file_location):
#             os.remove(file_location)

# # @app.post("/process-receipt")
# # async def process_receipt(file: UploadFile = File(...)):
# #     file_location = f"temp_{file.filename}"

# #     with open(file_location, "wb+") as f:
# #         shutil.copyfileobj(file.file, f)

# #     try:
# #         model = genai.GenerativeModel('gemini-1.5-flash')
# #         sample_file = genai.upload_file(path=file_location)

# #         prompt = 'Analyze this receipt. Extract main purchase name, total amount as float, and categorize. Return ONLY JSON: {"item": "Name", "amount": 0.00, "category": "Type"}'
# #         response = model.generate_content([prompt, sample_file])

# #         json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
# #         parsed_data = json.loads(json_match.group())

# #         data = load_db()
# #         data["expenses"].append(parsed_data)
# #         save_db(data)

# #         return {"status": "success", "extracted": parsed_data}

# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=str(e))

# #     finally:
# #         if os.path.exists(file_location):
# #             os.remove(file_location)

# @app.get("/optimize")
# def optimize_budget():
#     data = load_db()
#     total_spent = sum(e["amount"] for e in data["expenses"])
#     remaining_budget = data["monthly_budget"] - total_spent
#     days_left = data["days_in_month"]

#     history = list(reversed(data["expenses"]))[:1000]

#     response_data = {
#         "total_spent": total_spent,
#         "monthly_budget": data["monthly_budget"],
#         "remaining_budget": remaining_budget,
#         "history": history
#     }

#     if remaining_budget <= 0:
#         response_data["optimized_daily_limit"] = 0.0
#         response_data["status"] = "OVER_BUDGET"
#         return response_data

#     solver = pywraplp.Solver.CreateSolver('GLOP')
#     daily_spend = solver.NumVar(0, remaining_budget, 'daily_spend')
#     solver.Add(daily_spend * days_left <= remaining_budget)
#     solver.Maximize(daily_spend)
#     status = solver.Solve()

#     if status == pywraplp.Solver.OPTIMAL:
#         response_data["optimized_daily_limit"] = daily_spend.solution_value()
#         response_data["status"] = "OK"
#         return response_data

#     return {"error": "Could not optimize"}












# from fastapi import FastAPI, File, UploadFile, HTTPException
# from pydantic import BaseModel
# import json
# import os
# import shutil
# from groq import Groq
# import base64
# from ortools.linear_solver import pywraplp
# from fastapi.middleware.cors import CORSMiddleware
# import re
# from datetime import datetime
# from collections import defaultdict
# from typing import Optional

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# DB_FILE = "data.json"

# def initialize_db():
#     if not os.path.exists(DB_FILE):
#         json.dump({"expenses": [], "monthly_budget": 3000.0, "days_in_month": 30}, open(DB_FILE, "w"))

# initialize_db()

# def load_db(): return json.load(open(DB_FILE, "r"))
# def save_db(data): json.dump(data, open(DB_FILE, "w"))

# # Works with both old flat format AND new grouped format
# def get_expense_total(expense):
#     if "total" in expense:
#         return expense["total"]
#     elif "items" in expense:
#         return sum(i["amount"] for i in expense["items"])
#     else:
#         return expense.get("amount", 0)

# class Expense(BaseModel):
#     item: str
#     amount: float
#     category: str
#     date: Optional[str] = None
#     shop: Optional[str] = "Manual Entry"

# class BudgetUpdate(BaseModel):
#     budget: float

# @app.post("/manual-entry")
# def manual_entry(expense: Expense):
#     data = load_db()
#     entry = {
#         "type": "manual",
#         "shop": expense.shop or "Manual Entry",
#         "date": expense.date or datetime.now().strftime("%Y-%m-%d"),
#         "total": expense.amount,
#         "items": [{"item": expense.item, "amount": expense.amount, "category": expense.category}]
#     }
#     data["expenses"].append(entry)
#     save_db(data)
#     return {"status": "success"}

# @app.post("/update-budget")
# def update_budget(budget_data: BudgetUpdate):
#     data = load_db()
#     data["monthly_budget"] = budget_data.budget
#     save_db(data)
#     return {"status": "success"}

# @app.post("/reset-all")
# def reset_all():
#     data = {"expenses": [], "monthly_budget": 3000.0, "days_in_month": 30}
#     save_db(data)
#     return {"status": "success"}

# @app.post("/process-receipt")
# async def process_receipt(file: UploadFile = File(...)):
#     file_location = f"temp_{file.filename}"

#     with open(file_location, "wb+") as f:
#         shutil.copyfileobj(file.file, f)

#     try:
#         with open(file_location, "rb") as image_file:
#             image_data = base64.b64encode(image_file.read()).decode("utf-8")

#         ext = file.filename.split(".")[-1].lower()
#         media_type = "image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext}"

#         client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
#         response = client.chat.completions.create(
#             model="meta-llama/llama-4-scout-17b-16e-instruct",
#             messages=[
#                 {
#                     "role": "user",
#                     "content": [
#                         {
#                             "type": "image_url",
#                             "image_url": {"url": f"data:{media_type};base64,{image_data}"}
#                         },
#                         {
#                             "type": "text",
#                             "text": """Analyze this receipt. Extract:
# 1. Shop or store name (use "Unknown Shop" if not visible)
# 2. Date of purchase in YYYY-MM-DD format (use today if not visible)
# 3. Every individual line item with its price. Skip totals, taxes, subtotals.
# 4. Category per item if obvious, else use "General"

# Return ONLY this JSON, nothing else:
# {
#   "shop": "Shop Name",
#   "date": "YYYY-MM-DD",
#   "total": 0.00,
#   "items": [
#     {"item": "Item Name", "amount": 0.00, "category": "Category"}
#   ]
# }"""
#                         }
#                     ]
#                 }
#             ],
#             max_tokens=1000
#         )

#         raw = response.choices[0].message.content
#         json_match = re.search(r'\{.*\}', raw, re.DOTALL)
#         parsed = json.loads(json_match.group())

#         # Clean and validate items
#         clean_items = []
#         for item in parsed.get("items", []):
#             if not item.get("item") or item.get("amount") is None:
#                 continue
#             if not item.get("category"):
#                 item["category"] = "General"
#             clean_items.append(item)

#         total = parsed.get("total") or round(sum(i["amount"] for i in clean_items), 2)

#         entry = {
#             "type": "receipt",
#             "shop": parsed.get("shop", "Unknown Shop"),
#             "date": parsed.get("date", datetime.now().strftime("%Y-%m-%d")),
#             "total": round(total, 2),
#             "items": clean_items
#         }

#         data = load_db()
#         data["expenses"].append(entry)
#         save_db(data)

#         return {"status": "success", "extracted": entry, "count": len(clean_items)}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

#     finally:
#         if os.path.exists(file_location):
#             os.remove(file_location)

# # NEW: Monthly summary for last 12 months
# @app.get("/monthly-summary")
# def monthly_summary():
#     data = load_db()
#     monthly = defaultdict(float)

#     for expense in data["expenses"]:
#         date_str = expense.get("date", datetime.now().strftime("%Y-%m-%d"))
#         try:
#             date = datetime.strptime(date_str, "%Y-%m-%d")
#             key = date.strftime("%Y-%m")
#         except:
#             key = datetime.now().strftime("%Y-%m")
#         monthly[key] += get_expense_total(expense)

#     # Build last 12 months even if no data
#     result = []
#     now = datetime.now()
#     for i in range(11, -1, -1):
#         month_num = now.month - i
#         year = now.year
#         while month_num <= 0:
#             month_num += 12
#             year -= 1
#         key = f"{year}-{month_num:02d}"
#         label = datetime(year, month_num, 1).strftime("%b %Y")
#         result.append({
#             "month": key,
#             "label": label,
#             "total": round(monthly.get(key, 0.0), 2)
#         })

#     return {"monthly_summary": result}

# @app.get("/optimize")
# def optimize_budget():
#     data = load_db()
#     total_spent = sum(get_expense_total(e) for e in data["expenses"])
#     remaining_budget = data["monthly_budget"] - total_spent
#     days_left = data["days_in_month"]

#     history = list(reversed(data["expenses"]))[:1000]

#     response_data = {
#         "total_spent": total_spent,
#         "monthly_budget": data["monthly_budget"],
#         "remaining_budget": remaining_budget,
#         "history": history
#     }

#     if remaining_budget <= 0:
#         response_data["optimized_daily_limit"] = 0.0
#         response_data["status"] = "OVER_BUDGET"
#         return response_data

#     solver = pywraplp.Solver.CreateSolver('GLOP')
#     daily_spend = solver.NumVar(0, remaining_budget, 'daily_spend')
#     solver.Add(daily_spend * days_left <= remaining_budget)
#     solver.Maximize(daily_spend)
#     status = solver.Solve()

#     if status == pywraplp.Solver.OPTIMAL:
#         response_data["optimized_daily_limit"] = daily_spend.solution_value()
#         response_data["status"] = "OK"
#         return response_data

#     return {"error": "Could not optimize"}









from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from collections import defaultdict
from datetime import datetime
from groq import Groq
import json, os, shutil, base64, re

from ortools.linear_solver import pywraplp
from database import init_db, get_db, User, Expense
from auth import hash_password, verify_password, create_token, get_current_user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


# ── Auth Schemas ──────────────────────────────────────────────
class SignupRequest(BaseModel):
    email: str
    password: str


# ── Auth Endpoints ────────────────────────────────────────────
@app.post("/signup")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=req.email, hashed_password=hash_password(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


# ── Expense Schemas ───────────────────────────────────────────
class ManualExpense(BaseModel):
    item: str
    amount: float
    category: str
    date: Optional[str] = None


class BudgetUpdate(BaseModel):
    budget: float


# ── Helper ─────────────────────────────────────────────────────
def expense_to_dict(e: Expense):
    return {
        "shop": e.shop,
        "date": e.date,
        "total": e.total,
        "items": json.loads(e.items_json),
    }


# ── Protected Endpoints (require login) ─────────────────────────
@app.post("/manual-entry")
def manual_entry(expense: ManualExpense, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = Expense(
        user_id=user.id,
        shop="Manual Entry",
        date=expense.date or datetime.now().strftime("%Y-%m-%d"),
        total=expense.amount,
        items_json=json.dumps([{"item": expense.item, "amount": expense.amount, "category": expense.category}]),
    )
    db.add(entry)
    db.commit()
    return {"status": "success"}


@app.post("/update-budget")
def update_budget(data: BudgetUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.monthly_budget = data.budget
    db.commit()
    return {"status": "success"}


@app.post("/reset-all")
def reset_all(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Expense).filter(Expense.user_id == user.id).delete()
    user.monthly_budget = 3000.0
    db.commit()
    return {"status": "success"}


@app.post("/process-receipt")
async def process_receipt(
    file: UploadFile = File(...),
    override_date: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb+") as f:
        shutil.copyfileobj(file.file, f)

    try:
        with open(file_location, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")

        ext = file.filename.split(".")[-1].lower()
        media_type = "image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext}"

        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            # model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{image_data}"}},
                    {"type": "text", "text": (
                        "Analyze this receipt. Extract: shop name, date (YYYY-MM-DD), "
                        "and every line item with its price and category. Skip totals/taxes. "
                        'Return ONLY JSON: {"shop": "Name", "date": "YYYY-MM-DD", "total": 0.00, '
                        '"items": [{"item": "Name", "amount": 0.00, "category": "Type"}]}'
                    )},
                ],
            }],
            max_tokens=1000,
        )

        raw = response.choices[0].message.content
        parsed = json.loads(re.search(r"\{.*\}", raw, re.DOTALL).group())

        clean_items = [
            {**i, "category": i.get("category") or "General"}
            for i in parsed.get("items", [])
            if i.get("item") and i.get("amount") is not None
        ]
        total = parsed.get("total") or round(sum(i["amount"] for i in clean_items), 2)

        entry = Expense(
            user_id=user.id,
            shop=parsed.get("shop", "Unknown Shop"),
            date=override_date or parsed.get("date", datetime.now().strftime("%Y-%m-%d")),
            total=round(total, 2),
            items_json=json.dumps(clean_items),
        )
        db.add(entry)
        db.commit()

        return {"status": "success", "count": len(clean_items)}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_location):
            os.remove(file_location)


@app.get("/monthly-summary")
def monthly_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    expenses = db.query(Expense).filter(Expense.user_id == user.id).all()
    monthly = defaultdict(float)

    for e in expenses:
        try:
            key = datetime.strptime(e.date, "%Y-%m-%d").strftime("%Y-%m")
        except Exception:
            key = datetime.now().strftime("%Y-%m")
        monthly[key] += e.total

    result = []
    now = datetime.now()
    for i in range(11, -1, -1):
        month_num, year = now.month - i, now.year
        while month_num <= 0:
            month_num += 12
            year -= 1
        key = f"{year}-{month_num:02d}"
        result.append({
            "month": key,
            "label": datetime(year, month_num, 1).strftime("%b %Y"),
            "total": round(monthly.get(key, 0.0), 2),
        })

    return {"monthly_summary": result}


@app.get("/optimize")
def optimize_budget(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    expenses = db.query(Expense).filter(Expense.user_id == user.id).order_by(Expense.id.desc()).all()
    total_spent = sum(e.total for e in expenses)
    remaining_budget = user.monthly_budget - total_spent

    response_data = {
        "total_spent": total_spent,
        "monthly_budget": user.monthly_budget,
        "remaining_budget": remaining_budget,
        "history": [expense_to_dict(e) for e in expenses[:1000]],
    }

    if remaining_budget <= 0:
        response_data.update(optimized_daily_limit=0.0, status="OVER_BUDGET")
        return response_data

    solver = pywraplp.Solver.CreateSolver("GLOP")
    daily_spend = solver.NumVar(0, remaining_budget, "daily_spend")
    solver.Add(daily_spend * user.days_in_month <= remaining_budget)
    solver.Maximize(daily_spend)

    if solver.Solve() == pywraplp.Solver.OPTIMAL:
        response_data.update(optimized_daily_limit=daily_spend.solution_value(), status="OK")
        return response_data

    return {"error": "Could not optimize"}