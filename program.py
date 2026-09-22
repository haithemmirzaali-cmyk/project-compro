import struct
import time
from datetime import datetime, timezone, timedelta
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

############################################# BINARY FILE ##############################################################
books_struck = struct.Struct("<i50si30siiiI")
def add_book(book_id, title, status, author, year, copies):
    now = int(time.time())
    record = books_struck.pack(
        book_id,
        title.encode("utf-8").ljust(50, b"\x00"),
        status,
        author.encode("utf-8").ljust(30, b"\x00"),
        year,
        copies,
        now,   # created_at
        now    # updated_at
    )
    with open("books.dat", "ab") as f:
        f.write(record)

members_struck = struct.Struct("<ii50siiII")
def add_members(member_id , status , name, birth_year , max_loan):
    now = int(time.time())
    record = members_struck.pack(
        member_id,
        status,
        name.encode("utf-8").ljust(50, b"\x00"),
        birth_year,
        max_loan,
        now,   # created_at
        now    # updated_at
    )
    with open("members.dat", "ab") as f:
        f.write(record)

loans_struck = struct.Struct("<Iiii10s10sii")
def add_loans(op_code, book_id, member_id, loan_date, return_date, status_after, is_rented_after):
    now = int(time.time())
    record = loans_struck.pack(
        now,
        op_code,
        book_id,
        member_id,
        loan_date.encode("utf-8").ljust(10, b"\x00"),
        return_date.encode("utf-8").ljust(10, b"\x00"),
        status_after,
        is_rented_after
    )
    with open("loans.dat", "ab") as f:
        f.write(record)
def read_all_books(filename="books.dat"):
    books = []
    try:
        with open(filename, "rb") as f:
            while True:
                data = f.read(books_struck.size)
                if len(data) < books_struck.size:
                    break 
                unpacked = books_struck.unpack(data)
                
                book = {
                    "book_id": unpacked[0],
                    "title": unpacked[1].decode("utf-8").rstrip("\x00"),
                    "status": unpacked[2],
                    "author": unpacked[3].decode("utf-8").rstrip("\x00"),
                    "year": unpacked[4],
                    "copies": unpacked[5],
                    "created_at": datetime.fromtimestamp(unpacked[6]).strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.fromtimestamp(unpacked[7]).strftime("%Y-%m-%d %H:%M:%S")
                }
                books.append(book)
    except FileNotFoundError:
        print(f"ไฟล์ {filename} ไม่พบ")
    return books
def read_all_members(filename="members.dat"):
    members = []
    try:
        with open(filename, "rb") as f:
            while True:
                data = f.read(members_struck.size)
                if len(data) < members_struck.size:
                    break
                unpacked = members_struck.unpack(data)
                
                member = {
                    "member_id": unpacked[0],
                    "status": unpacked[1],
                    "name": unpacked[2].decode("utf-8").rstrip("\x00"),
                    "birth_year": unpacked[3],
                    "max_loan": unpacked[4],
                    "created_at": datetime.fromtimestamp(unpacked[5]).strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.fromtimestamp(unpacked[6]).strftime("%Y-%m-%d %H:%M:%S")
                }
                members.append(member)
    except FileNotFoundError:
        print(f"ไฟล์ {filename} ไม่พบ")
    return members

def read_all_loans(filename="loans.dat"):
    loans = []
    try:
        with open(filename, "rb") as f:
            while True:
                data = f.read(loans_struck.size)
                if len(data) < loans_struck.size:
                    break 
                unpacked = loans_struck.unpack(data)
                loan = {
                    "ts": datetime.fromtimestamp(unpacked[0]).strftime("%Y-%m-%d %H:%M:%S"),
                    "op_code": unpacked[1],
                    "book_id": unpacked[2],
                    "member_id": unpacked[3],
                    "loan_date": unpacked[4].decode("utf-8").rstrip("\x00"),
                    "return_date": unpacked[5].decode("utf-8").rstrip("\x00"),
                    "status_after": unpacked[6],
                    "is_rented_after": unpacked[7],
                }
                loans.append(loan)
    except FileNotFoundError:
        print(f"\n❌ File {filename} not found")
    return loans

############################################# BINARY FILE ##############################################################

