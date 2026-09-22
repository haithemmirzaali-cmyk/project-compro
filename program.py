import struct
import time
from datetime import datetime, timezone, timedelta
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

############################################# BINARY FILE STRUCTURES ##############################################################
book_layout = struct.Struct("<i50si30siiiI")
member_layout = struct.Struct("<ii50siiII")
loan_layout = struct.Struct("<Iiii10s10sii")

def add_book(book_id, title, status, author, pub_year, total_copies):
    current_ts = int(time.time())
    record = book_layout.pack(
        book_id,
        title.encode("utf-8").ljust(50, b"\x00"),
        status,
        author.encode("utf-8").ljust(30, b"\x00"),
        pub_year,
        total_copies,
        current_ts,   # created_at
        current_ts    # updated_at
    )
    with open("books.dat", "ab") as file_out:
        file_out.write(record)

def add_members(member_id, status, full_name, birth_year, loan_limit):
    current_ts = int(time.time())
    record = member_layout.pack(
        member_id,
        status,
        full_name.encode("utf-8").ljust(50, b"\x00"),
        birth_year,
        loan_limit,
        current_ts,   # created_at
        current_ts    # updated_at
    )
    with open("members.dat", "ab") as file_out:
        file_out.write(record)

def add_loans(operation_code, book_id, member_id, start_date, end_date, status_after, is_rented_after):
    current_ts = int(time.time())
    record = loan_layout.pack(
        current_ts,
        operation_code,
        book_id,
        member_id,
        start_date.encode("utf-8").ljust(10, b"\x00"),
        end_date.encode("utf-8").ljust(10, b"\x00"),
        status_after,
        is_rented_after
    )
    with open("loans.dat", "ab") as file_out:
        file_out.write(record)

def read_all_books(target_file="books.dat"):
    book_list = []
    try:
        with open(target_file, "rb") as file_in:
            while True:
                raw_bytes = file_in.read(book_layout.size)
                if len(raw_bytes) < book_layout.size:
                    break 
                data = book_layout.unpack(raw_bytes)
                
                book_entry = {
                    "book_id": data[0],
                    "title": data[1].decode("utf-8").rstrip("\x00"),
                    "status": data[2],
                    "author": data[3].decode("utf-8").rstrip("\x00"),
                    "year": data[4],
                    "copies": data[5],
                    "created_at": datetime.fromtimestamp(data[6]).strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.fromtimestamp(data[7]).strftime("%Y-%m-%d %H:%M:%S")
                }
                book_list.append(book_entry)
    except FileNotFoundError:
        print(f"ไฟล์ {target_file} ไม่พบ")
    return book_list

def read_all_members(target_file="members.dat"):
    member_list = []
    try:
        with open(target_file, "rb") as file_in:
            while True:
                raw_bytes = file_in.read(member_layout.size)
                if len(raw_bytes) < member_layout.size:
                    break
                data = member_layout.unpack(raw_bytes)
                
                member_entry = {
                    "member_id": data[0],
                    "status": data[1],
                    "name": data[2].decode("utf-8").rstrip("\x00"),
                    "birth_year": data[3],
                    "max_loan": data[4],
                    "created_at": datetime.fromtimestamp(data[5]).strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.fromtimestamp(data[6]).strftime("%Y-%m-%d %H:%M:%S")
                }
                member_list.append(member_entry)
    except FileNotFoundError:
        print(f"ไฟล์ {target_file} ไม่พบ")
    return member_list

def read_all_loans(target_file="loans.dat"):
    loan_list = []
    try:
        with open(target_file, "rb") as file_in:
            while True:
                raw_bytes = file_in.read(loan_layout.size)
                if len(raw_bytes) < loan_layout.size:
                    break 
                data = loan_layout.unpack(raw_bytes)
                loan_entry = {
                    "ts": datetime.fromtimestamp(data[0]).strftime("%Y-%m-%d %H:%M:%S"),
                    "op_code": data[1],
                    "book_id": data[2],
                    "member_id": data[3],
                    "loan_date": data[4].decode("utf-8").rstrip("\x00"),
                    "return_date": data[5].decode("utf-8").rstrip("\x00"),
                    "status_after": data[6],
                    "is_rented_after": data[7],
                }
                loan_list.append(loan_entry)
    except FileNotFoundError:
        print(f"\n❌ File {target_file} not found")
    return loan_list

