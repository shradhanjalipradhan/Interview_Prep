''' Statement
Given a 9 × 9 Sudoku board, determine whether it is valid. A board is considered valid if all of the following conditions hold (considering only the filled cells):

Each row contains the digits 1–9 at most once.

Each column contains the digits 1–9 at most once.

Each of the nine 3 × 3 sub-boxes contains the digits 1–9 at most once.

You do not need to check whether the Sudoku is solvable; only whether the current filled entries obey these rules.

Note:A partially filled Sudoku board can be valid even if it is not necessarily solvable. You only need to verify that the filled cells adhere to the given rules.'''



def isValidSudoku(board):
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]  

    for r in range(9):
        for c in range(9):
            val = board[r][c]

            if val == '.':
                continue

            box_idx = (r // 3) * 3 + (c // 3)

            if val in rows[r] or val in cols[c] or val in boxes[box_idx]:
                return False

            rows[r].add(val)
            cols[c].add(val)
            boxes[box_idx].add(val)

    return True
    
# Driver code
def main():
    boards = get_input_boards()
    
    for i, board in enumerate(boards):
      print(i+1, ".\tBoard: ")
      for row in board:
          print("\t\t", row)
        
      if(isValidSudoku(board)):
        print("\n\t Result: The board is valid.")
      else:
          print("\n\t Result: The board is invalid.")
      print("-"*100)

def get_input_boards():
    return [[['.','.','.','.','.','.','.','7','.'],
            ['2','7','5','.','.','.','3','1','4'],
            ['.','.','.','.','2','7','.','5','.'],
            ['9','8','.','.','.','.','.','3','1'],
            ['.','3','1','8','.','4','.','.','.'],
            ['.','.','.','1','.','.','8','.','5'],
            ['7','.','6','2','.','.','1','8','.'],
            ['.','9','.','7','.','.','.','.','.'],
            ['4','1','.','.','.','5','.','.','7']
        ],
        [
            ["5","3","3","6","7","8","9","1","2"],
            ["6","7","2","1","9","5","3","4","8"],
            ["1","9","8","3","4","2","5","6","7"],
            ["8","5","9","7","6","1","4","2","3"],
            ["4","2","6","8","5","3","7","9","1"],
            ["7","1","3","9","2","4","8","5","6"],
            ["9","6","1","5","3","7","2","8","4"],
            ["2","8","7","4","1","9","6","3","5"],
            ["3","4","5","2","8","6","1","7","9"]
        ],
        [
            ['6','4','5','9','8','2','1','3','7'],
            ['7','2','8','3','1','6','5','9','4'],
            ['3','9','1','5','4','7','6','8','2'],
            ['9','8','7','1','5','3','4','2','6'],
            ['4','1','6','2','7','9','8','5','3'],
            ['5','3','2','8','6','4','7','1','9'],
            ['8','7','3','6','9','5','2','4','1'],
            ['2','5','4','7','3','1','9','6','8'],
            ['1','6','9','4','2','8','3','7','5']
        ],
        [
            ['6','3','9','4','2','5','7','1','8'],
            ['6','4','8','1','3','7','9','6','5'],
            ['5','7','1','9','6','8','3','4','2'],
            ['1','6','2','7','5','4','8','3','9'],
            ['4','8','3','6','9','2','5','7','1'],
            ['9','5','7','3','8','1','6','2','4'],
            ['8','2','6','5','4','3','1','9','7'],
            ['3','1','5','2','7','9','4','8','6'],
            ['7','9','4','8','1','6','2','5','3']
        ],
        [
            ["5","3",".",".","7",".",".",".","."],
            ["6",".",".","1","9","5",".",".","."],
            [".","9","8",".",".",".",".","6","."],
            ["8",".",".",".","6",".",".",".","3"],
            ["4",".",".","8",".","3",".",".","1"],
            ["7",".",".",".","2",".",".",".","6"],
            [".","6",".",".",".",".","2","8","."],
            [".",".",".","4","1","9",".",".","5"],
            [".",".",".",".","8",".",".","7","9"]]]
          
if __name__ == '__main__':
    main()
