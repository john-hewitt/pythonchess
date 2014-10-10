#No running as an executable
#-------------------------------------------------------------------------------
# Author: John Hewitt
# Version: 1.0 -- 1/10/13
# Copyright John Hewitt
#
#   This work is licensed under the Creative Commons Attribution
#   NonCommercial-ShareAlike 3.0 Unported License. To view a 
#   copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/
#   or send a letter to Creative Commons, 444 Castro Street, Suite 900,
#   Mountain View, California, 94041, USA.
#-------------------------------------------------------------------------------

#IN PLACE OF A README:
# user inputs a five-character string. First two characters- number and letter
# pertaining to the square that the piece lies on. Third- a dash "-" or other 
# symbol (arbitrary). Fourth and fifth- the number and letter pertaining to the
# target square.
# EX.   Knight at E5 to D7 :   E5-D7  -OR-  e5-d7  -OR-  E5_d7


#Known Bugs/ To do:
# 1)King can only be put in check by a piece 6 squares or less away
## 2)Bishop movement function flawed somehow.
## 3)Non-perfect user input crashes program
## 4)Chess board does not look like a chess board -- PARTIAL FIX #3
# 4A)Rasterization needs overhauling. Board needs to
#      be bigger, the squares need to be color-coded, and the pieces need
#      to be color-coded by team. 
# 5)All functions need docstrings/code needs cleaning up
## 6)Pawns can take pieces directly in front of them. -- FIX #4
## 7)Pieces can take other pieces of the same team. -- FIX # 5
## 8)Players can not yet declare checkmate -- FIX # 7
# 9)Users must somehow be taught how to play.
## 10)It's generally just really buggy.
##d1-a4 11)Queen's movement function needs to be revised. -- FIX #2
# 12)Add Debug Mode
## 13)Add coordinates to sides of board -- FIX #3
## 14)Knight can only move abs(x)=1 abs(y)=2
##15)Trying to move a piece from a square with no piece crashes program -- Fix #6

# ------FIXED BUGS------
##1/5/13
# 1)Rook movement function fixed
# 2)Queen movement function fixed
# 3)Board made legible, coordinates added
# 4)Pawn movement function fixed
# 5)Players can no longer take own pieces, or move pieces of other team
# 6)Program no longer crashes when unoccupied space accessed
# 7)Player can now admit checkmate
# 8)Queen's movement function re-fixed 7/29/13
# 9)Board more readable- divided into colored squares. 7/30/30

#-----Latest Work--------
# 8/4/13: Started work on AI, added unicode charaters for Linux, OSX machines


import sys
import curses
import random

