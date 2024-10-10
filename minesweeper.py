import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        """
        Checks if a given cell is a mine.
        """
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell is in bounds and is a mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been found.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        """
        Checks if two sentences are equal.
        """
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        """
        String representation of the sentence.
        """
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # If the number of cells equals the count, all cells must be mines
        if len(self.cells) == self.count:
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If the count is zero, all cells must be safe
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # Step 1: Mark the cell as a move made
        self.moves_made.add(cell)

        # Step 2: Mark the cell as safe
        self.mark_safe(cell)

        # Step 3: Create a new sentence based on neighbors
        neighbors = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) != cell and 0 <= i < self.height and 0 <= j < self.width:
                    neighbors.add((i, j))

        new_sentence_cells = neighbors - self.mines - self.safes
        new_sentence_count = count - len(neighbors & self.mines)
        new_sentence = Sentence(new_sentence_cells, new_sentence_count)
        self.knowledge.append(new_sentence)

        # Step 4: Update knowledge (mark additional cells as safe or mines)
        self.update_knowledge()

    def update_knowledge(self):
        """
        Goes through all knowledge to identify new safe or mine cells.
        Removes empty sentences from the knowledge base and generates inferences.
        """
        updated = False

        # Mark safe and mine cells from current knowledge
        for sentence in self.knowledge:
            safe_cells = sentence.known_safes()
            mine_cells = sentence.known_mines()

            for safe in safe_cells.copy():
                self.mark_safe(safe)
                updated = True
            for mine in mine_cells.copy():
                self.mark_mine(mine)
                updated = True

        # Remove empty sentences from knowledge
        self.knowledge = [s for s in self.knowledge if len(s.cells) > 0]

        # Infer new sentences from existing knowledge
        new_inferences = []
        for s1 in self.knowledge:
            for s2 in self.knowledge:
                if s1 != s2 and s1.cells.issubset(s2.cells):
                    new_cells = s2.cells - s1.cells
                    new_count = s2.count - s1.count
                    new_sentence = Sentence(new_cells, new_count)
                    if new_sentence not in self.knowledge and new_sentence not in new_inferences:
                        new_inferences.append(new_sentence)
                        updated = True

        if new_inferences:
            self.knowledge.extend(new_inferences)

        # Recursively update if knowledge was changed
        if updated:
            self.update_knowledge()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        """
        safe_moves = self.safes - self.moves_made
        return safe_moves.pop() if safe_moves else None

    def make_random_move(self):
        """
        Returns a random move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        choices = [(i, j) for i in range(self.height) for j in range(self.width)
                   if (i, j) not in self.moves_made and (i, j) not in self.mines]
        return random.choice(choices) if choices else None
