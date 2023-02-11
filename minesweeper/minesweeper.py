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
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
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
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.

        mines are coodinated in (row, column), these are in 0 to (height or width)-1
        True: cell has a mine
        False: cell's status of a mine is unknown at worst
        """
        #print("#cells: ", len(self.cells), " count: ", self.count)
        if self.count == len(self.cells) and len(self.cells) > 0: #the total count of cells = the count
            #print("these are mines! ", self.cells)
            return self.cells

        """
        #this section doesn't work, cell is just (x,y)
        #it may not even be needed
        mines_found = []
        for index in self.cells:
            if index:#When true, index is a mine
                mines_found.append(index)#add the current indexed cell into the mine list
                print("cells index item: ", index)
        return mines_found#send the list of known mines
        """

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        temp_count = self.count
        temp_cells = self.cells

        safe_list = []
        """
        for index in temp_cells:
            #print("index in sentence known_safes: ", index)
            #it is just going through the elements of the sentence, so (1,6) is 1 then 6 for indx values

            if index:#When true, index is a mine
                #decrease count by 1
                temp_count = temp_count - 1
            else:#all non mines
                safe_list.append(index)
                #only non mines are added to this list
                #so they are either safe, or not yet known
        """
        if self.count == 0: #all the cells are safe in this sentance
            return self.cells
        if temp_count == 0: #the remaining cells are all safe in this sentence
            return safe_list

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        #print("in sentence, mark mine,")
        #print("cells array: ", self.cells, "Input cell: ", cell)
        for check_cell in self.cells.copy():
            if cell == check_cell:
                #removes it from the list IF it is in the cell list, as it is know to be a mine
                self.cells.remove(cell)
                self.count = self.count - 1#update the sentence now that one of the mines is removed

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        #print("in sentence, mark safe,")
        #print("cells array: ", self.cells, "Input cell: ", cell)
        for check_cell in self.cells.copy():
            if cell == check_cell:
                #print("removing a cell, ", cell)
                # removes it from the list IF it is in the cell list, as it is known to be safe adn is just cluttering
                self.cells.remove(cell)
                #i dont think there is anything to do with the count system here...


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
        # time to be sure there are no fake numbers now, IE (1,) or ()
        # its a jank fix, but i keep getting a "()" data set and im sot sure from what...
        self.moves_made.add(())
        for num in range(0, self.height):
            self.moves_made.add((num,))
        #for num in range(0, self.width):
            #self.moves_made.add((,))
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
        #print("AI mark_mine with a cell of: ", cell)
        if cell is not None:
            self.mines.add(tuple(cell))
            for sentence in self.knowledge:
                sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        #print("AI mark_safe with a cell of: ", cell)
        if cell is not None:
            self.safes.add(tuple(cell))
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
        #print("a move was made, the list should be updated")
        #print("       cell: ", cell)
        self.moves_made.add(tuple(cell))
        self.mark_safe(cell)

#region make sentence

        sentence_cells = set()#list of the adjacent cells to be made into the sentence...
        #may have to change it from [] if wrong data type
        i, j = cell#take in the coordinates
        for _i in range(3):
            cell_i = i + _i - 1 #the -2 are offsets, i don't know why range wouldnt use zeros before ...
            #print(cell_i)
            if cell_i >= 0 and cell_i < self.height:
                for _j in range(3):
                    cell_j = j + _j - 1
                    if cell_j >= 0 and cell_j < self.width:
                        if cell_i == i and cell_j == j:#this is to preven the center (the count base) from being in the sentence
                            pass
                        else:
                            send_cell = (cell_i, cell_j)
                            sentence_cells.add(tuple(send_cell))
                        #covers all adjacnet tiles that SHOULD exist on the board
# endregion make sentence

        temp_sent = Sentence(sentence_cells, count)#temporary sentence for this part in the loop
        #print("Sentence: ", temp_sent)
        self.knowledge.append(temp_sent)#add the new cell sentence to the knowledge
        pass#should do nothing, i want my regions to work

#region Safes and Mines
        #print("Updated knowledge: ", self.knowledge)
        copy_cells = temp_sent.known_safes()
        #print("known safes: ", copy_cells)
        if copy_cells != None:
            for item in copy_cells.copy():
                _i, _j = item
                #print("safe, _i: ", _i, " _j: ", _j)
                self.safes.add((_i, _j))#show this is a move that can be made
                self.mark_safe((_i, _j))
        copy_cells = temp_sent.known_mines()
        #print("known mines: ", copy_cells)
        if copy_cells != None:
            for item in copy_cells.copy():
                _i, _j = item
                mine_cell = (_i, _j)
                self.moves_made.add(tuple(mine_cell))  # this is so that the AI wont make a move on a mine
                # it will do this because it thinks it has already moved on that cell so it won't repeat
                # move_made works more as a way to say, "don't chose these tiles" which can be for a myriad of reasons
                #print("mine, _i: ", _i, " _j: ", _j)
                #self.mark_mine((_i, _j))
                self.mines.add(tuple(mine_cell))

#endregion Safes and Mines
        pass

#region Update Knowledge
        for up_sent in self.knowledge:
            #print("Updating this sentence: ", up_sent)
            temp_safe = up_sent.known_safes()
            if temp_safe != None:
                copy_safe = temp_safe.copy()
                for index in copy_safe:
                    up_sent.mark_safe(index)
                    self.safes.add(index)
            up_sent.mark_safe(cell)

            temp_mine = up_sent.known_mines()
            if temp_mine != None:
                copy_mine = temp_mine.copy()#here because python is weird...
                for index in copy_mine:
                    _i, _j = index
                    up_sent.mark_mine((_i, _j))
                    self.mines.add(index)

            #update the entire mines array inase one was somehow missed...
            for index in self.mines:
                _i, _j = index
                up_sent.mark_mine((_i, _j))

# endregion Update Knowledge
        pass

        #print("Safe moves:", self.safes)
        #print("Known mines post knowledge step: ", self.mines)
        #how will I get a new count to make noew infered sentances for #5... hmmmm
        #probably has to do with the set2 - set1 = count2 - count1
        #where set1 = count1 & set2 = count2
        #note that set1 is the subset of set2...

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        #print("safes:", self.safes)
        #print("moves made: ", self.moves_made)
        for move in self.safes:#known safe spaces in the board to move to
            if move not in self.moves_made:

                #print("Chosen Safe move: ", move)
                return move#send the move as the acion to take

        #in the entire san of the known safe states...
        return None#no new safe moves can be made

    def flag_mine(self, flags):
        #flags: set() of cells that are mines
        for mine in self.mines:
            if mine not in flags:
                flags.add(mine)
    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
#region V1
        """"
        check = False
        rand_cell = ()#touple?
        while check == False:#should only keep going if check is False
            check_val = 0
            i = random.randint(0, self.height - 1)
            j = random.randint(0, self.width - 1)
            rand_cell = (i, j)#touple of i and j
            for index in self.moves_made:
                if tuple(rand_cell) == index:#if it is already a made move...
                    check = False
                    check_val = 1
                    break
            for index in self.mines:
                if tuple(rand_cell) == index: #if the move is known to be on a mine...
                    check = False
                    check_val = 1
                    break
            if check_val == 0:
                print("a new random move has been found")
                check = True
        print("Chosen random move: ", rand_cell)
        if rand_cell in self.moves_made:
            print("Whoops, there is an error in checking this move has already been made")
        return rand_cell
        """
#endregion V1
        pass
#region V2
        pass
        #until i comment out v1, thsi shouldn't even run
        #print("V2 of random move has started")
        #make a for loop to act as a frontier for the random bias choosing
        move_options = set()
        for _i in range(0, self.height - 1 , 1):
            for _j in range(0, self.width - 1, 1):
                temp_cell = _i, _j
                move_options.add(tuple(temp_cell))

        #for loop of all made moves, remove all equivilent cells
        for made_move in self.moves_made:
            if made_move in move_options:
                move_options.remove(made_move)
                #this should be all:
                #mines, safe moves made, not the strange hang-up data (IE (, 1))
        for made_move in self.mines:
            if made_move in move_options:
                move_options.remove(made_move)
        pass
        chosen_random_move = ()  # change it later
        chosen_score = 100#absurdly large number so anything is a better move score

        for move_item in move_options:
            #check for adjacent tiles with counts
            move_options_score = 0
            move_i, move_j = move_item
            for _i in range(3):
                cell_i = move_i + _i - 1  # the -2 are offsets, i don't know why range wouldnt use zeros before ...
                # print(cell_i)
                if cell_i >= 0 and cell_i < self.height:
                    for _j in range(3):
                        cell_j = move_j + _j - 1
                        if cell_j >= 0 and cell_j < self.width:
                            for sent in self.knowledge:
                                #make a cell to check in sent
                                cell = (cell_i, cell_j)
                                if cell in sent.cells:  # this is to preven the center (the count base) from being in the sentence
                                    move_options_score += 1
                                    #now add more punishment if there is a non-zero count too
                                    move_options_score += sent.count

            if move_options_score < chosen_score:
                chosen_score = move_options_score
                chosen_random_move = move_item

                #make the new chosen move the first smallest move with a chosent score

        #make a system to prioritise cells with no nearby sentence data
#endregion V2
        #print("chosen move: ", chosen_random_move)
        return chosen_random_move