class Logic(object):
    def __init__(self):
        self.board = None
        self.moveSuccess = False
        self.AIActivated = False
        
    def initAI(self, whitePieces,blackPieces, stdscr):
        self.AI = AI(self.board, whitePieces, blackPieces, stdscr)
        self.AIActivated = True
        
    def decypherInput(self,string):
        '''Sterilizes and normalizes the user input. Currently, it is very 
        weak, and input must be perfect to prevent an unhandled exception.'''
        
        if string == "b'debug'":
            pass
        
        if string == "b'ckmte'":
            raise EndGame
        
        characters = ['','','','','','','','']
        
        itn = 0
        for x in string:
            characters[itn] = x
            itn += 1
        
                

        
        coordDict = {'A':0, 'B':1, 'C':2, 'D':3, 'E':4, 'F':5, 'G':6, 'H':7,
                     'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7,
                     '1':0, '2':1, '3':2, '4':3, '5':4, '6':5, '7':6, '8':7 }

        initialx = coordDict[characters[2]]
        initialy = coordDict[characters[3]]
        targetx = coordDict[characters[5]]
        targety = coordDict[characters[6]]
        

            
        return initialx, initialy, targetx, targety
        
        
        
    def playerMove(self):
        '''Called by the run() function, takes input and sends it to be 
        decyphered. Then calls the move() function of the piece. If king
        is in check, replaces piece and calls itself for the user to move again.'''
        #Let the people know whose turn it is!
        
        self.moveFailed = False
        
        if self.color == False:
            self._displayText('White Team\'s turn.')
        if self.color == True:
            self._displayText('Black Team\'s turn.')
        
        # Get that 5-character string, decypher it, then make sure
        # that there's actually a piece there, before moving it!
        move = self.userInput()
        try:
            initialx, initialy,targetx,targety =self.decypherInput(move)
        except KeyError:
            self._displayText('                     Key Error. Move again.')
            self.moveFailed = True
            return
            
        if self.board[initialx][initialy].occ ==False:
            self._displayText('                     Move again- no piece in initial square.')
            self.moveFailed = True
            return
            
        #No cheatin, trying to move the other team's pieces.
        if self.board[initialx][initialy].piece.black != self.color:
            self._displayText('                     Move again- piece is not on own team.  ')
            self.moveFailed = True
            return
            
        #But hold up, what you're trying to take a piece
        #that's actually yours? Can't have that.
        if self.board[targetx][targety].occ == True:
            if self.board[targetx][targety].piece.black == self.color:
                self._displayText('                     Move again- cannot take own piece. ')
                self.moveFailed = True
                return
            
        piece = self.board[initialx][initialy].piece
        self.movepiece(piece, targetx, targety)
        
        try:
            self.kingInCheck(self.color)
        except KingCheck:
            self.replacePiece(piece)
            self._displayText('King is in check.    King in check. \'ckmte\' to forfeit.   ')
            self.playerMove()

        if self.moveFailed != True:
            self.moveSuccess = True

    def run(self):
        '''Runs game logic. Loops until an unhandled exception of admitting
        checkmate comes up.'''
        self.color = False
        while True:
            
            #First Player's Turn
            self._updateDisplay()
            while self.moveSuccess != True:
                self.playerMove()  #White team turn
            self.color = True
            self.moveSuccess = False
            self._updateDisplay()  #display isn't updated until legal move move
            
            #Second Player - or AI - Turn
            while self.moveSuccess == False:                    
                self.playerMove()     # Black team turn
            self.color = False
            self._updateDisplay()
            self.moveSuccess = False

                    
    def userInput(self):
        '''Calls the GUI userinput function, and makes sure the string
        recieved is 5 characters long. If the AI has been activated, it checks to see if it is the AI's turn. If it is, it accepts the movement string from the AI.'''
        
        if self.color == False or self.AIActivated == False:
            userinput = self._userInput()
            if userinput is str:
                if len(userinput) != 5:
                    self._displayText('                     Invalid input. Move again.')
                    self.userInput()
            return str(userinput)
        else:
            AIinput = self.AI.calculateMove()
            return AIinput

    
            
    def registerGuiMethods(self, userInput, displayText, updateDisplay):
        '''Well, it registers the GUI methods. That's just about it.'''
        self._userInput = userInput
        self._displayText = displayText
        self._updateDisplay = updateDisplay
        
    
                
    def kingInCheck(self, teamColor):
        '''Before the game starts and at the end of every turn,
        1. check if either king is in check
        2. if either king is in check, check to see if checkmate
        3. set the self.occ to False for
         all squares with self.piece = None '''
        
        #If there's no piece on the square, this cleans up any errors 
        #for x in self.board:
            #for y in x:
                #if y.piece == None:
                    #y.occ = False
                
        #Now we've got to decide whether either king is in check. Sigh.
        if teamColor == False:
            playerTurn = 'white'
        else:
            playerTurn = 'black'
        
        # First off, check if the black king is in check. [1]The pieces of the
        # board are sorted through until the king is found. [2]Then, the king's
        # coordinates are used for reference in deciding if a piece could
        # be putting it in check.

        for v in self.board:
            for w in v:
                if w.piece != None and w.piece.name == 'king' and w.piece.black == teamColor: #[1]
                 #   print('king found', w.piece.loc, w.piece.black)
                    
                    x, y = w.piece.loc[0], w.piece.loc[1] #[2]
                    

                    
                    # A check for queens or bishops first. If a queen or bishop
                    # is found, a check to see if there is a piece blocking the
                    # way is done.
                    
                    #Alright, this may be the most unreadable, gross pile of
                    #code ever to disgrace my poor IDE. Lemme try to explain it.
                    #in order to find any queen or bishop within any diagonal of
                    #the king, locations of value [x+n][y+n], [x+n][y-n],
                    #[x-n][y+n], and [x-n][y-n] must be considered. The lists
                    #below itx (iterate-x) and ity allow for each of the four
                    #cases, without four diffrent 'while' structures. 
                    #itn (iteration-#) allows the iteration through itx and ity
                    itx = [1, 2, 3, 4, 5, 6, 7, -1, -2, -3, -4, -5, -6, -7,
                             1, 2, 3, 4, 5, 6, 7, -1, -2, -3, -4, -5, -6 -7]
                    ity = [1, 2, 3, 4, 5, 6, 7, -1, -2, -3, -4, -5, -6 -7,
                          -1, -2, -3, -4, -5, -6, -7, 1, 2, 3, 4, 5, 6, 7]
                    itn = 0
                    
                    #[1] If the location to be assessed is off the map, nix.
                    #[2] If square is occupied, continue
                    #[3] Piece on square is bishop/queen, raise KingCheck
                    #[4] If piece not bishop/queen, any bishop/queen farther
                    #    in that diagonal must be overlooked. Iteration is
                    #    advanced to next case.
                    
                    while itn < 24:
                        if 0 < (x + itx[itn]) < 8  and 0 < (y + ity[itn]) < 8: #[1]
                            
                            square = self.board[x + itx[itn]][y + ity[itn]]
                            if square.occ == True: #[2]
                 
                             
                                if square.piece.name == 'queen': #[3]
                                    if square.piece.black != teamColor:
                                        raise KingCheck
                                if square.piece.name == 'bishop': #[3]
                                    if square.piece.black != teamColor:
                                        raise KingCheck
                     
                                #[4]
                                if -1 < itn < 7: itn2 = itn; itn = 6
                                elif 7 <= itn < 13: itn2 = itn; itn = 12
                                elif 13 <= itn < 19: itn2 = itn; itn = 18
                                else: break


                        
                        
                        itn += 1
                        
                    #Now the same thing is done, only the
                    # ity and itx are modified for rooks
                    #and queens
                    itx = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             1, 2, 3, 4, 5, 6, 7, -1, -2, -3, -4, -5, -6, -7]
                    ity = [1, 2, 3, 4, 5, 6, 7, -1, -2, -3, -4, -5, -6, -7, 
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    itn = 0
                    
                    while itn < 24:
                        if 0 < (x + itx[itn]) < 8  and 0 < (y + ity[itn]) < 8: #[1]
                            #print(x + itx[itn], 'heuo', itn)
                            
                            square = self.board[x + itx[itn]][y + ity[itn]]
                            if square.occ == True: #[2]
                                
                                
                                if square.piece.name == 'queen': #[3]
                                    if square.piece.black != teamColor:
                                        raise KingCheck
                                
                                if square.piece.name == 'rook': #[3]
                                    
                                    if square.piece.black != teamColor:
                                        raise KingCheck
                              
                                #[4]
                                if -1 < itn < 7: itn2 = itn; itn = 6
                                elif 7 <= itn < 13: itn2 = itn; itn = 12
                                elif 13 <= itn < 19: itn2 = itn; itn = 18
                                else: break
                    
                        itn += 1
                    
                        
                    #Now, for the occasion that a pawn puts the king in check
                    
                    itx = [1, -1, 1, -1]
                    ity = [1, 1, -1, -1]
                    itn = 0
                    
                    if teamColor == True:
                        itn = 2
                  
                    while itn < 4:
                        if -1 < (x + itx[itn]) < 8  and -1 < (y + ity[itn]) < 8: #[1]
                        
                            square = self.board[x + itx[itn]][y + ity[itn]]
                            if square.occ == True: #[2]
                                if square.piece.name == 'pawn': #[3]
                                    if square.piece.black != teamColor:
                                        raise KingCheck

                        itn += 1
                        
                            
                    #finally, the knights. Surely, this must be a bit easier...   
                    itx = (1, 1, 2, 2, -1, -1, -2, -2)
                    ity = (2, -2, 1, -1, 2, -2, 1, -1)
                    itn = 0
                    
                    while itn < 8:
                        if -1 < (x + itx[itn]) < 8  and -1 < (y + ity[itn]) < 8: #[1]
                            
                            square = self.board[x + itx[itn]][y + ity[itn]]
                            if square.occ == True: #[2]
                                if square.piece.name == 'knight': #[3]
                                    if square.piece.black != teamColor:
                                        raise KingCheck

                        itn += 1
        
    def replacePiece(self, piece):
        '''In the event of the king being in check
        and a player moving a piece that doesn't 
        take the king out of check, the move must be
        un-done.'''
        x = piece.loc[0]
        y = piece.loc[1]
        oldx = piece.oldLoc[0]
        oldy = piece.oldLoc[1]
        
        self.board[x][y].occ = False
        piece.loc = piece.oldLoc
        self.board[oldx][oldy].piece = piece
        self.board[x][y].piece = self.board[x][y].oldPiece
        if self.board[x][y].piece != None:
            self.board[x][y].piece.captured = False
        
        
        
    
    def movepiece(self, piece, targetx, targety):
        '''Making sure that everything is cleaned up in *every* move.
          1- setting the piece's self.loc(x,y)
          2- setting the old square's self.occ
          3- setting the new square's self.occ
          4- setting the square's self.piece
          5- setting any captured piece's self.captured'''
        
        #Man, that would take a long time, to refer to the piece's 
        #x and y by that long phrase.
        x = piece.loc[0]
        y = piece.loc[1]
        
            
        
        try:
            piece.move(targetx,targety)
            
            
        except OccError:
            self._displayText('                     Through Occ Square             ')
            self.playerMove()
            self.moveFailed = True
            
        except DistError:
            self._displayText('                     Piece unable to move there     ')
            self.playerMove()
            self.moveFailed = True
#           displayGameText('Square out of range')
           #print('DistError!') #A call must be made back up to the GUI function that
                  # recieved user input for this move
                
        except TakePiece:
            #print('Piece Taken')
            self.board[x][y].piece = None
            self.board[targetx][targety].oldPiece = self.board[targetx][targety].piece
            piece.oldLoc = (x,y)
            self.board[x][y].occ = False
            self.board[targetx][targety].piece.captured = True
            piece.loc = (targetx,targety)
            self.board[targetx][targety].piece = piece
            
            
        else:
            self.board[targetx][targety].oldPiece = self.board[targetx][targety].piece
            self.board[x][y].piece = None
            piece.oldLoc = (x,y)
            self.board[targetx][targety].piece = piece
            self.board[piece.loc[0]][piece.loc[1]].occ = False
            self.board[targetx][targety].occ = True
            piece.loc = (targetx,targety)
            
    
    
    def createboard(self):
        '''Alright, bear with me on this one.
        The 'gameboard' is a list containing lists,
        the items of which are all instances of class
        'Gameboard'. It's made using a C++ style approach,
        I guess? But it's all I could do.'''
        
        #8 lists of 8 different GameSquare objects are created
        #Then the 8 lists are concatenated to form the 8X8 board
        y = 0
        x = 0
        squarelist = []
        gameboard = []
        while y < 8:
            while x < 8:
                t = GameSquare()
                squarelist.append(t)
                x += 1
            gameboard.append(squarelist)
            squarelist = []
            x = 0
            y += 1
        
       # print(gameboard)
    
  

        #Finally, it must be decided whether the squares are black or white.
        #Following the convention of 'white on the right', the first square
        #[0][0] must be black. 
        #The function works by taking a single x value, or column, and giving
        #its first square the attribute self.black = True. Then, the next square
        #in the column must be white. Then, the next must be black, 
        #and so on.     
        
        row = 0
        column = 0
        lastBlack = False
        
        while column < 8:
            if column == 1:
                lastBlack = True
            if column == 3:
                lastBlack = True
            if column == 5:
                lastBlack = True
            if column == 7:
                lastBlack = True
            if column == 2:
                lastBlack = False
            if column == 4:
                lastBlack = False
            if column == 6:
                lastBlack = False
            if column == 8:
                lastBlack = False
                
            
            
            while row < 8:
                if lastBlack == False:
                    gameboard[column][row].black = True
                    lastBlack = True
                elif lastBlack == True:
                    lastBlack = False
                row += 1
            column +=1
            row = 0
                
        
        #row = 0
        #column = 0
        #lastBlack = False
        #lastColumnStartBlack = True
        #while column < 8:
            
            ##At column 1 (the second), the first square is white, not black.
            ##the same thing goes for column 3, 5, 7. This allows for that.
            ##if column / 2 != 0:
                ##lastBlack = True
            ##elif column/2 != 1:
                ##lastBlack = True
            ##elif column/2 != 2:
                ##lastBlack = True
            ##elif column/2 != 3:
                ##lastBlack = True
            
            #if lastColumnStartBlack == True:
                #lastBlack = False
                
            #while row < 8:
                #if lastBlack == False:
                    #gameboard[column][row].black = True
                    #lastBlack = True
                    
                #elif lastBlack == True:
                    #lastBlack = False
                #row += 1
                
            #if lastColumnStartBlack == False:
                #lastColumnStartBlack = True
            #if lastColumnStartBlack == True:
                #lastColumnStartBlack = False
                
            #row = 0
            #column += 1
        #Finally, the completed gameboard is returned.
        self.board = gameboard
        return self.board
    
    
    def initboard(self):
        '''Creates instances of the piece classes, to fill the
        board. Assignes teams, either black or white, and places
        the pieces in their proper locations'''
        
        #The names of the instances are arbitrary, since they'll only
        #be referenced by their location on the gameboard from here on.
        # wPawn = white pawn. bPawn = black pawn. wBishopb = white bishop 
        # on black square. bBishopw = black bishop on white square
        
        #All of the white pieces!
        wPawnA = pawn(self.board, 0, 1)
        wPawnB = pawn(self.board, 1, 1)
        wPawnC = pawn(self.board, 2, 1)
        wPawnD = pawn(self.board, 3, 1)
        wPawnE = pawn(self.board, 4, 1)
        wPawnF = pawn(self.board, 5, 1)
        wPawnG = pawn(self.board, 6, 1)
        wPawnH = pawn(self.board, 7, 1)
        
        wRookA = rook(self.board, 0, 0)
        wKnightA = knight(self.board, 1, 0)
        wBishopb = bishop(self.board, 2, 0)
        wQueen = queen(self.board, 3, 0)
        wKing = king(self.board, 4, 0)
        wBishopw = bishop(self.board, 5, 0)
        wKnightB = knight(self.board, 6, 0)
        wRookB = rook(self.board, 7, 0)
        #-------------------------------------
        
        
        #All of the black pieces!
        bPawnA = pawn(self.board, 0, 6)
        bPawnB = pawn(self.board, 1, 6)
        bPawnC = pawn(self.board, 2, 6)
        bPawnD = pawn(self.board, 3, 6)
        bPawnE = pawn(self.board, 4, 6)
        bPawnF = pawn(self.board, 5, 6)
        bPawnG = pawn(self.board, 6, 6)
        bPawnH = pawn(self.board, 7, 6)
        
        bRookA = rook(self.board, 0, 7)
        bKnightA = knight(self.board, 1, 7)
        bBishopb = bishop(self.board, 5, 7)
        bQueen = queen(self.board, 3, 7)
        bKing = king(self.board, 4, 7)
        bBishopw = bishop(self.board, 2, 7)
        bKnightB = knight(self.board, 6, 7)
        bRookB = rook(self.board, 7, 7)
        #--------------------------------------
        
        #The teams are now set! 
        blackPieces = (bPawnA, bPawnB, bPawnC, bPawnD,
                       bPawnE, bPawnF, bPawnG, bPawnH, # 7
                       bRookA, bKnightA, bBishopb, bQueen, #11
                       bKing, bBishopw, bKnightB, bRookB)
        for x in blackPieces:
            x.black = True
            
        #Finally, in order to make these objects much easier to 
        #transport across the program, each will be an attribute
        # of the square they occupy. Isn't that a pain? But it's elegant
        # in a way, and frankly I can't think of anything else.
        allPieces =   (bPawnA, bPawnB, bPawnC, bPawnD,
                       bPawnE, bPawnF, bPawnG, bPawnH,
                       bRookA, bKnightA, bBishopb, bQueen, 
                       bKing, bBishopw, bKnightB, bRookB,
                       
                       wPawnA, wPawnB, wPawnC, wPawnD,
                       wPawnE, wPawnF, wPawnG, wPawnH,
                       wRookA, wKnightA, wBishopb, wQueen, 
                       wKing, wBishopw, wKnightB, wRookB)
        
  
        for x in allPieces:
            self.board[x.loc[0]][x.loc[1]].piece = x
            
        for y in allPieces:
            pass# print(y, y.loc, self.board[y.loc[0]][y.loc[1]].piece.loc)
        
        whitePieces = (wPawnA, wPawnB, wPawnC, wPawnD,
                       wPawnE, wPawnF, wPawnG, wPawnH,
                       wRookA, wKnightA, wBishopb, wQueen, 
                       wKing, wBishopw, wKnightB, wRookB)
            
        #Finally, those bishops need to know where they start
        bBishopb.startOnBlack = True
        wBishopb.startOnBlack = True
        return blackPieces, whitePieces
    
class GameSquare(object):
    '''This class includes all attributes that each
    square of the chessboard will need'''
    
    def __init__(self):
        '''Contains all arbitrary attributes of a single square'''
        self.occ = False
        self.black = False
        self.piece = None
        self.oldPiece = None
            

        
class GUI(object):
    def __init__(self):
        self.chess = None
        self.AI = None
        #So, I woke up one day to find this expression without a completion
        #the program still seems to run. I'm not sure what was supposed to be
        #assigned to self.stdscr. We can only hope.                             
   #    self.stdscr =
    
    def newGame(self):
        '''All initialization, registeration, et cetera is done. Then the 
        run loop of the logic is called, and the game is handed to the Logic.'''
        
        self.chess = Logic()
        self.chess.registerGuiMethods(self.userInput, self.displayText, self.updateDisplay)
        self.board = self.chess.createboard()
        self.blackPieces, self.whitePieces = self.chess.initboard()
        self.stdscr.addstr('Logic Running')
        
        if self.againstAI == True:
            self.chess.initAI( self.blackPieces, self.whitePieces, self.stdscr)
        
        self.stdscr.refresh()
        self.chess.run()
        
    def displayText(self, string, y=13, x=0):
        '''For all warnings to the user. Default location for start of text
        is 0,9.'''
        #if len(string) > 20:
            #stringOne = string[:10]
            #stringTwo = string[11:]
            #self.stdscr.addstr(y,x,stringOne)
            #self.stdscr.addstr(y + 1, x, stringTwo)
        #else:
            #self.stdscr.addstr(y,x, string)
        self.stdscr.addstr(y,x,string)
        self.stdscr.refresh()
    
    def updateDisplay(self):
        '''The (edited) gameboard is parsed by the rasterize function, and the strings
        returned are displayed on screen.'''
        strings = self.rasterize()
        self.stdscr.erase()
        itery = 0
        iterx = 0
        squareColor = 'Black'
        swap = 'Nope'
        while itery < 10:
            iterx = 0

            while iterx < 17:
                
                if itery > 7:
                    self.stdscr.addstr( (0 + itery), 0, self.strings[7-itery])
                    break
                
                needSecond = True
                



                    
                if squareColor == 'Black':
                    self.stdscr.addstr((0 + itery), (0 + iterx), self.strings[7-itery][iterx], curses.color_pair(1) )
                    if needSecond == True:
                        iterx += 1
                        self.stdscr.addstr((0 + itery), (0 + iterx), self.strings[7-itery][iterx], curses.color_pair(1) )
                        needSecond = False
                        
                    squareColor = 'White'
                elif squareColor == 'White':
                    self.stdscr.addstr((0 + itery), (0 + iterx), self.strings[7-itery][iterx], curses.color_pair(2) ) 
                    if needSecond == True:
                        iterx += 1
                        self.stdscr.addstr((0 + itery), (0 + iterx), self.strings[7-itery][iterx], curses.color_pair(2) ) 
                        needSecond = False
                    squareColor = 'Black'
                    
                #if iterx == 15:
                    #if squareColor == 'Black':
                        #squareColor = 'White'
                    #if squareColor == 'White':
                        #squareColor = 'Black'
                
                iterx += 1

            itery +=1
        itery = 0
        while itery < 10:
            iterx = 0
            while iterx < 17:
                if iterx < 3:
                    self.stdscr.addstr((0 + itery), (0 + iterx), self.strings[7-itery][iterx])
                    iterx += 1
                    self.stdscr.addstr((0 + itery), (0 + iterx), self.strings[7-itery][iterx])
                    iterx += 1
                iterx += 1
            itery += 1
                
            
        self.stdscr.refresh()
        
    
    def userInput(self):
        '''The user inputs a string looking like so:
        A1-B2, which is passed to Logic (decypherInput()), which
        interprets it and passes it to playerTurn()'''
        self.stdscr.nodelay(0)
        userInput = self.stdscr.getstr(10,0, 5)
        return userInput

        
    def userInputStartGame(self):
        '''Yeah, I know, I don't want to talk about it.'''
        self.stdscr.nodelay(0)
        keyNumber = self.stdscr.getch()
        return keyNumber
    
    def main(self):
        '''Entry point to the program.'''
        self.initScreen()
        try:
            self.welcomeMenu()
        except EndGame:
            self.endGame()
        finally:
            self.restoreScreen()
            
    def restoreScreen(self):
        '''Reset terminal window'''
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()

    def welcomeMenu(self):
        '''Offers the user multiple options when the game is started'''
        while True:
            #Erase the screen
            self.stdscr.erase()
            
            #First welcome menu
            self.stdscr.addstr(0,0, "----------------------------------------\nPython Chess Program\n----------------------------------------")
            self.stdscr.addstr(3,0, "Version 1.1.1")
            self.stdscr.addstr(5,0, "Options:")
            self.stdscr.addstr(6,0, "  [1] Play Game")
            self.stdscr.addstr(7,0, "  [2] Game Options (Coming Soon!)\n  [3] Tutorial \n  [4] Author/Copyright Info\n  [5] Quit\n\nEnter the Number that corresponds with your decision")
            decision = self.userInputStartGame()
            
            #Play Game Sreen
            if decision == ord('1'):
                self.stdscr.erase()
                self.stdscr.addstr(0,0,"What is the composition of your opponent characterized by?\n\n     [1] Carbon (Human Opponent)\n     [2] Silicon (Computer Opponent)")
                decision2 = self.userInputStartGame()
                if decision2 == ord('1'):
                    self.againstAI = False
                    self.newGame()
                    
                if decision2 == ord('2'):
                    self.againstAI = True
                    self.newGame()
               
            #Game Options Screen     
            elif decision == ord('2'):
                self.stdscr.erase()
                self.stdscr.addstr(0,0, "Want game options? Support the author!\n...or press any key to return, I guess...")
                self.stdscr.refresh()
                self.userInputStartGame()
                
            #Quit Game
            elif decision == ord('5'):
                break
            
            #Author/Copyright Info Screen
            elif decision == ord('4'):
                self.stdscr.addstr(0,0,"Author: John Hewitt\nContact: jhzakharov@gmail.com\n\nCopyright 2013 John Hewitt\n\nThis work is licensed under the Creative Commons\nAttribution NonCommercial-ShareAlike\nUnported License. To view a copy\nof this license, visit\nhttp://creativecommons.org/licenses/by-nc-sa/3.0/\nor send a letter to Creative Commons, 444 Castro\nStreet, Suite 900, Mountain View, California, 94041, USA\n\nA Word of Thanks to:\nCharles Adams\n")
                self.stdscr.refresh()
                decision = self.userInputStartGame()
                
            #Tutorial Screen
            elif decision == ord('3'):
                self.stdscr.erase()
                self.stdscr.addstr(0,0, '-----------How to Play----------\nMoves are mapped by the coordinates of the chessboard.\nEach move is entered as a 5-character string.\nString should be in the following format:\n\n     a2-a3  <--- Move piece at A2 to square at A3\n     A2_A3 <--- Also acceptable.\n\nCase of letters is arbitrary, as is the character between the two locations.\nProgram will recognize when a king is in check, and will\nstop any move that does not take king out of check.\nHowever, the program will not recognize\ncheckmate. So, when in check, the player must admit checkmate\nwith the following string:\n     ckmte \n\nPress any key to return')
                self.stdscr.refresh()
                deision = self.userInputStartGame()
                
                
        
    def initScreen(self):
        '''More of that curses initialization stuff'''
        self.stdscr = curses.initscr()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_CYAN)

    def endGame(self):
        '''What the players see once checkmate has been admitted'''
        self.stdscr.erase()
        str1,str2 = 'The team has won!', 'Press 2 to quit'
        while True:
            self.stdscr.addstr(0,0,str1)
            self.stdscr.addstr(1,0,str2)
            self.stdscr.refresh()
            decision = self.userInputStartGame()
            if decision == ord('2'):
                break
            

    def prepDisplay(self):
        '''Man, curses makes this whole thing a total pain. (y,x)
        I put the two boards here pretty much because it looks cool,
        and helps a bit in visualizing.
        
        curses                          Logic
        00 01 02 03 04 05 06 07         07 17 27 37 47 57 67 77
        10 11 12 13 14 15 16 17         06 16 26 36 46 56 66 76
        20 21 22 23 24 25 26 27         05 15 25 35 45 55 65 75
        30 31 32 33 34 35 36 37         04 14 24 34 44 54 64 74
        40 41 42 43 44 45 46 47         03 13 23 33 43 53 63 73
        50 51 52 53 54 55 56 57         02 12 22 32 42 52 62 72
        60 61 62 63 64 65 66 67         01 11 21 31 41 51 61 71
        70 71 72 73 74 75 76 77         00 10 20 30 40 50 60 70
        
        ^this is what the board's new coordinates have to be. The user
        must be able to read the board as they would with a conventional
        (x,y) 0,0 = bottom left style. This cannot affect any of the logic
        and must be used only to convert all locations before they are 
        rendered by curses'''
        
        
        column = []
        displayboard = []
        
        x = 0
        while x > 7:
            y = 8
            while y > 0:
                column.append(self.board[x][y])
                y -= 1
            displaybpard.append(column)
            column = []
            x += 1
            
    def rasterize(self):
        '''Turn the board into 8 strings that
        can be printed'''
        itn = 0
            
        str0,str1,str2,str3,str4 = '1 ', '2 ', '3 ', '4 ', '5 '
        str5,str6,str7,str8,str9 = '6 ', '7 ', '8 ', '   A B C D E F G H', ' -   -   -   -   -'
        strings = [str0,str1,str2,str3,str4,str5,str6,str7,str8,str9]
        platform = sys.platform
     
        for x in strings:
            x +=' '
        
        for x in self.board:
            itn = 0
            
            while itn < 8:
                
                if x[itn].piece == None:
                    char = '-'
                else:
                    name = x[itn].piece.name
                    color = x[itn].piece.black
                        
                    if name == 'pawn' and color:
                        if platform == 'win32':
                            char = 'P'
                        else:
                            char = 'Ã¢â„¢Å¸'
                    elif name == 'pawn' and not color:
                        if platform == 'win32':
                            char = 'p'
                        else:
                            char = 'Ã¢â„¢â„¢'
                    elif name == 'rook' and color:
                        if platform == 'win32':    
                            char = 'R'
                        else:
                            char = 'Ã¢â„¢Å“'
                    elif name == 'rook' and not color:
                        if platform == 'win32':
                            char = 'r'
                        else:
                            char = 'Ã¢â„¢â€“'
                    elif name == 'knight' and color:
                        if platform == 'win32':
                            char = 'E'
                        else:
                            char = 'Ã¢â„¢Å¾'
                    elif name == 'knight' and not color:
                        if platform == 'win32':
                            char = 'e'
                        else:
                            char = 'Ã¢â„¢Ëœ'
                    elif name == 'bishop' and color:
                        if platform == 'win32':
                            char = 'B'
                        else:
                            char = 'Ã¢â„¢ï¿½'
                    elif name == 'bishop' and not color:
                        if platform == 'win32':
                            char = 'b'
                        else:
                            char = 'Ã¢â„¢â€”'
                    elif name == 'king' and color:
                        if platform == 'win32':
                            char = 'K'
                        else:
                            char = 'Ã¢â„¢Å¡'
                    elif name == 'king' and not color:
                        if platform == 'win32':
                            char = 'k'
                        else:
                            char = 'Ã¢â„¢â€�'
                    elif name == 'queen' and color:
                        if platform == 'win32':
                            char = 'Q'
                        else:
                            char = 'Ã¢â„¢â€º'
                    elif name == 'queen' and not color:
                        if platform == 'win32':
                            char = 'q'
                        else:
                            char = 'Ã¢â„¢â€¢'
                strings[itn] += ' '
                strings[itn] += char
                ## TO TEST FOR CORRECT COLORING
                #if x[itn].black == False:
                    #strings[itn] += 'w'
                #elif x[itn].black == True:
                    #strings[itn] += 'b'
                itn += 1
        itn = 8    
        for x in strings:
            x = str(itn) + ' ' + x
        self.strings = strings
        return strings
                    
        
                
        
        #self.board[0][1].piece.move(0,2)
        #print('White has moved!')
        #self.board[1][6].piece.move(1,5)
        #print(self.board[0][2].piece.loc)u
    
        
        #self.board[1][1].move(1,2)
        #print('White moves!')
        #self.board[2][6].move(2,5)
        #print('Black moves!')
        #self.board[
        
 
        
        
