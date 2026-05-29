import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'roads.db')

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS roads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            road_type TEXT,
            location TEXT,
            city TEXT,
            state TEXT,
            length_km REAL,
            last_relaid_date TEXT,
            condition TEXT,
            contractor_name TEXT,
            contractor_contact TEXT
        );
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            road_id INTEGER,
            project_name TEXT,
            sanctioned_amount REAL,
            spent_amount REAL,
            currency TEXT DEFAULT 'INR',
            financial_year TEXT,
            source TEXT,
            FOREIGN KEY (road_id) REFERENCES roads(id)
        );
        CREATE TABLE IF NOT EXISTS officers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            designation TEXT,
            department TEXT,
            zone TEXT,
            city TEXT,
            state TEXT,
            phone TEXT,
            email TEXT
        );
        CREATE TABLE IF NOT EXISTS road_officers (
            road_id INTEGER,
            officer_id INTEGER,
            FOREIGN KEY (road_id) REFERENCES roads(id),
            FOREIGN KEY (officer_id) REFERENCES officers(id)
        );
    ''')
    conn.commit()
    conn.close()

def seed_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM roads")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    officers = [
        ("Ravi Kumar", "Executive Engineer", "GHMC", "Zone 3 - Jubilee Hills", "Hyderabad", "Telangana", "9848012345", "ee.zone3@ghmc.gov.in"),
        ("Suresh Reddy", "Executive Engineer", "GHMC", "Zone 1 - Secunderabad", "Hyderabad", "Telangana", "9848056789", "ee.zone1@ghmc.gov.in"),
        ("Priya Sharma", "Divisional Engineer", "NHAI", "NH-65 Division", "Hyderabad", "Telangana", "9848099999", "de.nh65@nhai.gov.in"),
        ("Anand Rao", "Executive Engineer", "PWD", "Division 2 - Banjara Hills", "Hyderabad", "Telangana", "9848011111", "ee.div2@pwd.telangana.gov.in"),
        ("Meena Pillai", "Executive Engineer", "GHMC", "Zone 5 - LB Nagar", "Hyderabad", "Telangana", "9848022222", "ee.zone5@ghmc.gov.in"),
    ]
    cursor.executemany("INSERT INTO officers (name, designation, department, zone, city, state, phone, email) VALUES (?,?,?,?,?,?,?,?)", officers)
    roads = [
        ("Jubilee Hills Road No. 36", "MDR", "Jubilee Hills", "Hyderabad", "Telangana", 2.3, "2023-01-15", "Fair", "ABC Infra Pvt Ltd", "9000012345"),
        ("Banjara Hills Road No. 12", "SH", "Banjara Hills", "Hyderabad", "Telangana", 3.1, "2022-06-20", "Poor", "XYZ Constructions", "9000054321"),
        ("NH-65 Hyderabad Bypass", "NH", "Outer Ring Road", "Hyderabad", "Telangana", 18.5, "2024-03-01", "Good", "L&T Infrastructure", "9000099999"),
        ("Secunderabad MG Road", "MDR", "Secunderabad", "Hyderabad", "Telangana", 1.8, "2021-11-10", "Poor", "Ramky Infrastructure", "9000088888"),
        ("LB Nagar Main Road", "SH", "LB Nagar", "Hyderabad", "Telangana", 4.2, "2023-08-22", "Fair", "Navayuga Engineering", "9000077777"),
        ("Kukatpally Housing Board Road", "MDR", "Kukatpally", "Hyderabad", "Telangana", 2.9, "2022-02-14", "Poor", "ABC Infra Pvt Ltd", "9000012345"),
        ("Gachibowli Outer Ring Road", "NH", "Gachibowli", "Hyderabad", "Telangana", 6.7, "2024-01-05", "Good", "L&T Infrastructure", "9000099999"),
        ("Ameerpet Metro Road", "MDR", "Ameerpet", "Hyderabad", "Telangana", 1.5, "2023-05-18", "Fair", "MEIL Constructions", "9000033333"),
        ("Dilsukhnagar Main Road", "SH", "Dilsukhnagar", "Hyderabad", "Telangana", 3.3, "2021-09-30", "Poor", "XYZ Constructions", "9000054321"),
        ("Madhapur Hi-Tech City Road", "MDR", "Madhapur", "Hyderabad", "Telangana", 2.1, "2023-12-10", "Good", "Navayuga Engineering", "9000077777"),
    ]
    cursor.executemany("INSERT INTO roads (name, road_type, location, city, state, length_km, last_relaid_date, condition, contractor_name, contractor_contact) VALUES (?,?,?,?,?,?,?,?,?,?)", roads)
    budgets = [
        (1, "Jubilee Hills Road Resurfacing 2023", 4200000, 3900000, "INR", "2022-23", "GHMC / State Budget"),
        (2, "Banjara Hills SH Repair", 6500000, 6200000, "INR", "2021-22", "State PWD"),
        (3, "NH-65 Bypass Construction", 850000000, 820000000, "INR", "2023-24", "NHAI / OMMS"),
        (4, "MG Road Restoration", 3100000, 2800000, "INR", "2021-22", "GHMC"),
        (5, "LB Nagar SH Widening", 9200000, 8100000, "INR", "2022-23", "State PWD"),
        (6, "KPHB Road Repair", 5400000, 5100000, "INR", "2021-22", "GHMC"),
        (7, "ORR Gachibowli Extension", 120000000, 115000000, "INR", "2023-24", "NHAI / OMMS"),
        (8, "Ameerpet Road Metro Work", 7800000, 7600000, "INR", "2022-23", "GHMC / HMRL"),
        (9, "Dilsukhnagar Road Repair", 4800000, 4500000, "INR", "2021-22", "GHMC"),
        (10, "Madhapur IT Corridor Road", 6100000, 5900000, "INR", "2023-24", "GHMC / IT Dept"),
    ]
    cursor.executemany("INSERT INTO budgets (road_id, project_name, sanctioned_amount, spent_amount, currency, financial_year, source) VALUES (?,?,?,?,?,?,?)", budgets)
    road_officers = [(1,1),(2,4),(3,3),(4,2),(5,5),(6,1),(7,3),(8,2),(9,5),(10,1)]
    cursor.executemany("INSERT INTO road_officers (road_id, officer_id) VALUES (?,?)", road_officers)
    conn.commit()
    conn.close()