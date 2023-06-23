#IMPORTS
import PySimpleGUI as sg #Para a criação de telas/GUIs
import sqlite3 #Para a manipulação do banco de dados
import re #Para a criação de expressões regulares para validar campos


#---------------------------------------------------DELETE TABLE------------------------------------------------------
def open_drop_table():
    layout_drop_table = [
        [sg.Push(),sg.Text("Apagar todos os registros?", font=('Arial', 18, 'bold'), text_color="#106EBE"), sg.Push()],
        [sg.Push(), sg.Button("Sim", size=(14,0), key="sim", button_color="green"), sg.Button("Não", size=(14,0), key="nao"), sg.Push()]
    ]
    window_drop_table=sg.Window("Registros", layout_drop_table)
    while True:
        event, values = window_drop_table.read(timeout=250)
        if event == sg.WIN_CLOSED or event == "nao":
            break
        if event == "sim":
            db = sqlite3.connect("vendas.db")
            cursor = db.cursor()
            cursor.execute("DROP TABLE vendas")
            db.commit()
            db.close()

            db = sqlite3.connect("vendas.db")
            cursor = db.cursor()
            cursor.execute("CREATE TABLE vendas(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, produto VARCHAR(50) NOT NULL, cliente VARCHAR(50) NOT NULL, valor DECIMAL(5,5) NOT NULL, data DATE NOT NULL, pago CHAR(3));")
            db.commit()
            db.close()

            db = sqlite3.connect("vendas.db")
            cursor = db.cursor()
            cursor.execute("SELECT * FROM vendas;")
            result = cursor.fetchall()
            window_drop_table.close()
            sg.Popup('Limpeza efetuada com sucesso! A tabela agora está vazia', keep_on_top=True, title="Limpeza efetuada com sucesso!")
            return result
            
    window_drop_table.close()
#---------------------------------------------------DELETE CONFIRMATION------------------------------------------------------
def open_delete():
    layout_delete = [
        [sg.Push(),sg.Text("Excluir?", font=('Arial', 18, 'bold'), text_color="#106EBE"), sg.Push()],
        [sg.Push(), sg.Text("ID", size=(7,0), justification="center", font="14"), sg.Input(key="id_busca", size=(10,0), font="14", justification="center"), sg.Push()],
        [sg.Push(), sg.Button("Sim", size=(14,0), key="sim", button_color="green"), sg.Button("Não", size=(14,0), key="nao"), sg.Push()]
    ]
    window_delete=sg.Window("Registros", layout_delete)
    while True:
        event, values = window_delete.read(timeout=250)
        if event == sg.WIN_CLOSED or event == "nao":
            break
        if event == "sim":
            if not values['id_busca']:
                sg.Popup('Preencha todos os campos!', keep_on_top=True)
            else:
                if values['id_busca'].isnumeric() == False:
                    window_delete['id_busca'].update("")
                    sg.Popup('ID Deve ser numérico!', keep_on_top=True)
                else:
                    if int(values['id_busca']) <= 0:
                        sg.Popup('ID Inválido!', keep_on_top=True)
                    else:
                        id = int(values['id_busca'])

                        db = sqlite3.connect("vendas.db")
                        cursor = db.cursor()
                        cursor.execute("SELECT count(produto) FROM vendas WHERE id = ?;", (id,))
                        count = cursor.fetchall()

                        if int(count[0][0]) == 0:
                            window_delete['id_busca'].update("")
                            sg.Popup('ID Inexistente!', keep_on_top=True)
                        else:
                            db = sqlite3.connect("vendas.db")
                            cursor = db.cursor()
                            cursor.execute("DELETE FROM vendas WHERE id = ?;", (id,))
                            db.commit()
                            db.close()
                            window_delete['id_busca'].update("")

                            db = sqlite3.connect("vendas.db")
                            cursor = db.cursor()
                            cursor.execute("SELECT * FROM vendas;")
                            result = cursor.fetchall()
                            window_delete.close()
                            sg.Popup('Excluído com Sucesso! Acesse os Registros para visualizar', keep_on_top=True, title="Excluído com Sucesso")
                            return result
    window_delete.close()


