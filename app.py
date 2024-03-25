from flask import (Flask, render_template, redirect,
                   url_for, request, flash)
import json
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dasfgaojv834hjd7cg77'


def read_json(path):
    """Возвращает таблицу json по пути path"""
    with open(path, 'r') as file:
        data = json.load(file)
    return data


def write_json(path, data):
    """Записывает по пути path таблицу data формата json"""
    with open(path, 'w') as file:
        json.dump(data, file, indent=4)


def check_email_in_table(table, email):
    """Проверка есть ли в таблице table почта с названием email"""
    for item in table:
        if item['email'] == email:
            return True
    return False


@app.route('/users')
@app.route('/')
def main_page():
    """Главная страница в приложении"""

    users = read_json('users.json')
    return render_template('index.html', users=users)


@app.route('/delete-user/<string:email>', methods=['GET', 'DELETE'])
def delete_user(email):
    """Реализация удаления пользователя из таблицы по пути и по нажатию кнопки"""

    users = read_json('users.json')
    # Избавляемся от пользователя, которого удаляем
    users = [user for user in users if user['email'] != email]
    write_json('users.json', users)

    # Формируем различный ответ, если вызвали по ссылке или через кнопку
    if request.method == 'DELETE':
        return render_template('table.html', users=users)
    else:
        return redirect(url_for('main_page'))


@app.route('/create-user', methods=['POST'])
def create_user():
    """Реализация добавления пользователя в таблицу"""

    data = request.form.to_dict()
    users = read_json('users.json')

    # Проверяем есть ли пользователь в таблице
    # Почта выступает в качестве первичного ключа
    if not check_email_in_table(users, data['email']):
        user = {"first_name": data['first_name'],
                "last_name": data['last_name'],
                "email": data['email']
                }
        users.append(user)
        write_json('users.json', users)
        return render_template('table.html', users=users)
    else:
        # Формируем ответ на страничку, если почта уже используется
        flash("Данный пользователь уже в таблице")
        return render_template('table.html', users=users)


@app.route('/update-user', methods=['POST'])
def update_user():
    """Реализация изменения пользователя
     Состоит из двух частей: update_user и edit_row
     Данная функция нужна для применения изменений на сервере и отображения пользователю
     """

    data = request.form.to_dict()
    users = read_json('users.json')
    for user in users:
        if user['email'] == data['email']:
            user['first_name'] = data['first_name']
            user['last_name'] = data['last_name']
    write_json('users.json', users)
    return render_template('table.html', users=users)



@app.route('/edit_row/<int:id>', methods=['POST'])
def edit_row(id):
    """Первая часть изменения данных в таблице
    Необходима для отображения полей у пользователя для изменения данных
    """
    users = read_json('users.json')
    data = {
        "first_name": users[id]['first_name'],
        "last_name": users[id]['last_name'],
        "email": users[id]['email'],
        "id": f"{id + 1}"
    }
    return render_template('edit_row.html', data=data)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        host = sys.argv[1]
        port = int(sys.argv[2])
        app.run(debug=False, host=host, port=port)
    elif len(sys.argv) == 1:
        app.run(debug=False)
    else:
        print("Usage: python3 app.py <host> <port>")
