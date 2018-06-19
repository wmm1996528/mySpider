from flask import Flask, render_template


app = Flask(__name__)

@app.route('/')
def index():
    return 'This is Spider web!'

@app.route('/result')
def result():
    return render_template('result.html', url='asd.html')


if __name__ == '__main__':
    app.run(port=2121)