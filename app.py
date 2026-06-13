from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database configuration - Using CineBookingDB
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',  # Your password
    'database': 'CineBookingDB'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

# =====================================================================
# API ENDPOINTS
# =====================================================================

@app.route('/api/movies', methods=['GET'])
def get_movies():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT movie_id, title FROM Movie ORDER BY title")
        movies = cursor.fetchall()
        conn.close()
        return jsonify({'success': True, 'data': movies})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_users():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM User ORDER BY user_id DESC")
            users = cursor.fetchall()
            conn.close()
            return jsonify({'success': True, 'data': users})
        except Error as e:
            conn.close()
            return jsonify({'success': False, 'error': str(e)}), 500
            
    elif request.method == 'POST':
        data = request.json
        try:
            cursor.execute("""
                INSERT INTO User (name, email, phone) 
                VALUES (%s, %s, %s)
            """, (data['name'], data['email'], data.get('phone')))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return jsonify({'success': True, 'message': 'User created successfully', 'user_id': new_id})
        except Error as e:
            conn.close()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'PUT':
        data = request.json
        user_id = data.get('user_id')
        if not user_id:
            conn.close()
            return jsonify({'success': False, 'error': 'User ID required'}), 400
            
        try:
            cursor.execute("""
                UPDATE User SET name = %s, email = %s, phone = %s WHERE user_id = %s
            """, (data['name'], data['email'], data.get('phone'), user_id))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'User updated successfully'})
        except Error as e:
            conn.close()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        user_id = request.args.get('user_id')
        if not user_id:
            conn.close()
            return jsonify({'success': False, 'error': 'User ID required'}), 400
            
        try:
            cursor.execute("DELETE FROM Booking WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM User WHERE user_id = %s", (user_id,))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'User deleted successfully'})
        except Error as e:
            conn.close()
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bookings', methods=['GET', 'DELETE'])
def manage_bookings():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'GET':
        try:
            cursor.execute("""
                SELECT B.booking_id, U.name as user_name, M.title as movie_title, 
                       S.show_time, B.number_of_tickets, B.booking_date
                FROM Booking B
                INNER JOIN User U ON B.user_id = U.user_id
                INNER JOIN `Show` S ON B.show_id = S.show_id
                INNER JOIN Movie M ON S.movie_id = M.movie_id
                ORDER BY B.booking_id DESC
            """)
            bookings = cursor.fetchall()
            
            for booking in bookings:
                if booking.get('show_time'):
                    if isinstance(booking['show_time'], datetime):
                        booking['show_time'] = booking['show_time'].strftime('%Y-%m-%d %H:%M:%S')
                if booking.get('booking_date'):
                    if isinstance(booking['booking_date'], datetime):
                        booking['booking_date'] = booking['booking_date'].strftime('%Y-%m-%d %H:%M:%S')
            
            conn.close()
            return jsonify({'success': True, 'data': bookings})
        except Error as e:
            conn.close()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        booking_id = request.args.get('booking_id')
        if not booking_id:
            conn.close()
            return jsonify({'success': False, 'error': 'Booking ID required'}), 400
            
        try:
            cursor.execute("DELETE FROM Booking WHERE booking_id = %s", (booking_id,))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Booking cancelled successfully'})
        except Error as e:
            conn.close()
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/shows', methods=['GET'])
def get_shows():
    movie_id = request.args.get('movie_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        if movie_id:
            cursor.execute("""
                SELECT S.show_id, S.show_time, S.ticket_price, T.name as theatre_name
                FROM `Show` S
                INNER JOIN Theatre T ON S.theatre_id = T.theatre_id
                WHERE S.movie_id = %s
                ORDER BY S.show_time
            """, (movie_id,))
        else:
            cursor.execute("""
                SELECT S.show_id, M.title, S.show_time, S.ticket_price, T.name as theatre_name
                FROM `Show` S
                INNER JOIN Movie M ON S.movie_id = M.movie_id
                INNER JOIN Theatre T ON S.theatre_id = T.theatre_id
                ORDER BY S.show_time
            """)
        
        shows = cursor.fetchall()
        
        for show in shows:
            if show.get('show_time'):
                if isinstance(show['show_time'], datetime):
                    show['show_time'] = show['show_time'].strftime('%Y-%m-%d %H:%M:%S')
        
        conn.close()
        return jsonify({'success': True, 'data': shows})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bookings/create', methods=['POST'])
def create_booking_via_procedure():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
    cursor = conn.cursor(dictionary=True)
    data = request.json
    
    try:
        cursor.callproc('BookTicket', [data['user_id'], data['show_id'], data['number_of_tickets']])
        
        result = []
        for res in cursor.stored_results():
            result.extend(res.fetchall())
            
        conn.commit()
        conn.close()
        return jsonify({
            'success': True, 
            'message': 'Booking confirmed successfully!',
            'data': result
        })
    except Error as e:
        conn.close()
        return jsonify({
            'success': False, 
            'error': str(e), 
            'message': str(e)
        }), 400

@app.route('/api/shows/calculate-price', methods=['POST'])
def calculate_price_procedure():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
    cursor = conn.cursor()
    data = request.json
    try:
        args = [data['show_id'], data['number_of_tickets'], 0.00]
        result_args = cursor.callproc('CalculateTotalPrice', args)
        total_price = result_args[2]
        conn.close()
        return jsonify({'success': True, 'total_price': float(total_price)})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/queries/<int:query_id>', methods=['GET'])
def execute_system_query(query_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
    cursor = conn.cursor(dictionary=True)
    
    queries = {
        1: "SELECT * FROM Movie",
        2: "SELECT * FROM `Show` WHERE movie_id = %s",
        3: """SELECT B.booking_id, U.name, U.email, B.number_of_tickets 
              FROM Booking B
              INNER JOIN User U ON B.user_id = U.user_id""",
        4: """SELECT B.booking_id, M.title AS movie_title, T.name AS theatre_name, S.show_time
              FROM Booking B
              INNER JOIN `Show` S ON B.show_id = S.show_id
              INNER JOIN Movie M ON S.movie_id = M.movie_id
              INNER JOIN Theatre T ON S.theatre_id = T.theatre_id""",
        5: """SELECT M.title, COUNT(B.booking_id) AS total_bookings
              FROM Movie M
              LEFT JOIN `Show` S ON M.movie_id = S.movie_id
              LEFT JOIN Booking B ON S.show_id = B.show_id
              GROUP BY M.movie_id, M.title""",
        6: """SELECT M.title, COUNT(B.booking_id) AS total_bookings
              FROM Movie M
              INNER JOIN `Show` S ON M.movie_id = S.movie_id
              INNER JOIN Booking B ON S.show_id = B.show_id
              GROUP BY M.movie_id, M.title
              HAVING COUNT(B.booking_id) > 100""",
        7: """SELECT DISTINCT M.title, S.ticket_price 
              FROM Movie M
              INNER JOIN `Show` S ON M.movie_id = S.movie_id
              WHERE S.ticket_price > (SELECT AVG(ticket_price) FROM `Show`)""",
        8: """SELECT U1.user_id, U1.name, SUM(B1.number_of_tickets) AS tickets_booked
              FROM User U1
              INNER JOIN Booking B1 ON U1.user_id = B1.user_id
              GROUP BY U1.user_id, U1.name
              HAVING SUM(B1.number_of_tickets) > (
                  SELECT SUM(B2.number_of_tickets) FROM Booking B2 WHERE B2.user_id = %s
              )""",
        9: """SELECT M.title, B.booking_id 
              FROM Movie M
              LEFT JOIN `Show` S ON M.movie_id = S.movie_id
              LEFT JOIN Booking B ON S.show_id = B.show_id""",
        10: """SELECT S.show_id, S.show_time 
               FROM `Show` S
               WHERE NOT EXISTS (
                   SELECT 1 FROM Booking B WHERE B.show_id = S.show_id
               )"""
    }
    
    selected_query = queries.get(query_id)
    if not selected_query:
        conn.close()
        return jsonify({'success': False, 'error': 'Invalid query ID'}), 404
        
    try:
        if query_id == 2:
            movie_param = request.args.get('movie_id', 1)
            cursor.execute(selected_query, (movie_param,))
        elif query_id == 8:
            user_param = request.args.get('user_id', 1)
            cursor.execute(selected_query, (user_param,))
        else:
            cursor.execute(selected_query)
            
        result = cursor.fetchall()
        conn.close()
        return jsonify({'success': True, 'data': result})
    except Error as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)