#Here we have all of our friendly errors!
#Maybe they shouldn't be used quite like this,
#But they're so darn useful!
class MoveError(Exception):
    pass
class DistError(MoveError):
    pass
class OccError(MoveError):
    pass
class TakePiece(Exception):
    pass
class KingCheck(Exception):
    pass
class EndGame(Exception):
    pass
class TeamError(MoveError):
    pass



class movePossibility():
    
    def __init__(initialSquare, targerSquare, piece):
        self.stratVal = 0 #Strategic Value
        self.initalSquare = initialSquare
        self.targetSquare = targetSquare
        self.piece = piece
        

class AI():
    
    def __init__(self, chessboard, humanPieces, AIPieces, stdscr, difficulty = 1):
        
        #First, the AI must have direct access to the chessboard, and the logic itself.
        self.chessboard = chessboard
        self.difficulty = difficulty
        self.stdscr = stdscr
        self.counter = 0
        
        #Specific pieces on the AI's team must be referenced 
        self.AIKing = AIPieces[12]
        self.AIQueen = AIPieces[11]
        self.AIBishopRight = AIPieces[10]
        self.AIBishopLeft = AIPieces[13]
        self.AIKnightLeft = AIPieces[9]
        self.AIKnightRight = AIPieces[14]
        self.AIRookRight = AIPieces[15]
        self.AIRookLeft = AIPieces[8]
        
        #Specific pieces on the human team must be referenced
        self.humanKing = humanPieces[12]
        self.humanQueen = humanPieces[11]
        self.humanBishopRight = humanPieces[10]
        self.humanBishopLeft = humanPieces[13]
        self.humanKnightLeft = humanPieces[9]
        self.humanKnightRight = humanPieces[14]
        self.humanRookRight = humanPieces[15]
        self.humanRookLeft = humanPieces[8]
     
                    
        
        
        
    def calculateMove(self):
        self.counter2 = 0
        initialx = random.randint(1,8)
        initialy = random.randint(1,8)
        targetx =  random.randint(1,8)
        targety =  random.randint(1,8)
        move ="  " + str(initialx) + str(initialy) + '-' + str(targetx) + str(targety)
        if self.counter < 10:
            self.counter = 0
            self.counter2 += 1
        self.stdscr.addstr(15 + self.counter,0 + self.counter2, move)
        self.stdscr.refresh()
        self.stdscr.addstr(16 + self.counter, 0,  str(self.chessboard[initialx-1][initialy-1].occ))
        self.stdscr.refresh()
        self.counter += 2
        return move
        #The AI thinks defensively and then offensively. Moves are decided with a value system that puts slightly more value in defense than offense. 
        
        #First, a list is made of all possible locations to which the opposing team can move.
        humanMoveList = []

        xList = [0,1,2,3,4,5,6,7]
        yList = [0,1,2,3,4,5,6,7]
        
        for piece in humanPieces:
            for xLoc in xList:
                for yLoc in yList:
                    try:
                        piece.move(xLoc,yLoc)
                        humanMoveList.append(movePossibility(piece.loc, [xLoc,yLoc], piece))
                    except MoveError:
                        pass
        stringList = []
        counter = 0
        for x in humanMoveList:
            stringList.append(str(x.stratVal) + ' ' + str((15 + counter),x.initialSquare) + ' ' + str(x.targetSquare) + ' ' + x.piece)