############################################ FUNCTIONS MENU ############################################################

def menu_add_book():
    print("\n=== Add New Book ===")
    try:
        b_id = int(input("Enter Book ID: "))
        b_title = str(input("Enter Title: "))
        b_author = str(input("Enter Author: "))
        b_year = int(input("Enter Year: "))
        b_copies = int(input("Enter Copies: "))
        init_status = 1  

        add_book(b_id, b_title, init_status, b_author, b_year, b_copies)
        print(f"\n✅ Book '{b_title}' added successfully!")

    except ValueError:
        print("\n❌ Invalid input. Please enter valid information.")

def menu_delete_book(target_book_id, target_file="books.dat"):
    records = []
    is_found = False
    try:
        with open(target_file, "rb") as file_in:
            while True:
                raw_bytes = file_in.read(book_layout.size)
                if len(raw_bytes) < book_layout.size:
                    break
                unpacked_data = book_layout.unpack(raw_bytes)
                records.append(list(unpacked_data))
    except FileNotFoundError:
        print(f"\n❌ File {target_file} not found")
        return

    for item in records:
        if item[0] == target_book_id and item[2] == 1: 
            item[2] = 0  
            item[7] = int(time.time()) 
            is_found = True
            break

    if not is_found:
        print(f"\n❌ Book ID {target_book_id} not found or already deleted")
        return

    with open(target_file, "wb") as file_out:
        for item in records:
            packed_rec = book_layout.pack(*item)
            file_out.write(packed_rec)

    print(f"\n✅ Book ID {target_book_id} deleted successfully")

def menu_view_books(target_file="books.dat"):
    book_data = read_all_books(target_file)
    if not book_data:
        print("No books found.")
        return

    print("-" * 108)
    print(f"{'ID':<6} {'Title':<45} {'Author':<25} {'Year':<6} {'Copies':<7} {'Status':<8}")
    print("-" * 108)

    for item in book_data:
        status_str = "Active" if item['status'] == 1 else "Deleted"
        print(f"{item['book_id']:<6} {item['title']:<45} {item['author']:<25} {item['year']:<6} {item['copies']:<7} {status_str:<8}")

    print("-" * 108)

def menu_edit_book(target_file="books.dat"):
    menu_view_books()
    try:
        target_id = int(input("Enter Book ID to edit: "))
    except ValueError:
        print("\n❌ Invalid input. Please enter a number.")
        return

    book_records = []
    is_found = False
    try:
        with open(target_file, "rb") as file_in:
            while True:
                raw_bytes = file_in.read(book_layout.size)
                if len(raw_bytes) < book_layout.size:
                    break
                unpacked_data = book_layout.unpack(raw_bytes)
                book_records.append(list(unpacked_data))
    except FileNotFoundError:
        print(f"\n❌ File {target_file} not found")
        return

    for rec in book_records:
        if rec[0] == target_id and rec[2] == 1: 
            print(f"Editing Book ID {target_id}")
            new_title = input(f"Enter new Title [{rec[1].decode('utf-8').rstrip(chr(0))}]: ")
            new_author = input(f"Enter new Author [{rec[3].decode('utf-8').rstrip(chr(0))}]: ")
            try:
                input_year = input(f"Enter new Year [{rec[4]}]: ")
                new_year = int(input_year) if input_year else rec[4]
                input_copies = input(f"Enter new Copies [{rec[5]}]: ")
                new_copies = int(input_copies) if input_copies else rec[5]
            except ValueError:
                print("\n❌ Invalid number input. Edit canceled.")
                return

            rec[1] = new_title.encode("utf-8").ljust(50, b"\x00") if new_title else rec[1]
            rec[3] = new_author.encode("utf-8").ljust(30, b"\x00") if new_author else rec[3]
            rec[4] = new_year
            rec[5] = new_copies
            rec[7] = int(time.time())
            is_found = True
            break

    if not is_found:
        print(f"\n❌ Book ID {target_id} not found or not active")
        return

    with open(target_file, "wb") as file_out:
        for rec in book_records:
            packed_rec = book_layout.pack(*rec)
            file_out.write(packed_rec)

    print(f"\n✅ Book ID {target_id} updated successfully")

