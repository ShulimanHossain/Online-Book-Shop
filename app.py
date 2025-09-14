from flask import Flask, render_template,request,redirect,url_for,jsonify,session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key='my_key_374'
mysql=MySQL (app)

@app.route('/',methods=['GET','POST'])
def home():
       cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
       try:
               cursor.execute("""SELECT * FROM v_top_selling_books """)
               topselling=cursor.fetchall()

               cursor.execute("""SELECT * FROM top_four_author""")
               topauthors=cursor.fetchall()

               cursor.execute("SELECT title, author_name, release_date FROM upcoming_books ORDER BY release_date ASC")
               upcoming_books = cursor.fetchall()
               allbook=[]
               if request.method=='POST' and request.form.get('allbook')=='allbook':
                    return redirect(url_for('all_book'))                   
       finally:
               cursor.close()
       return render_template("home.html",topselling=topselling,topauthors=topauthors,allbook=allbook,upcoming_books=upcoming_books)


@app.route('/book')
def all_book():
       cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
       try: 
            cursor.execute("""SELECT * FROM Books""")
            allbook=cursor.fetchall()
       finally:
            cursor.close()
       return render_template("all_book.html",allbook=allbook)

@app.route('/search',methods=['GET','POST'])
def search():
      message=""
      books=[]
      if request.method=='POST':
        bookname=request.form.get("bookname","").strip()
        authorname=request.form.get("authorname","").strip()
        
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if bookname and authorname: 
         try :
         
          cursor.execute( "SELECT b.*, a.name AS author_name  FROM Books b JOIN Authors a ON b.author_id=a.author_id WHERE b.title LIKE %s AND a.name LIKE %s""",(f"%{bookname}%",f"%{authorname}%"))
          books=cursor.fetchall()
         finally:
              cursor.close()
        elif not bookname  or not authorname:
              message="Please enter book name and author name both "
      return render_template("search_result.html",books=books,message=message)

@app.route('/loginoption',methods=['GET','POST'])
def loginoption():
      if request.method=='POST':
           role=request.form.get('role')
           if role=='login':
                return redirect(url_for('login'))
           elif role ==  'registration':
                return redirect(url_for('register'))
      return render_template('loginoption.html')
       

@app.route('/login',methods=['GET','POST'])
def login():
    message=''
    if request.method=='POST':
        userid_or_email=request.form['userid']
        password=request.form['password']
        role=request.form['role']

        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
             user=None
             if role == 'admin':
                    if userid_or_email.isdigit():  # If input is numeric, treat as user_id
                       cursor.execute('SELECT * FROM Admin WHERE admin_id = %s AND admin_password = %s',
                                   (int(userid_or_email), password))
                    else:  # Otherwise, treat as email
                     cursor.execute('SELECT * FROM Admin WHERE email = %s AND admin_password = %s',
                                   (userid_or_email, password))
                    user = cursor.fetchone()                          
             
             elif role=='member' :
                    if userid_or_email.isdigit():  # If input is numeric, treat as user_id
                       cursor.execute('SELECT * FROM Users WHERE user_id = %s AND user_password = %s',
                                   (int(userid_or_email), password))
                    else:  # Otherwise, treat as email
                     cursor.execute('SELECT * FROM Users WHERE email = %s AND user_password = %s',
                                   (userid_or_email, password))
                    user = cursor.fetchone()
             
             if user:
                 session['login'] = True
                 session['user_id'] = user['admin_id'] if role =='admin' else user['user_id']
                 session['username'] = user['admin_name'] if role == 'admin' else user['username']
                 session['role'] = role
                 
                 if role=='admin':
                      return redirect(url_for('admin_dashboard'))
                 else:
                     return redirect(url_for('member_dashboard'))
             else:
                 message = 'Incorrect ID/password'
        finally:
             cursor.close()      

    return render_template('login.html', message=message)

@app.route('/register',methods=['GET','POST'])
def register():
     message=''
     if request.method=='POST':
          name=request.form['name']
          email=request.form['email']
          contactnumber=request.form['contactnumber']
          password=request.form['password']
          cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
          try:
             cursor.execute("SELECT user_id FROM Users WHERE email=%s",(email,))
             user=cursor.fetchone()
             if user:
                  message="User already exists"
             else :
                  cursor.execute("INSERT INTO Users (username,email,phone_number,user_password) VALUES (%s,%s,%s,%s)",(name,email,contactnumber,password))
                  mysql.connection.commit()
                  message="Registration successfully done. Please login"
                  return redirect(url_for('login'))
          finally:
               cursor.close()
     return render_template('register.html',message=message)
               

     
