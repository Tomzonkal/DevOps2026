from flask import Flask, request, render_template_string

app = Flask(__name__)

# Gotowy szablon HTML z wbudowanym stylem CSS
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Chmurowy Kalkulator</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #eef2f3; margin: 0; }
        .calculator { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 8px 20px rgba(0,0,0,0.15); text-align: center; width: 350px; }
        h2 { color: #333; margin-bottom: 20px; font-size: 24px; }
        input[type="number"] { width: 80%; padding: 12px; margin: 10px 0; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; text-align: center; }
        select { width: 88%; padding: 12px; margin: 10px 0; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; background: #fff; cursor: pointer; }
        button { width: 88%; padding: 12px; background-color: #28a745; color: white; border: none; border-radius: 8px; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 15px; transition: 0.2s; }
        button:hover { background-color: #218838; }
        .result { margin-top: 25px; padding: 15px; background-color: #f8f9fa; border-radius: 8px; border-left: 5px solid #28a745; font-size: 20px; color: #333; font-weight: bold; word-break: break-all; }
    </style>
</head>
<body>
    <div class="calculator">
        <h2>Kalkulator AKS 422378 123456</h2>
        <form method="POST">
            <input type="number" name="num1" step="any" placeholder="Pierwsza liczba" required value="{{ num1 }}">
            <select name="operation">
                <option value="add" {% if op == 'add' %}selected{% endif %}>+ (Dodawanie)</option>
                <option value="sub" {% if op == 'sub' %}selected{% endif %}>- (Odejmowanie)</option>
                <option value="mul" {% if op == 'mul' %}selected{% endif %}>* (Mnożenie)</option>
                <option value="div" {% if op == 'div' %}selected{% endif %}>/ (Dzielenie)</option>
            </select>
            <input type="number" name="num2" step="any" placeholder="Druga liczba" required value="{{ num2 }}">
            <button type="submit">Oblicz</button>
        </form>
        
        {% if result is not none %}
            <div class="result">
                Wynik: {{ result }}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def calculator():
    result = None
    num1 = ''
    num2 = ''
    op = 'add'
    
    if request.method == 'POST':
        try:
            num1 = float(request.form['num1'])
            num2 = float(request.form['num2'])
            op = request.form['operation']
            
            if op == 'add':
                result = num1 + num2
            elif op == 'sub':
                result = num1 - num2
            elif op == 'mul':
                result = num1 * num2
            elif op == 'div':
                if num2 != 0:
                    result = num1 / num2
                else:
                    result = "Błąd: Dzielenie przez zero!"
            
            # Usuwamy końcówkę .0 dla liczb całkowitych, żeby ładniej wyglądało
            if isinstance(result, float) and result.is_integer():
                result = int(result)
                
        except Exception as e:
            result = "Błąd danych wejściowych"
            
    return render_template_string(HTML_TEMPLATE, result=result, num1=num1, num2=num2, op=op)

if __name__ == '__main__':
    # Aplikacja nadal działa na porcie 8080, zgodnym z Dockerem i Kubernetesem
    app.run(host='0.0.0.0', port=8080)