#---------------------------------------------------WINDOW 2------------------------------------------------------
def open_window2(soma, window, result):
    layout = [
        [sg.Push(),sg.Text("Registros", font=('Arial', 18, 'bold'), text_color="#106EBE"), sg.Push()],
        [sg.Push(), sg.Table(result, headings=("ID", "PRODUTO", "CLIENTE", "VALOR", "DATA", "PAGO"), justification='center', key='-TABLE-', col_widths=(3, 28, 28, 8, 10, 6), auto_size_columns=False, vertical_scroll_only=False), sg.Push()],
        [sg.VPush()],
        [sg.Text(f"TOTAL R$: {soma[0][0]:.2f}" if soma[0][0] else  "TOTAL R$: 00.00", text_color="green", key="soma")],
        [sg.Push(), sg.Button("Voltar", size=(14,0), key="voltar"), sg.Button("Alterar", size=(14,0), key="alterar"), sg.Button("Excluir", size=(14,0), key="excluir"), sg.Button("Limpar Registros", size=(14,0), key="limpar_registros", button_color="red"), sg.Push()],
    ]
    window2=sg.Window("Registros", layout, size=(800,320))
    while True:
        event, values = window2.read(timeout=250)
        if event == sg.WIN_CLOSED:
            window.close()
            break
        if event == "excluir":
            window2["-TABLE-"].update(open_delete())
            db = sqlite3.connect("vendas.db")
            cursor = db.cursor()
            cursor.execute("SELECT SUM(valor) FROM vendas;")
            soma = cursor.fetchall()
            window2['soma'].update(f"TOTAL R$: {soma[0][0]:.2f}" if soma[0][0] else  "TOTAL R$: 00.00")
        if event == "voltar":
            break
        if event == "alterar":
            window2["-TABLE-"].update(open_window3(window, window2))
            db = sqlite3.connect("vendas.db")
            cursor = db.cursor()
            cursor.execute("SELECT SUM(valor) FROM vendas;")
            soma = cursor.fetchall()
            window2['soma'].update(f"TOTAL R$: {soma[0][0]:.2f}" if soma[0][0] else  "TOTAL R$: 00.00")
        if event == "limpar_registros":
            window2["-TABLE-"].update(open_drop_table())
            db = sqlite3.connect("vendas.db")
            cursor = db.cursor()
            cursor.execute("SELECT SUM(valor) FROM vendas;")
            soma = cursor.fetchall()
            window2['soma'].update(f"TOTAL R$: {soma[0][0]:.2f}" if soma[0][0] else  "TOTAL R$: 00.00")
    window2.close()

#---------------------------------------------------WINDOW 3------------------------------------------------------
def open_window3(window, window2):
    layout = [
        [sg.Push(),sg.Text("ALTERAR REGISTRO", font=('Arial', 18, 'bold'), text_color="#106EBE"), sg.Push()],
        [sg.Push(), sg.Text("ID", size=(7,0), justification="center", font="14"), sg.Input(key="id_busca", size=(10,0), font="14", justification="center"), sg.Button("Buscar", size=(10,0), key="buscar"), sg.Push()],
        [sg.VPush()],
        [sg.Push(), sg.Button("Voltar", size=(10,0), key="voltar"), sg.Button("Limpar", size=(10,0), key="limpar"), sg.Push()],
    ]
  
    window3=sg.Window("Alterar", layout, size=(800,320))
    while True:
        event, values = window3.read()
        if event == sg.WIN_CLOSED:
            window2.close()
            window.close()
            break
        if event == "limpar":
            window3['id_busca'].update("")
        if event == "voltar":
            break
        if event == "buscar":
            if not values['id_busca']:
                sg.Popup('Preencha todos os campos!', keep_on_top=True)
            else:
                if values['id_busca'].isnumeric() == False:
                    window3['id_busca'].update("")
                    sg.Popup('ID Deve ser numérico!', keep_on_top=True)
                else:
                    if int(values['id_busca']) <= 0:
                        sg.Popup('ID Inválido!', keep_on_top=True)
                    else:
                        id = int(values['id_busca'])

                        db = sqlite3.connect("vendas.db")
                        cursor = db.cursor()
                        cursor.execute("SELECT count(produto) FROM vendas WHERE id = ?;", (id,))
                        count = cursor.fetchall()

                        if int(count[0][0]) == 0:
                            window3['id_busca'].update("")
                            sg.Popup('ID Inexistente!', keep_on_top=True)
                        else:
                            db = sqlite3.connect("vendas.db")
                            cursor = db.cursor()
                            result = cursor.fetchall()

                            produto = cursor.execute("SELECT produto FROM vendas WHERE id = ?", (id,))
                            produto = cursor.fetchall()
                            cliente = cursor.execute("SELECT cliente FROM vendas WHERE id = ?;", (id, ))
                            cliente = cursor.fetchall()
                            valor = cursor.execute("SELECT valor FROM vendas WHERE id = ?;", (id,))
                            valor = cursor.fetchall()
                            data = cursor.execute("SELECT data FROM vendas WHERE id = ?;", (id,))
                            data = cursor.fetchall()
                            pago = cursor.execute("SELECT pago FROM vendas WHERE id = ?;", (id,))
                            pago = cursor.fetchall()

                            var = open_update_window(window, window2, window3, produto[0][0], cliente[0][0], valor[0][0], data[0][0], pago[0][0], id)
                            return var
    window3.close()

