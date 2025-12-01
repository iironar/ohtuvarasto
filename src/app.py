import os
from flask import Flask, render_template, request, redirect, url_for, flash
from varasto import Varasto


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))


class WarehouseStore:
    def __init__(self):
        self.warehouses = {}
        self.id_counter = 1

    def get_next_id(self):
        current_id = self.id_counter
        self.id_counter += 1
        return current_id

    def get(self, warehouse_id):
        return self.warehouses.get(warehouse_id)

    def add(self, name, varasto):
        warehouse_id = self.get_next_id()
        self.warehouses[warehouse_id] = {
            'id': warehouse_id, 'name': name, 'varasto': varasto
        }
        return warehouse_id

    def delete(self, warehouse_id):
        if warehouse_id in self.warehouses:
            del self.warehouses[warehouse_id]


store = WarehouseStore()


def parse_float(value, default=0):
    try:
        return float(value) if value else default
    except ValueError:
        return None


@app.route('/')
def index():
    return render_template('index.html', warehouses=store.warehouses)


@app.route('/warehouse/create', methods=['GET', 'POST'])
def create_warehouse():
    if request.method == 'POST':
        return handle_create_warehouse()
    return render_template('create_warehouse.html')


def handle_create_warehouse():
    name = request.form.get('name', '').strip()
    tilavuus = parse_float(request.form.get('tilavuus'))
    alku_saldo = parse_float(request.form.get('alku_saldo'))

    error = validate_warehouse_input(name, tilavuus, alku_saldo)
    if error:
        flash(error, 'error')
        return render_template('create_warehouse.html')

    store.add(name, Varasto(tilavuus, alku_saldo))
    flash(f'Warehouse "{name}" created successfully', 'success')
    return redirect(url_for('index'))


def validate_warehouse_input(name, tilavuus, alku_saldo=0):
    if tilavuus is None:
        return 'Invalid capacity value'
    if alku_saldo is None:
        return 'Invalid initial balance value'
    if not name:
        return 'Name is required'
    if tilavuus <= 0:
        return 'Capacity must be positive'
    return None


@app.route('/warehouse/<int:warehouse_id>')
def view_warehouse(warehouse_id):
    warehouse = store.get(warehouse_id)
    if not warehouse:
        flash('Warehouse not found', 'error')
        return redirect(url_for('index'))
    return render_template('view_warehouse.html', warehouse=warehouse)


@app.route('/warehouse/<int:warehouse_id>/edit', methods=['GET', 'POST'])
def edit_warehouse(warehouse_id):
    warehouse = store.get(warehouse_id)
    if not warehouse:
        flash('Warehouse not found', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        return handle_edit_warehouse(warehouse, warehouse_id)
    return render_template('edit_warehouse.html', warehouse=warehouse)


def handle_edit_warehouse(warehouse, warehouse_id):
    name = request.form.get('name', '').strip()
    tilavuus = parse_float(request.form.get('tilavuus'))

    error = validate_edit_input(name, tilavuus)
    if error:
        flash(error, 'error')
        return render_template('edit_warehouse.html', warehouse=warehouse)

    warehouse['name'] = name
    warehouse['varasto'] = Varasto(tilavuus, warehouse['varasto'].saldo)
    flash(f'Warehouse "{name}" updated successfully', 'success')
    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


def validate_edit_input(name, tilavuus):
    if tilavuus is None:
        return 'Invalid capacity value'
    if not name:
        return 'Name is required'
    if tilavuus <= 0:
        return 'Capacity must be positive'
    return None


@app.route('/warehouse/<int:warehouse_id>/delete', methods=['POST'])
def delete_warehouse(warehouse_id):
    warehouse = store.get(warehouse_id)
    if not warehouse:
        flash('Warehouse not found', 'error')
        return redirect(url_for('index'))

    name = warehouse['name']
    store.delete(warehouse_id)
    flash(f'Warehouse "{name}" deleted successfully', 'success')
    return redirect(url_for('index'))


@app.route('/warehouse/<int:warehouse_id>/add', methods=['POST'])
def add_to_warehouse(warehouse_id):
    warehouse = store.get(warehouse_id)
    if not warehouse:
        flash('Warehouse not found', 'error')
        return redirect(url_for('index'))

    amount = parse_float(request.form.get('amount'))
    if amount is None or amount <= 0:
        flash('Amount must be a positive number', 'error')
        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))

    warehouse['varasto'].lisaa_varastoon(amount)
    flash(f'Added {amount} to warehouse', 'success')
    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


@app.route('/warehouse/<int:warehouse_id>/remove', methods=['POST'])
def remove_from_warehouse(warehouse_id):
    warehouse = store.get(warehouse_id)
    if not warehouse:
        flash('Warehouse not found', 'error')
        return redirect(url_for('index'))

    amount = parse_float(request.form.get('amount'))
    if amount is None or amount <= 0:
        flash('Amount must be a positive number', 'error')
        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))

    removed = warehouse['varasto'].ota_varastosta(amount)
    flash(f'Removed {removed} from warehouse', 'success')
    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