def menu_add_member():
    print("\n=== Add New Member ===")
    try:
        m_id = int(input("Enter Member ID: "))
        init_status = 1
        m_name = str(input("Enter Member Name: "))
        b_year = int(input("Enter Birth Year: "))
        default_max_loan = 5

        add_members(m_id, init_status, m_name, b_year, default_max_loan)
        print(f"\n✅ Member '{m_name}' added successfully!")

    except ValueError:
        print("\n❌ Invalid input. Please enter valid information.")

def menu_view_members(target_file="members.dat"):
    member_data = read_all_members(target_file)
    if not member_data:
        print("No members found.")
        return

    print("-" * 83)
    print(f"{'ID':<10} {'Name':<22} {'Birth Year':<17} {'Max Loan':<19} {'Status':<17}")
    print("-" * 83)

    for item in member_data:
        status_str = "Active" if item['status'] == 1 else "Deleted"
        print(f"{item['member_id']:<10} {item['name']:<22} {item['birth_year']:<17} {item['max_loan']:<19} {status_str:<17}")

    print("-" * 83)

def menu_edit_member(target_file="members.dat"):
    menu_view_members()
    try:
        target_id = int(input("Enter Member ID to edit: "))
    except ValueError:
        print("\n❌ Invalid input. Please enter a number.")
        return

    member_records = []
    is_found = False
    try:
        with open(target_file, "rb") as file_in:
            while True:
                raw_bytes = file_in.read(member_layout.size)
                if len(raw_bytes) < member_layout.size:
                    break
                unpacked_data = member_layout.unpack(raw_bytes)
                member_records.append(list(unpacked_data))
    except FileNotFoundError:
        print(f"\n❌ File {target_file} not found")
        return

    for rec in member_records:
        if rec[0] == target_id and rec[1] == 1:
            print(f"Editing Member ID {target_id}")
            new_name = input(f"Enter new Name [{rec[2].decode('utf-8').rstrip(chr(0))}]: ")
            try:
                input_birth = input(f"Enter new Birth Year [{rec[3]}]: ")
                new_birth = int(input_birth) if input_birth else rec[3]
                input_max = input(f"Enter new Max Loan [{rec[4]}]: ")
                new_max = int(input_max) if input_max else rec[4]
            except ValueError:
                print("\n❌ Invalid number input. Edit canceled.")
                return

            rec[2] = new_name.encode("utf-8").ljust(50, b"\x00") if new_name else rec[2]
            rec[3] = new_birth
            rec[4] = new_max
            rec[6] = int(time.time())  
            is_found = True
            break

    if not is_found:
        print(f"\n❌ Member ID {target_id} not found or not active")
        return

    with open(target_file, "wb") as file_out:
        for rec in member_records:
            packed_rec = member_layout.pack(*rec)
            file_out.write(packed_rec)

    print(f"\n✅ Member ID {target_id} updated successfully")

def menu_delete_member(target_member_id, target_file="members.dat"):
    member_records = []
    is_found = False
    try:
        with open(target_file, "rb") as file_in:
            while True:
                raw_bytes = file_in.read(member_layout.size)
                if len(raw_bytes) < member_layout.size:
                    break
                unpacked_data = member_layout.unpack(raw_bytes)
                member_records.append(list(unpacked_data))
    except FileNotFoundError:
        print(f"\n❌ File {target_file} not found")
        return

    for rec in member_records:
        if rec[0] == target_member_id and rec[1] == 1:
            rec[1] = 0 
            rec[6] = int(time.time()) 
            is_found = True
            break

    if not is_found:
        print(f"\n❌ Member ID {target_member_id} not found or already deleted")
        return

    with open(target_file, "wb") as file_out:
        for rec in member_records:
            packed_rec = member_layout.pack(*rec)
            file_out.write(packed_rec)

    print(f"\n✅ Member ID {target_member_id} deleted successfully")

def get_current_loans(loan_history):
    latest_state = {}
    for entry in loan_history:
        pair_key = (entry["book_id"], entry["member_id"])
        latest_state[pair_key] = entry

    active_loans = [item for item in latest_state.values() if item["is_rented_after"] == 1]
    return active_loans