#---------------------------------------------------WINDOW 4------------------------------------------------------
def open_update_window(window, window2, window3, produto, cliente, valor, data, pago, id):
    layout_update = [
        [sg.Push(), sg.Push(),sg.Text("ALTERAR REGISTRO", font=('Arial', 18, 'bold'), text_color="#106EBE"), sg.Push()],
        [sg.Push(), sg.Text("Produto", size=(7,0), justification="center", font="14"), sg.Input(key="produto", size=(46,0), font="14", justification="center", default_text=produto), sg.Push()],
        [sg.Push(), sg.Text("Cliente", size=(7,0), justification="center", font="14"), sg.Input(key="cliente", size=(46,0), font="14", justification="center", default_text=cliente), sg.Push()],
        [sg.Push(), sg.Text("Valor", size=(7,0), justification="center", font="14"), sg.Input(key="valor", size=(46,0), font="14", justification="center", default_text=(f'{valor:.2f}')), sg.Push()],
        [sg.Push(), sg.Text("Data", size=(7,0), justification="center", font="14"), sg.Input(key="data", size=(46,0), font="14", justification="center", default_text=data), sg.Push()],
        [sg.Push(), sg.Text("Pago", size=(7,0), justification="center", font="14"),sg.Listbox(values=("SIM", "NAO"), size=(44,0), font="14", key="pago", highlight_background_color="#106EBE", default_values=pago), sg.Push()],
        [sg.VPush()],
        [sg.Push(), sg.Button("Cancelar", size=(10,0), key="voltar"), sg.Button("Salvar", size=(10,0), key="salvar"), sg.Button("Limpar", size=(10,0), key="limpar"), sg.Push()]
    ] 

    window_update=sg.Window("Alterar", layout_update, size=(800,320))
    while True:
        event, values = window_update.read()
        if event == sg.WIN_CLOSED:
            window3.close()
            window2.close()
            window.close()
            break
        if event == "voltar":
            window3.close()
            break
        if event == "limpar":
            window_update['produto'].update("")
            window_update['cliente'].update("")
            window_update['valor'].update("")
            window_update['data'].update("")
        if event == "salvar":
            if not values['produto'] or not values['cliente'] or not values['valor'] or not values['data'] or not values['pago']:
                sg.Popup('Preencha todos os campos!', keep_on_top=True)
            else:
                if not re.match(r"^[0-9]{1,5}\.[0-9]{2}$", values['valor']):
                    sg.Popup('Preencha o valor corretamente. Exemplo: 100.00', keep_on_top=True)
                else:
                    valor = float(values['valor'])
                    if not re.match(r"^[0-9]{2}/[0-9]{2}/[2][0][0-9][0-9]$", values['data']):
                        sg.Popup('Preencha a data corretamente. Exemplo: 17/06/2023', keep_on_top=True)
                    else:
                        data = values['data']
                        pago = values['pago']
                        produto = values['produto'].upper()
                        cliente = values['cliente'].upper()

                        db = sqlite3.connect("vendas.db")
                        cursor = db.cursor()
                        cursor.execute("UPDATE vendas SET produto=?, cliente=?, valor=?, data=?, pago=? WHERE id = ?;", (produto, cliente, valor, data, pago[0], id))
                        db.commit()
                        db.close()

                        window_update['produto'].update("")
                        window_update['cliente'].update("")
                        window_update['valor'].update("")
                        window_update['data'].update("")
                        window_update['produto'].set_focus()

                        db = sqlite3.connect("vendas.db")
                        cursor = db.cursor()
                        cursor.execute("SELECT * FROM vendas;")
                        result = cursor.fetchall()
                        window_update.close()
                        window3.close()
                        sg.Popup('Atualizado com Sucesso! Acesse os Registros para visualizar', keep_on_top=True, title="Atualizado com Sucesso")
                        return result
    window_update.close()