############################################ FUNCTIONS MENU ############################################################
def menu_add_book():
    print("\n=== Add New Book ===")
    try:
        book_id = int(input("Enter Book ID: "))
        title = str(input("Enter Title: "))
        author = str(input("Enter Author: "))
        year = int(input("Enter Year: "))
        copies = int(input("Enter Copies: "))
        status = 1  

        add_book(book_id, title, status, author, year, copies)
        print(f"\n✅ Book '{title}' added successfully!")

    except ValueError:
        print("\n❌ Invalid input. Please enter valid information.")

def menu_delete_book(book_id, filename="books.dat"):
    books = []
    found = False
    try:
        with open(filename, "rb") as f:
            while True:
                data = f.read(books_struck.size)
                if len(data) < books_struck.size:
                    break
                unpacked = books_struck.unpack(data)
                books.append(list(unpacked))
    except FileNotFoundError:
        print(f"\n❌ File {filename} not found")
        return

    for b in books:
        if b[0] == book_id and b[2] == 1: 
            b[2] = 0  
            b[7] = int(time.time()) 
            found = True
            break

    if not found:
        print(f"\n❌ Book ID {book_id} not found or already deleted")
        return

    with open(filename, "wb") as f:
        for b in books:
            record = books_struck.pack(*b)
            f.write(record)

    print(f"\n✅ Book ID {book_id} deleted successfully")

def menu_view_books(filename="books.dat"):
    books = read_all_books(filename)
    if not books:
        print("No books found.")
        return

    print("-" * 108)
    print(f"{'ID':<6} {'Title':<45} {'Author':<25} {'Year':<6} {'Copies':<7} {'Status':<8}")
    print("-" * 108)

    for b in books:
        status_text = "Active" if b['status'] == 1 else "Deleted"
        print(f"{b['book_id']:<6} {b['title']:<45} {b['author']:<25} {b['year']:<6} {b['copies']:<7} {status_text:<8}")

    print("-" * 108)

def menu_edit_book(filename="books.dat"):
    menu_view_books()
    try:
        book_id = int(input("Enter Book ID to edit: "))
    except ValueError:
        print("\n❌ Invalid input. Please enter a number.")
        return

    books = []
    found = False
    try:
        with open(filename, "rb") as f:
            while True:
                data = f.read(books_struck.size)
                if len(data) < books_struck.size:
                    break
                unpacked = books_struck.unpack(data)
                books.append(list(unpacked))
    except FileNotFoundError:
        print(f"\n❌ File {filename} not found")
        return

    for b in books:
        if b[0] == book_id and b[2] == 1: 
            print(f"Editing Book ID {book_id}")
            title = input(f"Enter new Title [{b[1].decode('utf-8').rstrip(chr(0))}]: ")
            author = input(f"Enter new Author [{b[3].decode('utf-8').rstrip(chr(0))}]: ")
            try:
                year = input(f"Enter new Year [{b[4]}]: ")
                year = int(year) if year else b[4]
                copies = input(f"Enter new Copies [{b[5]}]: ")
                copies = int(copies) if copies else b[5]
            except ValueError:
                print("\n❌ Invalid number input. Edit canceled.")
                return

            b[1] = title.encode("utf-8").ljust(50, b"\x00") if title else b[1]
            b[3] = author.encode("utf-8").ljust(30, b"\x00") if author else b[3]
            b[4] = year
            b[5] = copies
            b[7] = int(time.time())
            found = True
            break

    if not found:
        print(f"\n❌ Book ID {book_id} not found or not active")
        return

    with open(filename, "wb") as f:
        for b in books:
            record = books_struck.pack(*b)
            f.write(record)

    print(f"\n✅ Book ID {book_id} updated successfully")

def menu_add_member():
    print("\n=== Add New Member ===")
    try:
        member_id = int(input("Enter Member ID: "))
        status = 1
        name = str(input("Enter Member Name: "))
        birth_year = int(input("Enter Birth Year: "))
        max_loan = 5

        add_members(member_id, status, name, birth_year, max_loan)
        print(f"\n✅ Member '{name}' added successfully!")

    except ValueError:
        print("\n❌ Invalid input. Please enter valid information.")

def menu_view_members(filename="members.dat"):
    members = read_all_members(filename)
    if not members:
        print("No members found.")
        return

    print("-" * 83)
    print(f"{'ID':<10} {'Name':<22} {'Birth Year':<17} {'Max Loan':<19} {'Status':<17}")
    print("-" * 83)

    for m in members:
        status_text = "Active" if m['status'] == 1 else "Deleted"
        print(f"{m['member_id']:<10} {m['name']:<22} {m['birth_year']:<17} {m['max_loan']:<19} {status_text:<17}")

    print("-" * 83)

