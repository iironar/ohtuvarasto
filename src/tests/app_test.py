import unittest
from app import app, store


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        store.warehouses.clear()
        store.id_counter = 1

    def test_index_empty(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouses', response.data)
        self.assertIn(b'No warehouses yet', response.data)

    def test_create_warehouse_get(self):
        response = self.client.get('/warehouse/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create New Warehouse', response.data)

    def test_create_warehouse_post(self):
        response = self.client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '50'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Warehouse', response.data)
        self.assertEqual(len(store.warehouses), 1)

    def test_create_warehouse_empty_name(self):
        response = self.client.post('/warehouse/create', data={
            'name': '',
            'tilavuus': '100',
            'alku_saldo': '0'
        }, follow_redirects=True)
        self.assertIn(b'Name is required', response.data)

    def test_create_warehouse_invalid_capacity(self):
        response = self.client.post('/warehouse/create', data={
            'name': 'Test',
            'tilavuus': '-10',
            'alku_saldo': '0'
        }, follow_redirects=True)
        self.assertIn(b'Capacity must be positive', response.data)

    def test_view_warehouse(self):
        self.client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.get('/warehouse/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Warehouse', response.data)
        self.assertIn(b'Total Capacity', response.data)

    def test_view_warehouse_not_found(self):
        response = self.client.get('/warehouse/999', follow_redirects=True)
        self.assertIn(b'Warehouse not found', response.data)

    def test_edit_warehouse_get(self):
        self.client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '50'
        })
        response = self.client.get('/warehouse/1/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Warehouse', response.data)

    def test_edit_warehouse_post(self):
        self.client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '50'
        })
        response = self.client.post('/warehouse/1/edit', data={
            'name': 'Updated Warehouse',
            'tilavuus': '200'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Updated Warehouse', response.data)

    def test_delete_warehouse(self):
        self.client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '50'
        })
        self.assertEqual(len(store.warehouses), 1)
        response = self.client.post(
            '/warehouse/1/delete', follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(store.warehouses), 0)

    def test_add_to_warehouse(self):
        self.client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.post('/warehouse/1/add', data={
            'product_name': 'Apples',
            'amount': '30'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Added 30', response.data)
        self.assertEqual(store.get(1)['products']['Apples'], 30)

    def test_remove_from_warehouse(self):
        self.client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        self.client.post('/warehouse/1/add', data={
            'product_name': 'Oranges',
            'amount': '50'
        })
        response = self.client.post('/warehouse/1/remove', data={
            'product_name': 'Oranges',
            'amount': '20'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Removed 20', response.data)
        self.assertEqual(store.get(1)['products']['Oranges'], 30)

    def test_add_invalid_amount(self):
        self.client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '50'
        })
        response = self.client.post('/warehouse/1/add', data={
            'product_name': 'Bananas',
            'amount': '-10'
        }, follow_redirects=True)
        self.assertIn(b'Amount must be a positive number', response.data)

    def test_remove_invalid_amount(self):
        self.client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '50'
        })
        response = self.client.post('/warehouse/1/remove', data={
            'product_name': 'Grapes',
            'amount': '0'
        }, follow_redirects=True)
        self.assertIn(b'Amount must be a positive number', response.data)

    def test_create_multiple_warehouses(self):
        self.client.post('/warehouse/create', data={
            'name': 'Warehouse 1',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        self.client.post('/warehouse/create', data={
            'name': 'Warehouse 2',
            'tilavuus': '200',
            'alku_saldo': '100'
        })
        self.assertEqual(len(store.warehouses), 2)
        response = self.client.get('/')
        self.assertIn(b'Warehouse 1', response.data)
        self.assertIn(b'Warehouse 2', response.data)

    def test_edit_nonexistent_warehouse(self):
        response = self.client.get('/warehouse/999/edit', follow_redirects=True)
        self.assertIn(b'Warehouse not found', response.data)

    def test_delete_nonexistent_warehouse(self):
        response = self.client.post(
            '/warehouse/999/delete', follow_redirects=True
        )
        self.assertIn(b'Warehouse not found', response.data)

    def test_add_to_nonexistent_warehouse(self):
        response = self.client.post('/warehouse/999/add', data={
            'product_name': 'Mangoes',
            'amount': '10'
        }, follow_redirects=True)
        self.assertIn(b'Warehouse not found', response.data)

    def test_remove_from_nonexistent_warehouse(self):
        response = self.client.post('/warehouse/999/remove', data={
            'product_name': 'Peaches',
            'amount': '10'
        }, follow_redirects=True)
        self.assertIn(b'Warehouse not found', response.data)

    def test_add_multiple_products(self):
        self.client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        self.client.post('/warehouse/1/add', data={
            'product_name': 'Apples',
            'amount': '20'
        })
        self.client.post('/warehouse/1/add', data={
            'product_name': 'Oranges',
            'amount': '30'
        })
        warehouse = store.get(1)
        self.assertEqual(len(warehouse['products']), 2)
        self.assertEqual(warehouse['products']['Apples'], 20)
        self.assertEqual(warehouse['products']['Oranges'], 30)

    def test_add_same_product_twice(self):
        self.client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        self.client.post('/warehouse/1/add', data={
            'product_name': 'Apples',
            'amount': '20'
        })
        self.client.post('/warehouse/1/add', data={
            'product_name': 'Apples',
            'amount': '15'
        })
        warehouse = store.get(1)
        self.assertEqual(warehouse['products']['Apples'], 35)

    def test_remove_nonexistent_product(self):
        self.client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.post('/warehouse/1/remove', data={
            'product_name': 'NonExistent',
            'amount': '10'
        }, follow_redirects=True)
        self.assertIn(b'not found in warehouse', response.data)

    def test_remove_all_of_product(self):
        self.client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        self.client.post('/warehouse/1/add', data={
            'product_name': 'Apples',
            'amount': '20'
        })
        self.client.post('/warehouse/1/remove', data={
            'product_name': 'Apples',
            'amount': '20'
        })
        warehouse = store.get(1)
        self.assertNotIn('Apples', warehouse['products'])

    def test_add_without_product_name(self):
        self.client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.post('/warehouse/1/add', data={
            'product_name': '',
            'amount': '10'
        }, follow_redirects=True)
        self.assertIn(b'Product name is required', response.data)

    def test_remove_without_product_name(self):
        self.client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.post('/warehouse/1/remove', data={
            'product_name': '',
            'amount': '10'
        }, follow_redirects=True)
        self.assertIn(b'Product name is required', response.data)
