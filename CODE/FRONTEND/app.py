from flask import Flask,render_template,request,flash,session,redirect,url_for
app = Flask(__name__)
app.secret_key="dfjdjfdlkdkl"
import mysql.connector
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score




# Establishing a connection to the database
mydb = mysql.connector.connect(
    host="localhost",       
    user="root",        
    password="",    
    database="ransomeware",
    port=3306
    
)
mycursor = mydb.cursor()



@app.route('/')
def index():
    return render_template('index.html')



@app.route('/about')
def about():
    return render_template('about.html')




@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        conpass = request.form['conpass']
        number = request.form['number']
        if password == conpass:
            sql = 'SELECT * FROM user WHERE email=%s'
            val = (email,)
            mycursor.execute(sql, val)
            data = mycursor.fetchall()  
            if data:
                msg = 'Email already exists!'
                return render_template('registration.html', msg=msg)
            else:
                sql = 'INSERT INTO user (name, email, password,conpass, number) VALUES (%s, %s, %s, %s,%s)'
                val = (name, email, password,conpass, number)
                mycursor.execute(sql, val)
                mydb.commit()
                msg = 'Registered successfully'
                return render_template('login.html', msg=msg)
        else:
            msg = 'Passwords do not match!'
            return render_template('registration.html', msg=msg)
    return render_template('registration.html')
            

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        sql = 'SELECT * FROM user WHERE email=%s'
        val = (email,)
        mycursor.execute(sql, val)
        data = mycursor.fetchall()
        
        if data:
            if password == data[0][2]:
                return render_template('load.html')
            else:
                msg = 'Password does not match!'
                return render_template('login.html', msg=msg)
        else:
            msg = 'User with this email does not exist. Please register.'
            return render_template('login.html', msg=msg)
    else:
        return render_template('login.html')
                

    
df = None

@app.route('/load', methods=['GET', 'POST'])
def load():
    global df
    if request.method == 'POST':
        file = request.files['file']
        # Check if the file has a filename and is a CSV
        if file and file.filename.endswith('.csv'):
            try:
                df = pd.read_csv(file)
                flash('CSV file uploaded successfully.', 'success')
            except Exception as e:
                flash('Error uploading file. Please try again.', 'error')
        else:
            flash('Only CSV files are allowed.', 'error')
        return redirect(url_for('load'))
    return render_template('load.html')

# Route to view the data
@app.route('/viewdata')
def viewdata():
    # Load the dataset
    dataset_path = 'CTU-IoT-ramsomware -Capture-1-1conn.log.labeled.csv'  # Make sure this path is correct to the uploaded file
    df = pd.read_csv(dataset_path)
    df = df.head(1000)

    # Convert the dataframe to HTML table
    data_table = df.to_html(classes='table table-striped table-bordered', index=False)

    # Render the HTML page with the table
    return render_template('viewdata.html', table=data_table)


model_accuracies = {
    'Logistic Regression': 0.9950313242600993,
    'Naïve Bayes': 0.9887128024895772,
    'K Neighbors Classifier': 0.9988118908347948,
    'Support Vector Machine': 0.51819660261863,
    'Random Forest': 0.9999459751485684,
    'Gradient Boosting': 0.9998919794682228

    
}

@app.route('/model', methods=['GET', 'POST'])
def model():
    accuracy = None  # Variable to store the accuracy result
    selected_algorithm = None  # Store the selected algorithm
    if request.method == 'POST':
        selected_algorithm = request.form['algo']
        accuracy = model_accuracies.get(selected_algorithm, 'Not available')

    return render_template('model.html', model_accuracies=model_accuracies, accuracy=accuracy, selected_algorithm=selected_algorithm)

@app.route('/prediction',methods=['GET','POST'])
def prediction():
    if request.method == 'POST':
        Unnamed = int(request.form['Unnamed: 0'])
        id_orig_h = int(request.form['id.orig_h'])
        id_orig_p = int(request.form['id.orig_p'])
        id_resp_h = int(request.form['id.resp_h'])
        id_resp_p = int(request.form['id.resp_p'])
        proto = int(request.form['proto'])
        service = int(request.form['service'])
        duration = float(request.form['duration'])
        orig_bytes = float(request.form['orig_bytes'])
        resp_bytes = float(request.form['resp_bytes'])
        conn_state = int(request.form['conn_state'])
        missed_bytes = int(request.form['missed_bytes'])
        history = int(request.form['history'])
        orig_pkts = int(request.form['orig_pkts'])
        orig_ip_bytes = int(request.form['orig_ip_bytes'])
        resp_pkts = int(request.form['resp_pkts'])
        resp_ip_bytes = int(request.form['resp_ip_bytes'])
        df = pd.read_csv('cleaned_dataset.csv')
        # Separate features and target
        X = df.drop('label', axis=1)
        y = df['label']
        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        abc = [[Unnamed,id_orig_h, id_orig_p, id_resp_h, id_resp_p, proto, service, duration, orig_bytes, resp_bytes, conn_state, missed_bytes, history, orig_pkts, orig_ip_bytes, resp_pkts, resp_ip_bytes]]

        # Import LogisticRegression from sklearn
        from sklearn.linear_model import LogisticRegression

        # Create an instance of LogisticRegression model
        model = LogisticRegression(max_iter=1000)

        # Train the model using X_train and y_train
        model.fit(X_train, y_train)

        # Predict the class of the new instance
        result = model.predict(abc)

        # Check the prediction and print the corresponding label
        if result == 0:
            msg = 'Benign'
        else:
            msg = 'Malicious'
        return render_template('prediction.html',msg = msg)
    return render_template('prediction.html')



@app.route('/logout')
def logout():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)