def menu_edit_member(filename="members.dat"):
    menu_view_members()
    try:
        member_id = int(input("Enter Member ID to edit: "))
    except ValueError:
        print("\n❌ Invalid input. Please enter a number.")
        return

    members = []
    found = False
    try:
        with open(filename, "rb") as f:
            while True:
                data = f.read(members_struck.size)
                if len(data) < members_struck.size:
                    break
                unpacked = members_struck.unpack(data)
                members.append(list(unpacked))
    except FileNotFoundError:
        print(f"\n❌ File {filename} not found")
        return

    for m in members:
        if m[0] == member_id and m[1] == 1:
            print(f"Editing Member ID {member_id}")
            name = input(f"Enter new Name [{m[2].decode('utf-8').rstrip(chr(0))}]: ")
            try:
                birth_year = input(f"Enter new Birth Year [{m[3]}]: ")
                birth_year = int(birth_year) if birth_year else m[3]
                max_loan = input(f"Enter new Max Loan [{m[4]}]: ")
                max_loan = int(max_loan) if max_loan else m[4]
            except ValueError:
                print("\n❌ Invalid number input. Edit canceled.")
                return

            m[2] = name.encode("utf-8").ljust(50, b"\x00") if name else m[2]
            m[3] = birth_year
            m[4] = max_loan
            m[6] = int(time.time())  
            found = True
            break

    if not found:
        print(f"\n❌ Member ID {member_id} not found or not active")
        return

    with open(filename, "wb") as f:
        for m in members:
            record = members_struck.pack(*m)
            f.write(record)

    print(f"\n✅ Member ID {member_id} updated successfully")

def menu_delete_member(member_id, filename="members.dat"):
    members = []
    found = False
    try:
        with open(filename, "rb") as f:
            while True:
                data = f.read(members_struck.size)
                if len(data) < members_struck.size:
                    break
                unpacked = members_struck.unpack(data)
                members.append(list(unpacked))
    except FileNotFoundError:
        print(f"\n❌ File {filename} not found")
        return

    for m in members:
        if m[0] == member_id and m[1] == 1:
            m[1] = 0 
            m[6] = int(time.time()) 
            found = True
            break

    if not found:
        print(f"\n❌ Member ID {member_id} not found or already deleted")
        return

    with open(filename, "wb") as f:
        for m in members:
            record = members_struck.pack(*m)
            f.write(record)

    print(f"\n✅ Member ID {member_id} deleted successfully")

def get_current_loans(loans):
    latest = {}
    for loan in loans:
        key = (loan["book_id"], loan["member_id"])
        latest[key] = loan

    current_loans = [l for l in latest.values() if l["is_rented_after"] == 1]
    return current_loans
def menu_borrow_book():
    print("\n=== Borrow Book ===")

    books = read_all_books("books.dat")
    members = read_all_members("members.dat")

    # แสดงหนังสือที่ยังยืมได้
    print("Available Books:")
    print("-" * 90)
    print(f"{'ID':<6} {'Title':<45} {'Copies':<8} {'Borrowed':<10} {'Available':<10}")
    print("-" * 90)

    loans = read_all_loans("loans.dat")
    current_loans = get_current_loans(loans)

    borrowed_count = {
        b["book_id"]: sum(1 for l in current_loans if l["book_id"] == b["book_id"])
        for b in books
    }

    for b in books:
        if b["status"] == 1:
            borrowed = borrowed_count.get(b["book_id"], 0)
            available = b["copies"] - borrowed
            print(f"{b['book_id']:<6} {b['title']:<45} {b['copies']:<8} {borrowed:<10} {available:<10}")

    print("-" * 90)

    try:
        book_id = int(input("Enter Book ID to borrow: "))
        member_id = int(input("Enter Member ID: "))
    except ValueError:
        print("\n❌ Invalid input. Please enter numbers only.")
        return

    # ตรวจสอบหนังสือ
    book = next((b for b in books if b["book_id"] == book_id and b["status"] == 1), None)
    if not book:
        print(f"\n❌ Book ID {book_id} not found or not active")
        return

    borrowed_now = borrowed_count.get(book_id, 0)
    if borrowed_now >= book["copies"]:
        print("\n❌ No copies available for this book")
        return

    # ตรวจสอบสมาชิก
    member = next((m for m in members if m["member_id"] == member_id and m["status"] == 1), None)
    if not member:
        print(f"\n❌ Member ID {member_id} not found or not active")
        return

    # กำหนดวันยืม/คืน ถัดไป 1 เดือนจากวันที่ยืม
    today = datetime.now().strftime("%Y/%m/%d")
    due_date = (datetime.now() + timedelta(days=30)).strftime("%Y/%m/%d")

    add_loans(
        op_code=1,      
        book_id=book_id,
        member_id=member_id,
        loan_date=today,
        return_date=due_date,
        status_after=book["status"],
        is_rented_after=1
    )

    print(f"\n✅ Member '{member['name']}' borrowed '{book['title']}' until {due_date}")

