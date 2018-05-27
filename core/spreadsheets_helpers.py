def htmlColorToJSON(htmlColor):
    if htmlColor.startswith("#"):
        htmlColor = htmlColor[1:]
    return {"red": int(htmlColor[0:2], 16) / 255.0, "green": int(htmlColor[2:4], 16) / 255.0,
            "blue": int(htmlColor[4:6], 16) / 255.0}


class Sheet:
    def __init__(self, title: str):
        self.body = {
            'properties': {
                'sheetType': 'GRID',
                'title': title,
                'sheetId': 0,
                # 'gridProperties': {'rowCount': 8, 'columnCount': 5}
            },
            "data": []
        }
        self.rows_count = 0

    def addRow(self, titles=[], default_type="stringValue", default_color='#ffffff', default_width=200, types=[]):
        row = {
            "columnMetadata": [],
            "startRow": self.rows_count,
            "rowData": [{"values": []}]
        }
        for i in range(len(titles)):
            row['columnMetadata'].append({"pixelSize": default_width})
            type = types[i] if len(types) > i else default_type
            row['rowData'][0]["values"].append({
                "userEnteredValue": {
                    type: titles[i]
                },
                "userEnteredFormat": {
                    "backgroundColor": htmlColorToJSON(default_color)
                }
            })
        self.body["data"].append(row)
        self.rows_count += 1
        return self


class Table:
    def __init__(self, title: str):
        self.body = {
            "properties": {
                "title": title
            },
            "sheets": []
        }

    def addSheet(self, sheet: Sheet):
        self.body['sheets'].append(sheet.body)
        return self
