
import os
from flask import Flask, render_template, request, session, redirect, url_for
from models import db, User
from forms import SignupForm, LoginForm
import pandas as pd

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///finance'
db.init_app(app)

app.secret_key = "development-key"

@app.route("/")
def index():
  form = SignupForm()
  return render_template("index.html",form = form)

@app.route("/about")
def about():
  return render_template("about.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
  form = SignupForm()

  if request.method == "POST":
    if form.validate() == False:
      return render_template('signup.html', form=form)
    else:
      newuser = User(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
      db.session.add(newuser)
      db.session.commit()

      session['email'] = newuser.email
      return redirect(url_for('home'))

  elif request.method == "GET":
    return render_template('signup.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
  form = LoginForm()

  if request.method == "POST":
    if form.validate() == False:
      return render_template("index.html", form=form)
    else:
      email = form.email.data
      password = form.password.data

      user = User.query.filter_by(email=email).first()
      if user is not None and user.check_password(password):
        session['email'] = form.email.data
        return redirect(url_for('home'))
      else:
        return redirect(url_for('login'))

  elif request.method == 'GET':
    return render_template('index.html', form=form)

@app.route("/logout")
def logout():
  session.pop('email', None)
  return redirect(url_for('index'))

@app.route("/home", methods=["GET", "POST"])
def home():



  import pandas_datareader as pdr
  import csv
  import pandas
  import json
  from pandas_datareader.data import Options
  from datetime import date
  from sqlalchemy import create_engine

  stocks = ['AAPL','GOOGL', 'AMZN', 'FB', 'SSNLF', 'MSFT', 'SNE', 'IBM', 'NTDOY', 'ORCL', 'VMW', 'INTC', 'HPQ', 'DVMT',
  'CSCO', 'ADBE', 'SAP', 'LNVGY', 'RHT', 'SYMC', 'TWTR', 'ATNY', 'ACTS', 'ATVI', 'IOTS', 'ADRO', 'AMD', 'ADVS', 'ZBRA',
  'XPLR', 'XBIT', 'WIX', 'WBMD', 'VNOM', 'VIA', 'VECO', 'UPLD', 'UBNT', 'UFPT', 'TYME', 'TRIV', 'TRIP', 'TGA', 'TSI',
  'TESS', 'AIR', 'ATEN', 'AQN', 'DDD', 'WUBA', 'ASX', 'A', 'AYX', 'AMBR', 'AEE', 'BHE', 'BIO', 'CPL', 'CTS', 'CMI', 'DGI',
  'D', 'HEI', 'ASUR', 'AVID', 'EPAY', 'CBAK', 'CPSH', 'CYAN', 'DBVT', 'DELT', 'EDGW', 'XELA', 'FALC', 'SVVC', 'FBIO', 'GEOS',
  'QQQC', 'GPRO', 'MRVL', 'MZOR', 'BKFS', 'BA', 'CAJ', 'CRY', 'CUB', 'DGI', 'GME', 'GM', 'GNE', 'ASR', 'PAC', 'MDT',
  'MTD', 'MIXT', 'MULE', 'NC', 'NPTN', 'NXPI', 'NSTG', 'UEPS']

  stock_df = pdr.get_quote_yahoo(stocks)


  #s = Options('AAPL')._get_data_in_date_range(date.today())
  #print s
  stock_df.index.name = "StockSymbol"

  stock_df.to_csv("stock.csv")

  company_stock = pandas.read_csv("stock.csv")
  companies = pandas.read_csv("companies.csv")

  merged = company_stock.merge(companies, on = 'StockSymbol')
  merged['Amount'] = merged['last']*(merged['NumberofStocks']).astype(float)
  merged.columns = map(str.lower, merged.columns)
  merged.rename(columns = {'change_pct':'changepct','last':'lastprice','amount':'totalpricestocks','short_ratio' : 'shortratio'}, inplace = True)
  merged.to_csv('new_stock.csv', index=False)



  df = pd.read_csv('new_stock.csv')

  engine = create_engine('postgresql:///finance')
  df.to_sql('j', engine)

  return render_template("home.html")

if __name__ == "__main__":
  app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)),debug=True)