def menu_return_book():
    print("\n=== Return Book ===")

    loans = read_all_loans("loans.dat")
    books = read_all_books("books.dat")
    members = read_all_members("members.dat")

    # แสดงที่ยังไม่คืน
    loans = read_all_loans("loans.dat")
    current_loans = get_current_loans(loans)

    if not current_loans:
        print("No books currently borrowed.")
        return

    print("-" * 97)
    print(f"{'BookID':<8} {'Title':<45} {'MemberID':<10} {'Member Name':<20} {'Loan Date':<10}")
    print("-" * 97)

    for l in current_loans:
        book_title = next((b["title"] for b in books if b["book_id"] == l["book_id"]), "Unknown")
        member_name = next((m["name"] for m in members if m["member_id"] == l["member_id"]), "Unknown")
        print(f"{l['book_id']:<8} {book_title:<45} {l['member_id']:<10} {member_name:<20} {l['loan_date']:<10}")

    print("-" * 97)

    try:
        book_id = int(input("Enter Book ID to return: "))
        member_id = int(input("Enter Member ID: "))
    except ValueError:
        print("\n❌ Invalid input. Please enter numbers only.")
        return

    loan = next((l for l in current_loans if l["book_id"] == book_id and l["member_id"] == member_id), None)
    if not loan:
        print("\n❌ No matching active loan found")
        return

    today = datetime.now().strftime("%Y/%m/%d")
    book = next((b for b in books if b["book_id"] == book_id), None)

    add_loans(
        op_code=2,      
        book_id=book_id,
        member_id=member_id,
        loan_date=loan["loan_date"], 
        return_date=today,  
        status_after=book["status"] if book else 1,
        is_rented_after=0 
    )

    print(f"\n✅ Book ID {book_id} has been returned by Member ID {member_id}")

def menu_view_overdue_loans():
    print("\n=== Overdue Books ===")

    loans = read_all_loans("loans.dat")
    books = read_all_books("books.dat")
    members = read_all_members("members.dat")

    current_loans = get_current_loans(loans)

    if not current_loans:
        print("No books currently borrowed.")
        return

    today = datetime.now().date()
    overdue_loans = []

    for loan in current_loans:
        try:
            due_date = datetime.strptime(
                loan["return_date"], "%Y/%m/%d"
            ).date()

            if today > due_date:
                overdue_days = (today - due_date).days

                overdue_loans.append({
                    "loan": loan,
                    "overdue_days": overdue_days
                })

        except ValueError:
            continue

    if not overdue_loans:
        print("\n❌ No overdue books.")
        return

    print("-" * 97)
    print(
        f"{'BookID':<8} "
        f"{'Title':<100} "
        f"{'MemberID':<10} "
        f"{'Member Name':<20} "
        f"{'Overdue':<10}"
    )
    print("-" * 97)

    for item in overdue_loans:
        loan = item["loan"]
        overdue_days = item["overdue_days"]

        book_title = next(
            (b["title"] for b in books
             if b["book_id"] == loan["book_id"]),
            "Unknown"
        )

        member_name = next(
            (m["name"] for m in members
             if m["member_id"] == loan["member_id"]),
            "Unknown"
        )

        print(
            f"{loan['book_id']:<8} "
            f"{book_title:<35} "
            f"{loan['member_id']:<10} "
            f"{member_name:<20} "
            f"{overdue_days} days"
        )

    print("-" * 97)
    print(f"Total overdue books: {len(overdue_loans)}")

