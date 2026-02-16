import math

def calculate_weights(cols: int) -> list[float]:
    """
    Having allowed a number of columns between 2 and 8 included, calculate each column's weight 
    as equally as possible, with:

    - (1 / cols) for each one if the result is not a number with more than 2 decimal points 
      (i.e cols = 2 || 4 || 5).

    - Otherwise, the first K-1 number of columns will have a weight of (1 / cols) truncated to
      two decimal points while the Kth column will have the difference between 1 and the sum
      of all the previous weights as weight. To truncate decimal points and get an accurate 
      decimal difference, operations are made with the numbers being multiplied by 100 and 
      floored; then, results are divided by 100 to get the hundredth decimal parts again.

    Args:
        cols (int): The number of columns.
    
    Returns:
        list[float]: An ordered list containing the two-point float weights.
    """
    equals = 1 / cols

    if cols in (2, 4, 5):
        return [equals] * cols

    rest = math.floor(equals * 100)
    last = 100 - (rest * (cols - 1))

    weights = [rest / 100] * (cols - 1)
    weights.append(last / 100)

    return weights


def select_best_choice(results: dict[int,float]) -> tuple:
    """
    Select the item with the highest score and return (key, score)
    """
    return max(results.items(), key=lambda x: x[1])
