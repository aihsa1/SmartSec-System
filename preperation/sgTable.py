import PySimpleGUI as sg
from bson import ObjectId
import datetime

headings = ['Name', 'Age', 'Job']
data = [
    ['Bob', '24', 'Engineer'],
    ['Sue', '40', 'Retired'],
    ['Joe', '32', 'Programmer'],
    ['Mary', '28', 'Teacher'],
]

# data = [[ObjectId('6252f0d6118784a746aa9475'), ['127.0.0.1', 57371], 'uint8', datetime.datetime(2022, 4, 10, 17, 59, 34, 571000)], [ObjectId('6252f0e2118784a746aa9476'), ['127.0.0.1', 57371], 'uint8', datetime.datetime(2022, 4, 10, 17, 59, 46, 481000)], [ObjectId('6252f17f0585945a344776bc'), ['127.0.0.1', 57430], 'uint8', datetime.datetime(2022, 4, 10, 18, 2, 23, 789000)], [ObjectId('6252f2195b802e4a2e0d5bc0'), ['127.0.0.1', 57487],
#                                                                                                                                                                                                                                                                                                                                                                                          'uint8', datetime.datetime(2022, 4, 10, 18, 4, 57, 427000)], [ObjectId('6252f2305b802e4a2e0d5bc1'), ['127.0.0.1', 57487], 'uint8', datetime.datetime(2022, 4, 10, 18, 5, 16, 797000)], [ObjectId('6252f2385b802e4a2e0d5bc2'), ['127.0.0.1', 57487], 'uint8', datetime.datetime(2022, 4, 10, 18, 5, 22, 675000)], [ObjectId('6252fbcf0273a2cba8e11739'), ['127.0.0.1', 56718], 'uint8', datetime.datetime(2022, 4, 10, 18, 46, 23, 133000)]]
# headings = ['_id', 'addr', 'dtype', 'date']

layout = [
    [
        sg.Column(
            [
                [sg.Table(
                    values=data,
                    headings=headings,
                    auto_size_columns=True,
                    expand_x=True,
                    display_row_numbers=True,
                    justification='center',
                    key="-TABLE-",
                    enable_events=True
                )]
            ]
        )
    ]
]

w = sg.Window('Table Demo', layout, size=(400, 400))

while True:
    event, values = w.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == '-TABLE-':
        i = values["-TABLE-"][0]
        print(i)
        info = dict(zip(headings, data[i]))
        sg.popup_no_buttons(info.__str__(
        ), title=f"info about {info['Name']}", image=sg.EMOJI_BASE64_HAPPY_BIG_SMILE)
    # print(event, values)
