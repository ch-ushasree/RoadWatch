import sqlite3
from backend.database import get_connection
from datetime import datetime

def lookup_road(location: str) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    search = f"%{location}%"
    cursor.execute('''
        SELECT * FROM roads
        WHERE name LIKE ? OR location LIKE ? OR city LIKE ?
        LIMIT 3
    ''', (search, search, search))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return {"found": False, "message": f"No road data found for '{location}'."}
    results = []
    for row in rows:
        try:
            relaid = datetime.strptime(row["last_relaid_date"], "%Y-%m-%d")
            months_ago = (datetime.now() - relaid).days // 30
            age_text = f"{months_ago} months ago"
        except:
            age_text = "unknown"
        results.append({
            "id": row["id"],
            "name": row["name"],
            "road_type": row["road_type"],
            "location": row["location"],
            "city": row["city"],
            "length_km": row["length_km"],
            "last_relaid_date": row["last_relaid_date"],
            "last_relaid_text": age_text,
            "condition": row["condition"],
            "contractor_name": row["contractor_name"],
            "contractor_contact": row["contractor_contact"],
        })
    return {"found": True, "roads": results}


def get_budget(road_id: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM budgets WHERE road_id = ?", (road_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"found": False, "message": "No budget data found."}
    sanctioned = row["sanctioned_amount"]
    spent = row["spent_amount"]
    utilisation = round((spent / sanctioned) * 100, 1) if sanctioned > 0 else 0
    def format_inr(amount):
        if amount >= 10000000:
            return f"Rs.{amount/10000000:.2f} Cr"
        elif amount >= 100000:
            return f"Rs.{amount/100000:.2f} Lakh"
        else:
            return f"Rs.{amount:,.0f}"
    return {
        "found": True,
        "project_name": row["project_name"],
        "sanctioned": format_inr(sanctioned),
        "spent": format_inr(spent),
        "utilisation_percent": utilisation,
        "financial_year": row["financial_year"],
        "source": row["source"],
    }


def get_officer(road_id: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.* FROM officers o
        JOIN road_officers ro ON o.id = ro.officer_id
        WHERE ro.road_id = ?
    ''', (road_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"found": False, "message": "No officer found."}
    return {
        "found": True,
        "name": row["name"],
        "designation": row["designation"],
        "department": row["department"],
        "zone": row["zone"],
        "phone": row["phone"],
        "email": row["email"],
    }


def get_accountability_score(road_id: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM roads WHERE id = ?", (road_id,))
    road = cursor.fetchone()
    cursor.execute("SELECT * FROM budgets WHERE road_id = ?", (road_id,))
    budget = cursor.fetchone()
    conn.close()
    if not road:
        return {"found": False, "message": "Road not found."}
    try:
        relaid = datetime.strptime(road["last_relaid_date"], "%Y-%m-%d")
        age_months = (datetime.now() - relaid).days // 30
    except:
        age_months = 24
    condition_score = {"Good": 100, "Fair": 60, "Poor": 20}.get(road["condition"], 50)
    if budget:
        utilisation = (budget["spent_amount"] / budget["sanctioned_amount"]) * 100
        if utilisation > 80 and road["condition"] == "Poor":
            budget_score = 20
        elif utilisation > 80:
            budget_score = 90
        else:
            budget_score = 60
    else:
        budget_score = 50
    age_penalty = min(age_months * 1.5, 40) if road["condition"] in ["Fair", "Poor"] else 0
    final_score = max(0, round((condition_score * 0.5 + budget_score * 0.5) - age_penalty))
    if final_score >= 75:
        verdict = "Good — road well maintained relative to spending"
    elif final_score >= 45:
        verdict = "Moderate — some accountability gaps"
    else:
        verdict = "Poor — high spending with deteriorated road condition"
    return {
        "found": True,
        "road_name": road["name"],
        "condition": road["condition"],
        "age_months": age_months,
        "accountability_score": final_score,
        "verdict": verdict,
    }


def draft_complaint(road_name: str, issue: str, officer_name: str,
                    officer_email: str, officer_designation: str,
                    department: str) -> dict:
    today = datetime.now().strftime("%d %B %Y")
    subject = f"Complaint Regarding Poor Road Condition - {road_name}"
    body = f"""Date: {today}

To,
{officer_name}
{officer_designation}
{department}

Subject: {subject}

Respected Sir/Madam,

I am writing to bring to your attention the deteriorating condition of {road_name}. The road is currently in a poor state with issues including: {issue}.

This poses a serious risk to public safety and requires immediate attention from the concerned authorities.

I request you to kindly inspect the road at the earliest and take necessary action for its repair and restoration. A prompt response will be appreciated.

I also request that the action taken report be shared with me for transparency.

Thanking you,
[Your Name]
[Your Contact Number]
[Your Address]

CC: grievances@telangana.gov.in"""
    return {
        "found": True,
        "subject": subject,
        "to_email": officer_email,
        "body": body,
    }