def menu_borrow_book():
    print("\n=== Borrow Book ===")

    all_books = read_all_books("books.dat")
    all_members = read_all_members("members.dat")

    print("Available Books:")
    print("-" * 90)
    print(f"{'ID':<6} {'Title':<45} {'Copies':<8} {'Borrowed':<10} {'Available':<10}")
    print("-" * 90)

    loan_records = read_all_loans("loans.dat")
    active_loans = get_current_loans(loan_records)

    borrowed_counts = {
        book["book_id"]: sum(1 for loan in active_loans if loan["book_id"] == book["book_id"])
        for book in all_books
    }

    for book in all_books:
        if book["status"] == 1:
            currently_borrowed = borrowed_counts.get(book["book_id"], 0)
            available_qty = book["copies"] - currently_borrowed
            print(f"{book['book_id']:<6} {book['title']:<45} {book['copies']:<8} {currently_borrowed:<10} {available_qty:<10}")

    print("-" * 90)

    try:
        selected_book_id = int(input("Enter Book ID to borrow: "))
        selected_member_id = int(input("Enter Member ID: "))
    except ValueError:
        print("\n❌ Invalid input. Please enter numbers only.")
        return

    target_book = next((b for b in all_books if b["book_id"] == selected_book_id and b["status"] == 1), None)
    if not target_book:
        print(f"\n❌ Book ID {selected_book_id} not found or not active")
        return

    borrowed_now = borrowed_counts.get(selected_book_id, 0)
    if borrowed_now >= target_book["copies"]:
        print("\n❌ No copies available for this book")
        return

    target_member = next((m for m in all_members if m["member_id"] == selected_member_id and m["status"] == 1), None)
    if not target_member:
        print(f"\n❌ Member ID {selected_member_id} not found or not active")
        return

    start_date_str = datetime.now().strftime("%Y/%m/%d")
    due_date_str = (datetime.now() + timedelta(days=30)).strftime("%Y/%m/%d")

    add_loans(
        operation_code=1,      
        book_id=selected_book_id,
        member_id=selected_member_id,
        start_date=start_date_str,
        end_date=due_date_str,
        status_after=target_book["status"],
        is_rented_after=1
    )

    print(f"\n✅ Member '{target_member['name']}' borrowed '{target_book['title']}' until {due_date_str}")

def menu_return_book():
    print("\n=== Return Book ===")

    loan_records = read_all_loans("loans.dat")
    all_books = read_all_books("books.dat")
    all_members = read_all_members("members.dat")

    active_loans = get_current_loans(loan_records)

    if not active_loans:
        print("No books currently borrowed.")
        return

    print("-" * 97)
    print(f"{'BookID':<8} {'Title':<45} {'MemberID':<10} {'Member Name':<20} {'Loan Date':<10}")
    print("-" * 97)

    for item in active_loans:
        b_title = next((b["title"] for b in all_books if b["book_id"] == item["book_id"]), "Unknown")
        m_name = next((m["name"] for m in all_members if m["member_id"] == item["member_id"]), "Unknown")
        print(f"{item['book_id']:<8} {b_title:<45} {item['member_id']:<10} {m_name:<20} {item['loan_date']:<10}")

    print("-" * 97)

    try:
        selected_book_id = int(input("Enter Book ID to return: "))
        selected_member_id = int(input("Enter Member ID: "))
    except ValueError:
        print("\n❌ Invalid input. Please enter numbers only.")
        return

    target_loan = next((item for item in active_loans if item["book_id"] == selected_book_id and item["member_id"] == selected_member_id), None)
    if not target_loan:
        print("\n❌ No matching active loan found")
        return

    return_date_str = datetime.now().strftime("%Y/%m/%d")
    target_book = next((b for b in all_books if b["book_id"] == selected_book_id), None)

    add_loans(
        operation_code=2,      
        book_id=selected_book_id,
        member_id=selected_member_id,
        start_date=target_loan["loan_date"], 
        end_date=return_date_str,  
        status_after=target_book["status"] if target_book else 1,
        is_rented_after=0 
    )

    print(f"\n✅ Book ID {selected_book_id} has been returned by Member ID {selected_member_id}")