#------------------------------------------------MAIN WINDOW-----------------------------------------------------
sg.theme('Reddit')
layout = [
    [sg.Push(),sg.Text("NOVA VENDA", font=('Arial', 18, 'bold'), text_color="#106EBE"), sg.Push()],
    [sg.Push(), sg.Text("Produto", size=(7,0), justification="center", font="14"), sg.Input(key="produto", size=(46,0), font="14", justification="center"), sg.Push()],
    [sg.Push(), sg.Text("Cliente", size=(7,0), justification="center", font="14"), sg.Input(key="cliente", size=(46,0), font="14", justification="center"), sg.Push()],
    [sg.Push(), sg.Text("Valor", size=(7,0), justification="center", font="14"), sg.Input(key="valor", size=(46,0), font="14", justification="center"), sg.Push()],
    [sg.Push(), sg.Text("Data", size=(7,0), justification="center", font="14"), sg.Input(key="data", size=(46,0), font="14", justification="center"), sg.Push()],
    [sg.Push(), sg.Text("Pago", size=(7,0), justification="center", font="14"),sg.Listbox(values=("SIM", "NAO"), size=(44,0), font="14", key="pago", highlight_background_color="#106EBE"), sg.Push()],
    [sg.VPush()],
    [sg.Push(), sg.Button("Salvar", size=(10,0), key="salvar"), sg.Button("Limpar", size=(10,0), key="limpar"), sg.Button("Registros", size=(10,0), key="listar"), sg.Push()]
]

window=sg.Window("Vendas", layout, size=(800,320))
while True:
    event, values=window.read()
    if event==sg.WIN_CLOSED or event=="encerrar":
        break
    if event =="limpar":
        window['produto'].update("")
        window['cliente'].update("")
        window['valor'].update("")
        window['data'].update("")
        window['produto'].set_focus()
    if event=="salvar":
        if not values['produto'] or not values['cliente'] or not values['valor'] or not values['data'] or not values['pago']:
            sg.Popup('Preencha todos os campos!', keep_on_top=True)
        else:
            if not re.match(r"^[0-9]{1,5}\.[0-9]{2}$", values['valor']):
                sg.Popup('Preencha o valor corretamente. Exemplo: 100.00', keep_on_top=True)
            else:
                valor = float(values['valor'])
                if not re.match(r"^[0-9]{2}/[0-9]{2}/[2][0][0-9][0-9]$", values['data']):
                    sg.Popup('Preencha a data corretamente. Exemplo: 17/06/2023', keep_on_top=True)
                else:
                    data = values['data']
                    pago = values['pago']
                    produto = values['produto'].upper()
                    cliente = values['cliente'].upper()

                    db = sqlite3.connect("vendas.db")
                    cursor = db.cursor()
                    cursor.execute("INSERT INTO vendas(produto, cliente, valor, data, pago) VALUES(?, ?, ?, ?, ?);", (produto, cliente, valor, data, pago[0]))
                    db.commit()
                    db.close()

                    window['produto'].update("")
                    window['cliente'].update("")
                    window['valor'].update("")
                    window['data'].update("")
                    window['produto'].set_focus()
                    sg.Popup('Salvo com Sucesso! Acesse os Registros para visualizar', keep_on_top=True, title="Salvo com Sucesso")

                    db = sqlite3.connect("vendas.db")
                    cursor = db.cursor()
                    cursor.execute("SELECT SUM(valor) FROM vendas;")
                    soma = cursor.fetchall()

                    db = sqlite3.connect("vendas.db")
                    cursor = db.cursor()
                    cursor.execute("SELECT * FROM vendas;")
                    result = cursor.fetchall()

                    open_window2(soma, window, result)

    if event=="listar":
        db = sqlite3.connect("vendas.db")
        cursor = db.cursor()
        cursor.execute("SELECT SUM(valor) FROM vendas;")
        soma = cursor.fetchall()

        db = sqlite3.connect("vendas.db")
        cursor = db.cursor()
        cursor.execute("SELECT * FROM vendas;")
        result = cursor.fetchall()
        open_window2(soma, window, result)
window.close()
