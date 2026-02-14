class Column:
    def __init__(self, title: str, weight: float, n_rows: int):
        self.title = title.capitalize()
        self.weight = weight
        self.values = [0] * n_rows

    def set_value(self, i: int, val: int):
        """
        Set a score in a cell given the row index (i) and value
        """
        if not (0 < val < 11):
            raise ValueError("Score must be between 1 and 10.")
        self.values[i] = val


class WeightedMatrix:
    def __init__(self):
        self.rows = 0
        self.cols = 0

        self.matrix: list[Column] = []
        self.items: dict[int,str] = {}

    def update_value(self, val: int, i: int, j: int):
        """
        Modifies the original matrix from memory by inserting the value in (i, j).
        """
        col = self.matrix[j-1]
        col.set_value(i-1, val)

    def insert_column(self, attribute: str, weight: int):
        """
        Insert a new column at the end of the original matrix
        """
        if self.cols < 8:
            self.matrix.append(Column(attribute, weight, self.rows))
            self.cols += 1
        else:
            raise IndexError('You can only add up to 8 columns.')

    def delete_column(self, j: int):
        """
        Delete a column by its number
        """
        if self.cols > 2:
            self.matrix.pop(j-1)
            self.cols -= 1
        else:
            raise IndexError('There must be at least 2 columns in the matrix.')

    def update_column_attr(self, j: int, attr: str):
        """
        Update a column's attribute reference (title) by its number (j) and capitalize it.
        """
        self.matrix[j-1].title = attr.capitalize()

    def update_column_weight(self, j: int, weight: float):
        """
        Update a column's weight by its number (j).
        """
        self.matrix[j-1].weight = weight
        
    def insert_row(self, item: str):
        """
        Insert a new blank row at the end of the original matrix
        """
        if self.rows < 8:
            # Update all columns
            for col in self.matrix:
                rows = col.values
                rows.append(0)

            last_row_idx = self.rows
            self.rows += 1
            
            self.items[last_row_idx] = item.capitalize()
        else:
            raise IndexError('You can only add up to 8 rows.')

    def delete_row(self, i: int):
        """
        Delete a row by its number
        """
        if self.rows > 2:
            idx = i-1
            for col in self.matrix:
                rows = col.values
                rows.pop(idx)

            self.rows -= 1
            self.items.pop(idx) # Remove the item

            # Shift indices starting from the one after the deleted one (skips if it was the last one)
            for n in range(idx + 1, self.rows + 1):
                self.items[n - 1] = self.items.pop(n)
        else:
            raise IndexError('There must be at least 2 rows in the matrix.')

    def update_row(self, i: int, item: str):
        """
        Update a row's item reference (title) by its number (i) and capitalize it.
        """
        idx = i-1
        self.items[idx] = item.capitalize()

    def compute_scores(self) -> dict[int,float]:
        """
        Make the weighted sum of each row and map the row index to the score accumulatively
        """

        if not _is_full_matrix(self.matrix):
            raise ValueError('The matrix is incomplete. Fill all the cells to calculate the scores.')
        
        scores = {i: 0 for i in range(self.rows)} # Initiate scores dict with zeros

        for col in self.matrix:
            rows = col.values
            for i, val in enumerate(rows):
                scores[i] += val * col.weight

        scores = {key: round(val, 1) for key, val in scores.items()} # Round results to 1 decimal point
        return scores


def _is_full_matrix(matrix: list[Column]) -> bool:
    """
    Validate that the input matrix has all cells completed.
    """
    for col in matrix:
        if not all(col.values): # If any row in any column contains zeros
            return False
    return True


def _weights_add_up(matrix: list[Column]) -> bool:
    """
    Validate that current columns add up to 1; not more nor less.
    """
    res = sum([col.weight for col in matrix])
    if res != 1:
        return False
    return True