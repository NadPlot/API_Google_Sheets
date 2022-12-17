import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials


# Создаем Сервис-объект для работы с Google-таблицами
CREDENTIALS_FILE = 'managesheet-371909-eeba38bd209f.json'  # имя файла с закрытым ключом, полученый при создании Сервисного аккаунта

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                                                                  'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)  # Сервис-объект для работы с Google-таблицами


# Создание нового документа Google-таблицы
spreadsheet = service.spreadsheets().create(body = {
    'properties': {'title': 'Logs', 'locale': 'ru_RU'},
    'sheets': [{'properties': {'sheetType': 'GRID',
                               'sheetId': 0,
                               'title': 'Sheet01',
                               'gridProperties': {'rowCount': 8, 'columnCount': 5}}}]
}).execute()


# Предоставление доступа на чтение к новому документу
driveService = apiclient.discovery.build('drive', 'v3', http = httpAuth)
shareRes = driveService.permissions().create(
    fileId = spreadsheet['spreadsheetId'],
    body = {'type': 'anyone', 'role': 'writer'},  # доступ на редактирование кому угодно
    fields = 'id'
).execute()


# Заполнение таблицы данными
results = service.spreadsheets().values().batchUpdate(spreadsheetId = spreadsheet['spreadsheetId'], body = {
    "valueInputOption": "USER_ENTERED",
    "data": [
        {"range": "Sheet01!A1:A1",
         "values": [["Логи кластера №1"]]},
    ]
}).execute()


