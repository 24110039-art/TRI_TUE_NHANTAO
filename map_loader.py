def load_map(file_name):
    with open(f"maps/{file_name}", 'r') as f:
        return [line.strip() for line in f.readlines()]

def get_positions(grid):
    start, goal = None, None
    for y, row in enumerate(grid):
        for x, char in enumerate(row):
            if char == 'P': start = (x, y)
            if char == 'G': goal = (x, y)
    return start, goal