@app.route('/admin',methods=['GET','POST'])
def admin_dashboard():
    if 'login' not in session or session['role']!='admin':
          return redirect (url_for('login'))
    message = request.args.get('message', None)    
          
    if request.method=='POST':
           option=request.form.get('option')
           if option=='revenue':
                return redirect(url_for('revenue'))
           elif option == 'add':
                return redirect(url_for('add'))
           elif option == 'delete':
                return redirect(url_for('delete'))
           elif option == 'changeprice':
                return redirect(url_for('changeprice'))
           elif option == 'updatestock':
                return redirect(url_for('updatestock'))
           elif option == 'userdetails':
                return redirect(url_for('userdetails'))
           elif option == 'orderdetails':
                return redirect(url_for('orderdetails'))
           elif option == 'changepass':
                return redirect(url_for('changepass'))
           
 
    return render_template('admin_dashboard.html',message=message)

@app.route('/admin/revenue')
def revenue():
     if 'login' not in session or session['role']!='admin':
           return redirect(url_for('login'))
     months=[]
     revenues=[]
     cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     try: 
            cursor.execute("SELECT * FROM v_revenue")
            result=cursor.fetchall()
            for row in result:
                 months.append(row['month'])
                 revenues.append(float(row['revenue']))
     finally:
               cursor.close()
     return render_template('revenue.html',action='revenue',months=months,revenues=revenues)
     

@app.route('/admin/add', methods=['GET','POST'])
def add():
     if 'login' not in session or session['role']!='admin':
           return redirect(url_for('login'))
     message=''
     newAuthor=False
     author_id=None
     book_id=None
     if request.method=='POST':
             title=request.form['name']
             author_name=request.form['author_name']
             author_email=request.form['author_email']
             isbn=request.form['isbn']
             price= request.form['price']
             published_date=request.form['published_date']
             stock=request.form['stock']
             cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
             try:
              cursor.execute("SELECT author_id FROM Authors WHERE email=%s",(author_email,))
              author=cursor.fetchone()

              if author: 
                   author_id=author['author_id']
                   cursor.execute("""INSERT INTO Books(title,isbn,price,published_date,stock,author_id)
                                   VALUES(%s,%s,%s,%s,%s,%s)""",(title,isbn,price,published_date,stock,author_id))
                   mysql.connection.commit()
                   book_id=cursor.lastrowid
                   
                   return redirect(url_for('admin_dashboard', message=f"BOOK Successfully added.New Book id is {book_id}"))                   
              else :
                   newAuthor=True
                   message = f"Author with email '{author_email}' does  not exist. Please enter new author information."
                   if 'nationality' in request.form and 'birth_date' in request.form :
                        
                    birth=request.form['birth_date']
                    nationality=request.form['nationality']
                    cursor.execute("""INSERT INTO Authors(name,email,nationality,birth_date)
                                   VALUES(%s,%s,%s,%s)""",(author_name,author_email,nationality,birth))
                    mysql.connection.commit()
                    author_id=cursor.lastrowid
                    cursor.execute("""INSERT INTO Books(title,isbn,price,published_date,stock,author_id)
                                   VALUES(%s,%s,%s,%s,%s,%s)""",(title,isbn,price,published_date,stock,author_id))
                    mysql.connection.commit()
                    book_id=cursor.lastrowid
                    
                    newAuthor=False
                    return redirect(url_for('admin_dashboard', message=f"New author and book added successfully. New Author id : {author_id} , Book id : {book_id}"))     
                   else :
                         
                         message = f"Author with email '{author_email}' does not exist. Please enter new author information."
             finally:
              cursor.close()
     return render_template('add_book.html',action='add',message=message,newAuthor=newAuthor,author_id=author_id ,book_id=book_id)

@app.route('/admin/delete', methods=['GET','POST'])
def delete():
      if 'login' not in session or session['role']!='admin':
          return redirect(url_for('login'))
      message=''
      if request.method=='POST':
           book_id=request.form['book_id']
           
           cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
           try:
            cursor.execute('DELETE FROM Books WHERE book_id=%s',(book_id,))
            mysql.connection.commit()
            message="Book deleted successfully"
           finally:
                cursor.close()
      return render_template('delete_book.html',action='delete',message=message)

