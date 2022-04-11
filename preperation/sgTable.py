import PySimpleGUI as sg

headings = ['Name', 'Age', 'Job']
data = [
    ['Bob', '24', 'Engineer'],
    ['Sue', '40', 'Retired'],
    ['Joe', '32', 'Programmer'],
    ['Mary', '28', 'Teacher'],
]
layout = [
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

w = sg.Window('Table Demo', layout, size=(400, 400))

while True:
    event, values = w.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == '-TABLE-':
        i = values["-TABLE-"][0]
        print(i)
        info = dict(zip(headings, data[i]))
        sg.popup_no_buttons(info.__str__(), title=f"info about {info['Name']}", image=sg.EMOJI_BASE64_HAPPY_BIG_SMILE)
    # print(event, values)