def menu_view_all_loans():
    loans = read_all_loans("loans.dat")
    books = read_all_books("books.dat")
    members = read_all_members("members.dat")

    if not loans:
        print("\nNo loans found.")
        return

    print("-" * 124)
    print(f"{'Timestamp':<20} {'BookID':<7} {'Title':<45} {'MemberID':<10} {'Member Name':<20} {'Type':<8} {'Status':<6}")
    print("-" * 124)

    for loan in loans:
        book_title = next((b["title"] for b in books if b["book_id"] == loan["book_id"]), "Unknown")
        member_name = next((m["name"] for m in members if m["member_id"] == loan["member_id"]), "Unknown")
        loan_type = "Borrow" if loan["op_code"] == 1 else "Return"
        status_text = "Borrowed" if loan["is_rented_after"] == 1 else "Returned"

        print(f"{loan['ts']:<20} {loan['book_id']:<7} {book_title:<45} {loan['member_id']:<10} {member_name:<20} {loan_type:<8} {status_text:<6}")

    print("-" * 124)

def menu_view_current_loans():
    loans = read_all_loans("loans.dat")
    current_loans = get_current_loans(loans)

    if not current_loans:
        print("\nNo books currently borrowed.")
        return

    books = read_all_books("books.dat")
    members = read_all_members("members.dat")

    print("\n=== Current Loans ===")
    print("-" * 124)
    print(f"{'BookID':<8} {'Title':<45} {'MemberID':<10} {'Member Name':<20} {'Loan Date':<10}")
    print("-" * 124)

    for l in current_loans:
        book_title = next((b["title"] for b in books if b["book_id"] == l["book_id"]), "Unknown")
        member_name = next((m["name"] for m in members if m["member_id"] == l["member_id"]), "Unknown")
        print(f"{l['book_id']:<8} {book_title:<45} {l['member_id']:<10} {member_name:<20} {l['loan_date']:<10}")

    print("-" * 124)

