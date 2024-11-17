from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from http import HTTPStatus

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'library'

mysql = MySQL(app)

@app.route("/api/mysqlbooks", methods=["GET"])
def get_books():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM books")
        rows = cur.fetchall()

        column_names = ["id", "title", "author", "year"]
        result = []
        for row in rows:
            result.append(dict(zip(column_names, row)))

        return jsonify({"success": True, "data": result, "total": len(result)}), HTTPStatus.OK
    except:
        return jsonify({"success": False, "error": "Bad Request"}), HTTPStatus.BAD_REQUEST
    finally:
        cur.close()

@app.route("/api/mysqlbooks", methods=["POST"])
def add_book():
    if not request.is_json:
        return jsonify({"success": False, "error": "Content-type must be application/json"}), HTTPStatus.BAD_REQUEST

    data = request.get_json()

    required_fields = ["title", "author", "year"]
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "error": f"Missing required field: {field}"}), HTTPStatus.BAD_REQUEST

    try:
        cur = mysql.connection.cursor()
        cur.execute(f"INSERT INTO books(title, author, year) VALUES('{data["title"]}', '{data["author"]}', {data["year"]})")
        mysql.connection.commit()

        cur.execute("SELECT * FROM books WHERE id = LAST_INSERT_ID()")
        new_book = cur.fetchone()

        column_names = ["id", "title", "author", "year"]
        result = dict(zip(column_names, new_book))

        return jsonify({"success": True, "data": result}), HTTPStatus.CREATED
    except:
        return jsonify({"success": False, "error": "Bad Request"}), HTTPStatus.BAD_REQUEST
    finally: 
        cur.close()

@app.route("/api/mysqlbooks/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT * FROM books where id = {book_id}")
        book = cur.fetchone()

        if book is None:
            return jsonify({"success": False,"error": "Book not found"}), HTTPStatus.NOT_FOUND

        if not request.is_json:
            return jsonify({"success": False, "error": "Content-type must be application/json"}), HTTPStatus.BAD_REQUEST

        new_data = request.get_json()

        query = "UPDATE books SET "
        updated_value = []

        for data in new_data:
            updated_value.append(f"{data}='{new_data[data]}'")

        query += ", ".join(updated_value)
        query += f" WHERE id = {book_id}"

        cur.execute(query)
        mysql.connection.commit()

        cur.execute(f"SELECT * FROM books WHERE id = {book_id}")
        book = cur.fetchone()

        column_names = ["id", "title", "author", "year"]
        result = dict(zip(column_names, book))

        return jsonify({"success": True, "data": result}), HTTPStatus.CREATED
    except:
        return jsonify({"success": False, "error": "Bad Request"}), HTTPStatus.BAD_REQUEST
    finally: 
        cur.close()

@app.route("/api/mysqlbooks/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT * FROM books where id = {book_id}")
        book = cur.fetchone()

        if book is None:
            return jsonify({"success": False,"error": "Book not found"}), HTTPStatus.NOT_FOUND
        
        cur.execute(f"DELETE FROM books where id = {book_id}")
        mysql.connection.commit()

        return jsonify({"success": True, "message": f"Book with id: {book_id} was successfuly deleted"}), HTTPStatus.CREATED

    except:
        return jsonify({"success": False, "error": "Bad Request"}), HTTPStatus.BAD_REQUEST
    finally: 
        cur.close()

if __name__ == "__main__":
    app.run(debug=True)