@app.route('/admin/changeprice', methods=['GET','POST'])
def changeprice():
      if 'login' not in session or session['role']!='admin':
          return redirect(url_for('login'))
      message=''
      if request.method=='POST':
           book_id=request.form['book_id']
           newprice=request.form['newprice']
           cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
           try :
            cursor.execute('UPDATE Books SET price =%s WHERE book_id=%s ',(newprice,book_id))
            mysql.connection.commit()
            message="successfully changed price"
           finally:
                cursor.close()
      return render_template('change_price.html',action='changeprice',message=message)

@app.route('/admin/updatestock', methods=['GET','POST'])
def updatestock():
      if 'login' not in session or session['role']!='admin':
          return redirect(url_for('login'))
      message=''
      if request.method=='POST':
           book_id=request.form['book_id']
           newstock=request.form['newstock']
           cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
           try: 
            cursor.execute("UPDATE Books SET stock=%s WHERE  book_id=%s",(newstock,book_id))
            mysql.connection.commit()
            message="successfully update stock"
           finally:
                cursor.close()
      return render_template('update_stock.html',action='updatestock',message=message)

@app.route('/admin/userdetails', methods=['GET','POST'])
def userdetails():
     if 'login' not in session or session['role']!='admin':
           return redirect(url_for('login'))
     message=''
     userinfo=None
     if request.method=='POST':
             user_id=request.form['user_id']
             cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
             
             cursor.execute("SELECT * FROM v_user_order_details WHERE user_id LIKE %s ORDER BY order_date DESC",(user_id,))
             userinfo=cursor.fetchone()
             
     return render_template('user_details.html',action='userdetails',userinfo=userinfo)

@app.route('/admin/orderdetails')
def orderdetails():
     if 'login' not in session or session['role']!='admin':
           return redirect(url_for('login'))
    
     cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     cursor.execute("SELECT * FROM v_order_summary ORDER BY order_date DESC")
     orderinfo=cursor.fetchall()
             
     return render_template('order_details.html',action='orderdetails',orderinfo=orderinfo)

@app.route('/admin/changepass', methods=['GET','POST'])
def changepass():
     if 'login' not in session or session['role']!='admin':
           return redirect(url_for('login'))
     message=''
     
     if request.method=='POST':
             admin_id=request.form['admin_id']
             newpass=request.form['newpassword']
             cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
             cursor.execute('UPDATE Admin SET admin_password=%s WHERE admin_id=%s',(newpass,admin_id))
             mysql.connection.commit()
             message="Successfully changed password"
             
     return render_template('change_admin_pass.html',action='changepass',message=message)


@app.route('/member')
def member_dashboard():
    if 'login' not  in   session or session['role']!='member':
          return redirect(url_for("login"))
    
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try: 
        cursor.execute("SELECT * FROM v_user_info WHERE user_id=%s",(session['user_id'],))
        info=cursor.fetchone()
        cursor.execute("SELECT * FROM v_user_orders WHERE user_id=%s",(session['user_id'],))
        order_info=cursor.fetchall()
        cursor.execute('SELECT * FROM books')
        books=cursor.fetchall()
    finally:
     cursor.close()
    return render_template('member.html',user_info=info,order_info=order_info,cart=session.get("cart",[]),books=books)
    
    
@app.route('/addCart/<int:book_id>',methods=["POST"])
def addCart(book_id):
         if 'login' not  in   session or session['role']!='member':
          return redirect(url_for("login"))
         quantity=int(request.form.get("quantity",1))
         cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute("SELECT stock FROM books WHERE book_id=%s",(book_id,))
         book=cursor.fetchone()
         if not book:
              return "Book not found"
         if book["stock"]<quantity:
              return f"Not enough quantity"
         cart=session.get("cart",{})
         cart[str(book_id)]=cart.get(str(book_id),0)+quantity
         session["cart"]=cart
         return redirect(url_for("member_dashboard"))