############################################ FUNCTIONS MENU ############################################################
################################################ REPORT ################################################################
def generate_report(report_file="report.pdf"):
    all_books = read_all_books("books.dat")
    all_members = read_all_members("members.dat")
    loan_records = read_all_loans("loans.dat")

    tz_utc7 = timezone(timedelta(hours=7))
    generated_timestamp = datetime.now(tz_utc7).strftime("%Y-%m-%d %H:%M (%z)")

    latest_loans_map = {}
    for entry in loan_records:
        pair_key = (entry["book_id"], entry["member_id"])
        latest_loans_map[pair_key] = entry  

    active_borrowers_map = {}
    for (b_id, m_id), entry in latest_loans_map.items():
        if entry["is_rented_after"] == 1:
            m_name = next((m["name"] for m in all_members if m["member_id"] == m_id), "Unknown")
            active_borrowers_map.setdefault(b_id, []).append(m_name)

    def get_status_text(val):
        return "Active" if val == 1 else "Deleted"

    # ตั้งค่าเอกสาร PDF 
    doc = SimpleDocTemplate(
        report_file,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1A365D")
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=15,
        leading=14,
        textColor=colors.HexColor("#4A5568")
    )
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=16,
        leading=12
    )

    elements = []

    # Header
    elements.append(Paragraph("Library Borrow System - Summary Report", title_style))
    elements.append(Paragraph(f"<b>Generated At:</b> {generated_timestamp} | <b>App Version:</b> 2.0", subtitle_style))
    elements.append(Spacer(1, 15))

    # Table Data
    table_data = [
        ["BookID", "Title", "Author", "Year", "Copies", "Borrowed By", "Status"]
    ]

    for book in all_books:
        if book["status"] != 1:
            continue

        borrowers = active_borrowers_map.get(book["book_id"], [])
        if not borrowers:
            borrowed_str = "0"
        else:
            borrowed_str = "\n".join([f"{idx}. {name}" for idx, name in enumerate(borrowers, start=1)])

        table_data.append([
            str(book['book_id']),
            book['title'][:30] + "..." if len(book['title']) > 30 else book['title'],
            book['author'],
            str(book['year']),
            str(book['copies']),
            borrowed_str,
            get_status_text(book['status'])
        ])

    table = Table(table_data, colWidths=[55, 230, 160, 45, 55, 150, 60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (3, 0), (4, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 15))

    # Calculations
    total_book_count = len(all_books)
    active_book_count = sum(1 for b in all_books if b["status"] == 1)
    deleted_book_count = total_book_count - active_book_count
    total_borrowed_now = sum(len(names) for names in active_borrowers_map.values())
    total_available_now = sum(
        (b["copies"] - len(active_borrowers_map.get(b["book_id"], []))) for b in all_books if b["status"] == 1
    )

    borrow_freq = {b["book_id"]: 0 for b in all_books}
    for record in loan_records:
        if record["op_code"] == 1:
            borrow_freq[record["book_id"]] += 1

    if borrow_freq:
        top_book_id = max(borrow_freq, key=borrow_freq.get, default=None)
        if top_book_id is not None:
            max_borrow_count = borrow_freq[top_book_id]
            top_book_title = next((b["title"] for b in all_books if b["book_id"] == top_book_id), "N/A")
        else:
            top_book_title = "N/A"
            max_borrow_count = 0
    else:
        top_book_title = "N/A"
        max_borrow_count = 0

    active_member_count = sum(1 for m in all_members if m["status"] == 1)

    # Summary Text
    elements.append(Paragraph("Summary (Active Books Only)", heading_style))
    summary_text = f"""
    • <b>Total Books:</b> {total_book_count} | 
    <b>Active Books:</b> {active_book_count} | 
    <b>Deleted Books:</b> {deleted_book_count}<br/>
    • <b>Borrowed Now:</b> {total_borrowed_now} | 
    <b>Available Now:</b> {total_available_now}
    """
    elements.append(Paragraph(summary_text, body_style))

    elements.append(Paragraph("Borrow Statistics", heading_style))
    stats_text = f"""
    • <b>Most Borrowed Book:</b> {top_book_title} ({max_borrow_count} times)<br/>
    • <b>Currently Borrowed:</b> {total_borrowed_now}<br/>
    • <b>Active Members:</b> {active_member_count}
    """
    elements.append(Paragraph(stats_text, body_style))

    doc.build(elements)
    print(f"\n✅ PDF Report generated: {report_file}")


################################################ REPORT ################################################################
################################################# MENU #################################################################
def main_menu():
    while True:
        print("\n=== Library Borrow System ===")
        print("1. Manage Books")
        print("2. Manage Members")
        print("3. Manage Loans")
        print("4. Generate report")
        print("5. Exit")
        choice = input("Select an option (1-5): ")

        if choice == "1":
            manage_books()
        elif choice == "2":
            manage_members()
        elif choice == "3":
            manage_loans()
        elif choice == "4":
            generate_report("report.pdf")
        elif choice == "5":
            print("\nExiting program...")
            break
        else:
            print("\n❌ Invalid option! Please select 1-5.")


def manage_books():
    while True:
        print("\n--- Manage Books ---")
        print("1. Add Book")
        print("2. View All Books")
        print("3. Edit Book")
        print("4. Delete Book")
        print("5. Back to Main Menu")
        choice = input("Select an option (1-5): ")

        if choice == "1":
            menu_add_book()
        elif choice == "2":
            menu_view_books()
        elif choice == "3":
            menu_edit_book()
        elif choice == "4":
            menu_view_books()
            while True:
                try:
                    book_id = int(input("Enter Book ID: "))
                    menu_delete_book(book_id)
                    break
                except ValueError:
                    print("\n❌ Invalid input. Please enter a number.")
        elif choice == "5":
            break
        else:
            print("\n❌ Invalid option! Please select 1-5.")


def manage_members():
    while True:
        print("\n--- Manage Members ---")
        print("1. Add Member")
        print("2. View All Members")
        print("3. Edit Member")
        print("4. Delete Member")
        print("5. Back to Main Menu")

        choice = input("Select an option (1-5): ")
        if choice == "1":
            menu_add_member()
        elif choice == "2":
            menu_view_members()
        elif choice == "3":
            menu_edit_member()
        elif choice == "4":
            menu_view_members()
            while True:
                try:
                    member_id = int(input("Enter Member ID: "))
                    menu_delete_member(member_id)
                    break
                except ValueError:
                    print("\n❌ Invalid input. Please enter a number.")
        elif choice == "5":
            break
        else:
            print("\n❌ Invalid option! Please select 1-5.")


def manage_loans():
    while True:
        print("\n--- Manage Loans ---")
        print("1. Borrow Book")
        print("2. Return Book")
        print("3. View All Loans")
        print("4. View overdue Loans")
        print("5. Current Loans")
        print("6. Back to Main Menu")

        choice = input("Select an option (1-6): ")
        if choice == "1":
            menu_borrow_book()
        elif choice == "2":
            menu_return_book()
        elif choice == "3":
            menu_view_all_loans()
        elif choice == "4":
            menu_view_overdue_loans()
        elif choice == "5":
            menu_view_current_loans()
        elif choice == "6":
            break
        else:
            print("\n❌ Invalid option! Please select 1-6.")

################################################# MENU #################################################################

main_menu()#  :)