def menu_view_all_loans():
    loan_records = read_all_loans("loans.dat")
    all_books = read_all_books("books.dat")
    all_members = read_all_members("members.dat")

    if not loan_records:
        print("\nNo loans found.")
        return

    print("-" * 124)
    print(f"{'Timestamp':<20} {'BookID':<7} {'Title':<45} {'MemberID':<10} {'Member Name':<20} {'Type':<8} {'Status':<6}")
    print("-" * 124)

    for record in loan_records:
        b_title = next((b["title"] for b in all_books if b["book_id"] == record["book_id"]), "Unknown")
        m_name = next((m["name"] for m in all_members if m["member_id"] == record["member_id"]), "Unknown")
        action_type = "Borrow" if record["op_code"] == 1 else "Return"
        rental_status = "Borrowed" if record["is_rented_after"] == 1 else "Returned"

        print(f"{record['ts']:<20} {record['book_id']:<7} {b_title:<45} {record['member_id']:<10} {m_name:<20} {action_type:<8} {rental_status:<6}")

    print("-" * 124)

def menu_view_current_loans():
    loan_records = read_all_loans("loans.dat")
    active_loans = get_current_loans(loan_records)

    if not active_loans:
        print("\nNo books currently borrowed.")
        return

    all_books = read_all_books("books.dat")
    all_members = read_all_members("members.dat")

    print("\n=== Current Loans ===")
    print("-" * 97)
    print(f"{'BookID':<8} {'Title':<45} {'MemberID':<10} {'Member Name':<20} {'Loan Date':<10}")
    print("-" * 97)

    for item in active_loans:
        b_title = next((b["title"] for b in all_books if b["book_id"] == item["book_id"]), "Unknown")
        m_name = next((m["name"] for m in all_members if m["member_id"] == item["member_id"]), "Unknown")
        print(f"{item['book_id']:<8} {b_title:<45} {item['member_id']:<10} {m_name:<20} {item['loan_date']:<10}")

    print("-" * 97)

################################################ REPORT ################################################################

def gen_report(output_filename="report.pdf"):
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
        output_filename,
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
            book['title'],
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
    print(f"\n✅ PDF Report generated: {output_filename}")

################################################# MENU #################################################################

def main_menu():
    while True:
        print("\n=== Library Borrow System ===")
        print("1. Manage Books")
        print("2. Manage Members")
        print("3. Manage Loans")
        print("4. Generate report")
        print("5. Exit")
        user_choice = input("Select an option (1-5): ")

        if user_choice == "1":
            manage_books()
        elif user_choice == "2":
            manage_members()
        elif user_choice == "3":
            manage_loans()
        elif user_choice == "4":
            gen_report("report.pdf")
        elif user_choice == "5":
            gen_report("report.pdf")
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
        user_choice = input("Select an option (1-5): ")

        if user_choice == "1":
            menu_add_book()
        elif user_choice == "2":
            menu_view_books()
        elif user_choice == "3":
            menu_edit_book()
        elif user_choice == "4":
            menu_view_books()
            while True:
                try:
                    target_id = int(input("Enter Book ID: "))
                    menu_delete_book(target_id)
                    break
                except ValueError:
                    print("\n❌ Invalid input. Please enter a number.")
        elif user_choice == "5":
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

        user_choice = input("Select an option (1-5): ")
        if user_choice == "1":
            menu_add_member()
        elif user_choice == "2":
            menu_view_members()
        elif user_choice == "3":
            menu_edit_member()
        elif user_choice == "4":
            menu_view_members()
            while True:
                try:
                    target_id = int(input("Enter Member ID: "))
                    menu_delete_member(target_id)
                    break
                except ValueError:
                    print("\n❌ Invalid input. Please enter a number.")
        elif user_choice == "5":
            break
        else:
            print("\n❌ Invalid option! Please select 1-5.")

def manage_loans():
    while True:
        print("\n--- Manage Loans ---")
        print("1. Borrow Book")
        print("2. Return Book")
        print("3. View All Loans")
        print("4. Current Loans")
        print("5. Back to Main Menu")

        user_choice = input("Select an option (1-5): ")
        if user_choice == "1":
            menu_borrow_book()
        elif user_choice == "2":
            menu_return_book()
        elif user_choice == "3":
            menu_view_all_loans()
        elif user_choice == "4":
            menu_view_current_loans()
        elif user_choice == "5":
            break
        else:
            print("\n❌ Invalid option! Please select 1-5.")

################################################# MENU #################################################################

main_menu()