#------------------------------------------------------------------------------
#After healthy amount of whitespace, we have the classes for each of the 
#pieces of chess!
#------------------------------------------------------------------------------
    
class pawn():
    '''Contains all attributes, most importantly the conditions
    on which the pawn can move into a target square.'''
    
    def __init__(self, gameboard, initx, inity):
        self.board = gameboard
        self.captured = False
        self.loc = (initx,inity)
        self.oldLoc = (None,None)
        self.name = 'pawn'
        self.board[initx][inity].occ = True
        self.black = False
        self.alreadyMoved = False
    
    def move(self, targetx, targety):
        '''First, makes the target square's location relative to the piece,
        then decides if the relative location is an acceptable target.'''
        x = targetx - self.loc[0]
        y = targety - self.loc[1]     
        
        
        if self.black == True and y > 0:
            raise DistError
        if self.black == False and y < 0:
            raise DistError
    
        if abs(x) == 1 and abs(y) == 1:
            if self.board[self.loc[0] + x][self.loc[1] + y].occ == True:
                raise TakePiece
 
        if y == 1 and x == 0 and self.board[self.loc[0]][self.loc[1] + 1 ].occ == True:
            raise OccError
        if y == 2 and x == 0 and self.board[self.loc[0]][self.loc[1] + 2].occ == True:
            raise OccError
        if y == 2 and x == 0 and self.board[self.loc[0]][self.loc[1] + 1].occ == True:
            raise OccError
        if y == -1 and x == 0 and self.board[self.loc[0]][self.loc[1] - 1 ].occ == True:
            raise OccError
        if y == -2 and x == 0 and self.board[self.loc[0]][self.loc[1] - 2 ].occ == True:
            raise OccError
        if y == -2 and x == 0 and self.board[self.loc[0]][self.loc[1] - 1 ].occ == True:
            raise OccError            
            
        if y == 2 or y == -2:
            if x == 0:
                
                if self.alreadyMoved == False:
                    self.alreadyMoved = True
                    return   
        if abs(x) > 0 or abs(y) >1:
            raise DistError
        
        #Alright, so it looks like a kludge here. It's not, I think.
        #These stop the pawn from moving straight forward into an occupied
        #square, or doing the same in its inital two-space move, or jumping
        #a piece during its initial two-space move.
        

        #Note to self: All cleaning up of moves will be done by the logic 
        #class functions 'movepiece'!

        
        
