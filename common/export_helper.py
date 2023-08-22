import csv
import json
import xlsxwriter
from gridfs import GridFS
from pymongo import MongoClient

STORAGE_PATH = "/home/MeghalragVijayan/Documents/QBurst/Workspace/flask_apps/employee_management_system"
client = MongoClient('mongodb://localhost:27017/')
db = client['employee_management']
fs = GridFS(db, collection='employee_export')  # GridFS collection for exported files


def export_to_csv_and_save(users):
    csv_data = []
    csv_data.append(["Name", users.name])
    csv_data.append(["Email", users.email])
    csv_data.append(["Phone Number", users.phone_number])
    csv_data.append(["Designation", users.designation])
    csv_data.append(["Department", users.department])
    csv_data.append(["Manager", users.manager])
    csv_data.append(["Joined Date", str(users.hired_date)])

    csv_file = f'{STORAGE_PATH}/user_details.csv'
    
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_data)

    with open(csv_file, 'rb') as file:
        file_id = fs.put(file, filename=csv_file, content_type='text/csv')
    return file_id

def export_to_xlsx_and_save(users):
    xlsx_file = f'{STORAGE_PATH}/user_details.xlsx'
    workbook = xlsxwriter.Workbook(xlsx_file)
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold': True})
    worksheet.write('A1', 'Name', bold)
    worksheet.write('A2', 'Email', bold)
    worksheet.write('A3', 'Phone Number', bold)
    worksheet.write('A4', 'Designation', bold)
    worksheet.write('A5', 'Department', bold)
    worksheet.write('A6', 'Manager', bold)
    worksheet.write('A7', 'Joined Date', bold)

    row = 1
    # for user in users:
    #     worksheet.write(row, 1, user.email)
    #     worksheet.write(row, 2, user.phone_number)
    #     row += 1
    worksheet.write('B1', users.name)
    worksheet.write('B2', users.email)
    worksheet.write('B3', users.phone_number)
    worksheet.write('B4', users.designation)
    worksheet.write('B5', users.department)
    worksheet.write('B6', users.manager)
    worksheet.write('B7', str(users.hired_date))

    workbook.close()

    with open(xlsx_file, 'rb') as file:
        file_id = fs.put(file, filename=xlsx_file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    return file_id

def export_to_json_and_save(users):
    json_file = f'{STORAGE_PATH}/user_details.json'
    user_data = [
        {"Name": users.name},
        {"Email": users.email},
        {"Phone Number": users.phone_number},
        {"Designation": users.designation},
        {"Department": users.department},
        {"Manager": users.manager},
        {"Joined Date": str(users.hired_date)}
    ]
    with open(json_file, 'w') as jsonfile:
        json.dump(user_data, jsonfile, indent=4)

    with open(json_file, 'rb') as file:
        file_id = fs.put(file, filename=json_file, content_type='application/json')
    
    return file_id