@app.route('/review/<int:book_id>',methods=['GET','POST'])
def review(book_id):
              if 'login' not  in   session or session['role']!='member':
                      return redirect(url_for("login"))  
              message=""
              cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
              try :
                   cursor.execute("""SELECT order_details.* FROM Orders o JOIN Order_details order_details ON
                                  o.order_id=order_details.order_id 
                                  WHERE o.user_id = %s AND order_details.book_id=%s """,(session['user_id'],book_id))
                   result=cursor.fetchone()
                   if not result :
                        message="You can only review books you have buy"
                        return render_template("review.html",book_id=book_id,message=message)
                   if request.method=='POST':
                        rating=float(request.form['rating'])
                        review_text=request.form['review_text']
                        cursor.execute("""
                          INSERT INTO Review_book (user_id, book_id, rating, review_text)
                          VALUES (%s, %s, %s, %s)
                          ON DUPLICATE KEY UPDATE rating=%s, review_text=%s, review_date=CURRENT_TIMESTAMP
                         """, (session['user_id'], book_id, rating, review_text, rating, review_text))
                        cursor.execute("""UPDATE Books b SET b.rating =(SELECT ROUND(AVG(r.rating) , 2) FROM Review_book r WHERE r.book_id=b.book_id) WHERE b.book_id=%s""",(book_id,))
                        cursor.execute("""UPDATE Authors a JOIN Books b ON a.author_id=b.author_id SET a.rating =(SELECT ROUND(AVG(b2.rating) , 2) FROM Books b2  WHERE b2.author_id=a.author_id) WHERE b.book_id=%s""",(book_id,))
                        mysql.connection.commit()
                        message="Review submitted successfully"
              finally:
                   cursor.close()
              return render_template("review.html",book_id=book_id,message=message)

@app.route('/book_reviews/<int:book_id>')
def book_reviews(book_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # Get book details
        cursor.execute("SELECT * FROM Books b JOIN Authors a ON b.author_id = a.author_id WHERE b.book_id=%s", (book_id,))
        book = cursor.fetchone()

        if not book:
            return "Book not found"

        # Get all reviews for the book
        cursor.execute("""
            SELECT r.rating, r.review_text, r.review_date, u.username
            FROM Review_book r
            JOIN Users u ON r.user_id = u.user_id
            WHERE r.book_id = %s
            ORDER BY r.review_date DESC
        """, (book_id,))
        reviews = cursor.fetchall()
    finally:
        cursor.close()

    return render_template("book_reviews.html", book=book, reviews=reviews)


@app.route('/viewcart')
def viewcart():
         if 'login' not  in   session or session['role']!='member':
           return redirect(url_for("login"))     
         cart=session.get("cart",{})
         cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         totalBill=0
         if cart:
              placeholder=",".join(["%s"]*len(cart))
              cursor.execute(f"SELECT * FROM books WHERE book_id IN ({placeholder})",tuple(cart))
              cart_book=cursor.fetchall()
             
              for book in cart_book:
                   quantity=cart[str(book["book_id"])]
                   totalBill+=book["price"]*quantity
         else :
              cart_book=[]
         session['totalbill']=totalBill
         return render_template("cart.html",cart_book=cart_book,totalBill=totalBill)          

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # Book details
        cursor.execute("SELECT * FROM bookDetails  WHERE book_id=%s", 
                       (book_id,))
        book = cursor.fetchone()
        
        if not book:
            return "Book not found", 404
        
        # All reviews for this book
        cursor.execute("""SELECT * FROM bookDetailsReview 
                          WHERE book_id = %s""", 
                          (book_id,))
        reviews = cursor.fetchall()
        
    finally:
        cursor.close()
    
    return render_template('book_detail.html', book=book, reviews=reviews)

@app.route('/placeorder',methods=['POST'])
def placeorder():
     if 'login' not  in   session or session['role']!='member':
           return redirect(url_for("login")) 
     cart=session.get("cart",{})
     if not cart:
          return "Your cart is empty"
     totalBill=float(session.get('totalbill',0))
     cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     cursor.execute("INSERT INTO Orders (user_id,total_bill) VALUES (%s,%s)",(session["user_id"],totalBill))
     order_id=cursor.lastrowid
     for book_id,quantity in cart.items():
          cursor.execute("INSERT INTO Order_details (order_id,book_id,quantity) VALUES (%s,%s,%s)",(order_id,book_id,quantity))
     mysql.connection.commit()
     session["cart"]={}
     session["totalbill"]=0
     return f"Order placed successfully! Total bill :${totalBill:.2f}"

@app.route('/logout')
def logout(): 
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