class rook():
    '''Contains all attributes, most importantly the conditions
    on which the pawn can move into a target square'''
    
    def __init__(self, gameboard, initx, inity):
        self.board = gameboard
        self.captured = False
        self.loc = (initx,inity)
        self.oldLoc = (None,None)
        self.name = 'rook'
        self.board[initx][inity].occ = True
        self.black = False
        
    def move(self,targetx,targety):
        '''Raises a MoveError if the move is illegal, raises a TakePiece
        if the move takes a piece.'''
        #Relativization!
        x = targetx - self.loc[0]
        y = targety - self.loc[1]
        
        # Rooks can't go diagonally
        if abs(x) > 0 and abs(y) > 0:
            raise DistError
        
        #Look, the next for conditions are really ugly. I understand. 
        #They'll be changed at some point, hopefully- but I'm not sure how.
        #if there's somthinging in the way and the rook is moving along x
        if x > 0 and y == 0:
            #print('alongx')
            itera = 1
            while itera < x:
                if self.board[self.loc[0] + itera][self.loc[1]].occ == True:
                    raise OccError
                itera += 1

        #if there's something in the way, rook is moving along y
        if y > 0:
          #  print('alongy')
            itera = 1
            while itera < y:
                if self.board[self.loc[0]][self.loc[1] + itera].occ ==True:
                    raise OccError
                itera += 1
                
        #if there's somthing in the way closer to 0, rook is moving along x
        if x < 0:
          #  print('alongx0')
            itera = 1
            while itera < abs(x):
                if self.board[self.loc[0] - itera][self.loc[1]].occ == True:
                    raise OccError
                itera += 1
                
                
        #if there's something in the way closer to 0, rook is moving along y
        if y < 0:
          #  print('alongy0')
            itera = 1
            while itera < abs(y):
                if self.board[self.loc[0]][self.loc[1] - itera].occ ==True:
                    raise OccError
                itera += 1         

        #Finally, if no errors are raised, and there is a piece on the target
        #square, the piece is taken. How does that happen? Dunno.
        if self.board[targetx][targety].occ == True:
            raise TakePiece
        
        #Note to self: All cleaning up done by Logic().movepiece()!
        
