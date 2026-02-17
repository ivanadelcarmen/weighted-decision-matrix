import unittest
import random

from src.core.weighted_matrix import (
    WeightedMatrix,
    Column,
    _is_full_matrix,
    _weights_add_up
)


class TestColumnObjects(unittest.TestCase):
    def test_column_init(self):
        title = 'color'
        weight = 0.3
        n_rows = 4

        col = Column(title, weight, n_rows)
        self.assertEqual(col.values, [0] * n_rows)
        self.assertEqual(col.weight, weight)
        self.assertEqual(col.title, title.capitalize())
    
    def test_column_set_value(self):
        n_rows = 4
        col = Column('color', 0.3, n_rows)
        # Generate random numbers for each row between 1 and 10
        random_nums = [random.randint(1,10) for _ in range(n_rows)]

        for i, num in enumerate(random_nums): # Row indexes, so start from 0
            col.set_value(i, num)
        
        self.assertEqual(col.values, random_nums)


class TestWeightedMatrices(unittest.TestCase):
    def test_matrix_init(self):
        matrix = WeightedMatrix()
        self.assertEqual(matrix.cols, 0)
        self.assertEqual(matrix.rows, 0)
        self.assertEqual(matrix.matrix, [])
        self.assertEqual(matrix.items, {})

    def test_insert_row(self):
        matrix = WeightedMatrix()
        matrix.insert_row('item1') # Names are capitalized
        matrix.insert_row('item2')

        self.assertEqual(matrix.rows, 2)
        self.assertEqual(len(matrix.items), 2)
        self.assertEqual(matrix.items, {0: 'Item1', 1: 'Item2'})

    def test_update_row(self):
        matrix = WeightedMatrix()
        matrix.items[0] = 'Option1'
        matrix.update_row(1, 'first option')

        self.assertEqual(matrix.items[0], 'First option')

    def test_insert_column(self):
        matrix = WeightedMatrix()
        matrix.rows = 4 # Add 4 rows to each column

        matrix.insert_column('texture', 0.3) # Names are capitalized
        matrix.insert_column('taste', 0.5)
        matrix.insert_column('color', 0.2)
        
        self.assertEqual(matrix.cols, 3)
        self.assertEqual(len(matrix.matrix), 3)

        titles_cap = ['Texture','Taste','Color']
        for j, col in enumerate(matrix.matrix):
            self.assertEqual(len(col.values), matrix.rows)
            self.assertFalse(all(col.values)) # Check all values are 0
            self.assertEqual(col.title, titles_cap[j])
    
    def test_update_columns(self):
        matrix = WeightedMatrix()
        matrix.matrix.append(Column('example1', 0, 3))
        matrix.matrix.append(Column('example2', 0, 3))
        
        matrix.update_column_attr(2, 'column')
        matrix.update_column_weight(1, 0.5)

        self.assertEqual(matrix.matrix[1].title, 'Column')
        self.assertEqual(matrix.matrix[0].weight, 0.5)

    def test_delete_row(self):
        matrix = WeightedMatrix()

        # Insert 4 rows
        matrix.insert_row('fst')
        matrix.insert_row('snd')
        matrix.insert_row('trd')
        matrix.insert_row('fth')

        matrix.insert_column('color', 0.4)
        matrix.insert_column('texture', 0.6)

        matrix.delete_row(2)

        self.assertEqual(matrix.rows, 3)
        self.assertEqual(matrix.items, {0: 'Fst', 1: 'Trd', 2: 'Fth'})
        for col in matrix.matrix:
            self.assertEqual(len(col.values), 3)

    def test_delete_column(self):
        matrix = WeightedMatrix()
        matrix.insert_column('fst', 0.2)
        matrix.insert_column('snd', 0.4)
        matrix.insert_column('trd', 0.4)

        matrix.delete_column(2)
        self.assertEqual(len(matrix.matrix), 2)

    def test_update_value(self):
        matrix = WeightedMatrix()
        matrix.insert_row('fst')
        matrix.insert_row('snd')
        matrix.insert_column('color',0.3)
        matrix.insert_column('texture',0.7)

        values = [3,5,7,6]
        matrix.update_value(3,1,1)
        matrix.update_value(5,2,1)
        matrix.update_value(7,1,2)
        matrix.update_value(6,2,2)
        
        idx = 0
        for col in matrix.matrix:
            for val in col.values:
                self.assertEqual(val, values[idx])
                idx += 1
    
    def test_compute_scores(self):
        matrix = WeightedMatrix()
        matrix.insert_row('fst')
        matrix.insert_row('snd')
        matrix.insert_column('color',0.3)
        matrix.insert_column('texture',0.7)

        matrix.update_value(3,1,1)
        matrix.update_value(5,2,1)
        matrix.update_value(7,1,2)
        matrix.update_value(6,2,2)
        # Now the matrix looks like: [[3,5], [7,6]], where inner lists are columns

        scores = matrix.compute_scores()
        self.assertEqual(len(matrix.items), len(scores))
        self.assertTrue(list(scores.keys()) == [0,1])
        self.assertEqual(scores[0], round((3*0.3)+(7*0.7), 1))
        self.assertEqual(scores[1], round((5*0.3)+(6*0.7), 1))


class TestMatrixValidations(unittest.TestCase):
    def test_matrix_full(self):
        n = 3
        k = 4
        matrix = []
        for _ in range(k): # Add k columns with n rows
            col = Column('',0,n)
            matrix.append(col)
            for idx in range(n):
                col.set_value(idx, random.randint(1,10))

        self.assertTrue(_is_full_matrix(matrix))

    def test_matrix_not_full(self):
        n = 3
        k = 4
        matrix = []
        for _ in range(k): # Add k columns with n rows
            col = Column('',0,n)
            matrix.append(col)
            for idx in range(n-1):
                # Using range(n-1), the last row in each col will still have zeros
                col.set_value(idx, random.randint(1,10))

        self.assertFalse(_is_full_matrix(matrix))

    def test_weights_right(self):
        n = 3
        matrix = []
        matrix.append(Column('',0.3,n))
        matrix.append(Column('',0.5,n))
        matrix.append(Column('',0.2,n))

        self.assertTrue(_weights_add_up(matrix))

    def test_weights_wrong(self):
        n = 3
        matrix = []
        matrix.append(Column('',0.3,n))
        matrix.append(Column('',0.2,n))
        matrix.append(Column('',0.3,n))
        self.assertFalse(_weights_add_up(matrix)) # sum < 1

        matrix.append(Column('',0.6,n))
        self.assertFalse(_weights_add_up(matrix)) # sum > 1


if __name__ == '__main__':
    unittest.main(verbosity=2)