from flask import Flask, render_template

app = Flask(__name__, template_folder="../templates/", static_folder="../static")

@app.route("/realtime")
def index():
	return render_template('index.html',)

@app.route("/map")
def map():
	return render_template('map.html',)

@app.route("/bound")
def bound():
	return render_template('bound.html',)



if __name__ == "__main__":
	app.run()