class knight():
    '''Contains all attributes, most importantly the conditions
    on which the knight can move into a target square'''
    
    def __init__(self, gameboard, initx, inity):
        self.board = gameboard
        self.captured = False
        self.loc = (initx,inity)
        self.oldLoc = (None,None)
        self.name = 'knight'
        self.black = False
        self.board[initx][inity].occ = True
        
    def move(self,targetx,targety):
        '''Raises a MoveError if the move is illegal, raises a TakePiece
        if the move takes a piece.'''
        x = targetx - self.loc[0]
        y = targety - self.loc[1]
        
        #If the knight is on black it must move to a white square
        #If the knight is on white, it must move to black
        if self.board[self.loc[0]][self.loc[1]].black == True:
            if self.board[targetx][targety].black == True:
                raise DistError
            
        if self.board[self.loc[0]][self.loc[1]].black == False:
            if self.board[targetx][targety].black == False:
                raise DistError   
        
        #No straight lines in any direction, knight ye!
        #And, no going any further than 3 total squares!
        if x == 0 or y == 0:
            raise DistError
        if abs(x) + abs(y) > 3:
          #  print(x + y)
            raise DistError
        
        #Yarr, capture the piece!
        if self.board[targetx][targety].occ == True:
            raise TakePiece
        
        #All cleaning up done by Logic().movepiece()!
        
#Comment for commit        
        
class bishop():
    '''Contains all attributes, most importantly the conditions
    on which the bishop can move into a target square'''
    
    def __init__(self, gameboard, initx, inity):
        self.board = gameboard
        self.captured = False
        self.loc = (initx,inity)
        self.oldLoc = (None,None)
        self.name = 'bishop'
        self.black = False
        self.startOnBlack = False
        self.board[initx][inity].occ = True
        
    def move(self, targetx, targety):
        '''Raises a MoveError if the move is illegal, raises a TakePiece
        if the move takes a piece.'''
        x = targetx - self.loc[0]
        y = targety - self.loc[1]
        
        #So! The first two nested if-statements stop a bishop that started on
        #a black square from going to a white, and visa-versa. Number three
        #makes sure that the bishop is going in a diagonal.
        if self.startOnBlack == True:
            if self.board[targetx][targety].black == False:
                raise DistError
        if self.startOnBlack == False:
            if self.board[targetx][targety].black == True:
                raise DistError
        
        if abs(x) != abs(y):
            raise DistError
    
        
        #All of those nasty makings sures, making sure that the bishop isn't
        #mowing over any pieces on its way to the target square.
        #what a pain they are.
        if x > 0 and y > 0:
            itera = 1
            while itera < x:
                if self.board[self.loc[0] + itera][self.loc[1] + itera].occ == True:
                    raise OccError
                itera += 1

        #if there's something in the way, rook is moving along y
        if x > 0 and y < 0:
            itera = 1
            while itera < abs(y):
                if self.board[self.loc[0] + itera][self.loc[1] - itera].occ == True:
                    raise OccError
                itera += 1
                
        #if there's somthing in the way closer to 0, rook is moving along x
        if x < 0 and y > 0:
            itera = 1
            while itera < abs(x):
                if self.board[self.loc[0] - itera][self.loc[1] + itera].occ == True:
                    raise OccError
                itera += 1
                
        #if there's something in the way closer to 0, rook is moving along y
        if x < 0 and y < 0:
            itera = 1
            while itera < abs(y):
                if self.board[self.loc[0] - itera][self.loc[1] - itera].occ ==True:
                    raise OccError
                itera += 1         

        #Finally, if no errors are raised, and there is a piece on the target
        #square, the piece is taken. How does that happen? Dunno.
        if self.board[targetx][targety].occ == True:
            raise TakePiece

 
class king():
    
    def __init__(self, gameboard, initx, inity):
        self.board = gameboard
        self.captured = False
        self.loc = (initx,inity)
        self.name = 'king'
        self.black = False
        self.oldLoc = (None,None)
        self.board[initx][inity].occ = True
        self.check = False
        
    def move(self, targetx, targety):
        
        x = (targetx - self.loc[0])
        y = (targety - self.loc[1])
        
        if abs(x) > 1 or abs(y) > 1:
            raise DistError
        
        if self.board[targetx][targety].occ == True:
            raise TakePiece
        
        #All cleaning done by Logic().movepiece()

        

        
class queen():
    
    def __init__(self, gameboard, initx, inity):
        self.board = gameboard
        self.captured = False
        self.loc = (initx,inity)
        self.oldLoc = (None,None)
        self.name = 'queen'
        self.black = False
        self.board[initx][inity].occ = True
        self.queen = True
        
    def move(self, targetx, targety):
        
        x = (targetx - self.loc[0])
        y = (targety - self.loc[1])
       
       # print(targetx,targety)
       # print(self.loc[0],self.loc[1])
        #print(x,y)
        if abs(x) != abs(y):
            if not x == 0:
                if not y == 0:
                    raise DistError
        
        #Sigh, now to check if there are any pieces in the way
        #I hate this part. And it was so easy to define how the
        #queen should move!
        
        #queen is moving up 
        if x == 0 and y > 0:
            itera = 1
            while itera < abs(y):
                if self.board[self.loc[0]][self.loc[1] + itera].occ == True:
                    raise OccError
                itera += 1
         
        #queen is moving down
        if x == 0 and y < 0:
            itera = 1
            while itera < abs(y):
                if self.board[self.loc[0]][self.loc[1] - itera].occ == True:
                    raise OccError
                itera += 1
                
        #queen is moving right
        if y == 0 and x > 0:
            itera = 1
            while itera < x:
                if self.board[self.loc[0] + itera][self.loc[1]].occ == True:
                    raise OccError
                itera += 1
        
        #queen is moving left
        if y == 0 and x < 0:
            itera = 1
            while itera < abs(x):
                if self.board[self.loc[0] - itera][self.loc[1]].occ == True:
                    raise OccError
                itera += 1

        #queen is moving along postive-positive diagonal -- GOOD
        if x == y and x > 0:
            itera = 1
            while itera < x:
                if self.board[self.loc[0] + itera][self.loc[1] + itera].occ == True:
                    raise OccError
                itera += 1

        #queen is moving along positive-negative diagonal
        if abs(x) == abs(y) and y < 0 and x > 0:
            itera = 1
            while itera < abs(y):
                if self.board[self.loc[0] + itera][self.loc[1] - itera].occ == True:
                    raise OccError
                itera += 1
                
        #queen is moving along the negative-positive diagonal
        if abs(x) == abs(y) and y > 0 and x < 0:
            itera = 1
            while itera < abs(x):
                if self.board[self.loc[0] - itera][self.loc[1] + itera].occ == True:
                    raise OccError
                itera += 1
                
        #queen is moving along the negative-negative diagonal
        if x == y and x < 0:
            itera = 1
            while itera < abs(y):
                if self.board[self.loc[0] - itera][self.loc[1] - itera].occ ==True:
                    raise OccError
                itera += 1         
        
        #These are important! Make sure they are correct!
        # ---- In the Event of Valid Move ---- 
        if self.board[targetx][targety].occ == True:
            raise TakePiece
        
        #All cleaning up done by Logic().movepiece()!
                

        
        
   
              
if __name__ == '__main__':
    GUI().main()

