import sqlite3
from tkcalendar import DateEntry
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from time import mktime
from io import BytesIO
import re
from json import loads as JSONLoads, dumps as JSONDumps
from hashlib import sha256
import random
from random import randint, shuffle
from base64 import b64encode, b64decode
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from PIL import Image as PILImage
from os import path as OSPath
import numpy
import pandas as pd
from math import isnan as MathIsnan
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

fill = '#FFF'
AppName = 'Quiz System'

class NewConnection:
    def __init__(self):
        self.conn = sqlite3.connect('data.db')
        self.cursor = self.conn.cursor()
        
    def Close(self):
        self.cursor.close()
        self.conn.close()


def InsertData(table, keys, values):
    # Prevents database errors
    if not len(keys) == len(values):
        return False
    
    # Generate the SQL query
    string = ''
    for i in range(len(keys)):
        string += '?'
        if i < len(keys) - 1:
            string += ','
    query = 'INSERT INTO ' + table + ' (' + ','.join(keys) + ') VALUES (' + string + ')'
    
    
    database = NewConnection() # Create a new database connection
    # Create the new record
    database.cursor.execute(query, tuple(values))
    database.conn.commit()
    database.Close() # Close the database connection

database = NewConnection() # Create a new database connection

# Delete Tables

'''
database.cursor.execute('DROP TABLE IF EXISTS RecordsLinkQuestionVersions')
database.cursor.execute('DROP TABLE IF EXISTS Records')
database.cursor.execute('DROP TABLE IF EXISTS Quizzes')
database.cursor.execute('DROP TABLE IF EXISTS QuizVersionsLinkQuestions')
database.cursor.execute('DROP TABLE IF EXISTS QuizVersions')
database.cursor.execute('DROP TABLE IF EXISTS Questions')
database.cursor.execute('DROP TABLE IF EXISTS QuestionVersions')
database.cursor.execute('DROP TABLE IF EXISTS Enrolments')
database.cursor.execute('DROP TABLE IF EXISTS Classes')
database.cursor.execute('DROP TABLE IF EXISTS Users')
'''

# Create Tables
database.cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
    USERNAME VARCHAR(20) PRIMARY KEY,
    FNAME VARCHAR(30) NOT NULL,
    LNAME VARCHAR(30) NOT NULL,  
    HASH CHAR(64) NOT NULL,
    SALT CHAR(32) NOT NULL,
    TYPE TINYINT NOT NULL
)''')
database.cursor.execute('''CREATE TABLE IF NOT EXISTS Classes (
    ID CHAR(8) PRIMARY KEY,
    TEACHERID VARCHAR(20) NOT NULL,
    NAME VARCHAR(40) NOT NULL,
    FOREIGN KEY (TEACHERID) REFERENCES Users(USERNAME) ON DELETE CASCADE ON UPDATE CASCADE
)''')
database.cursor.execute('''CREATE TABLE IF NOT EXISTS Enrolments (
    CLASSID CHAR(8) NOT NULL,
    STUDENTID VARCHAR(20) NOT NULL,
    FOREIGN KEY (CLASSID) REFERENCES Classes(ID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (STUDENTID) REFERENCES Users(USERNAME) ON DELETE CASCADE ON UPDATE CASCADE
)''')
database.cursor.execute('''CREATE TABLE IF NOT EXISTS QuestionVersions (
    ID CHAR(32) PRIMARY KEY,
    QUESTION VARCHAR(150) NOT NULL,
    OPTIONSJSON TEXT NOT NULL,
    CORRECTOPTIONINDEX INT NOT NULL,
    IMAGEBASE64 LONGTEXT,
    DATE INT NOT NULL
)''')
database.cursor.execute('''CREATE TABLE IF NOT EXISTS Questions (
    ID CHAR(32) PRIMARY KEY,
    TEACHERID VARCHAR(20) NOT NULL,
    CURRENTVERSIONID CHAR(32) NOT NULL,
    DELETED INT DEFAULT 0,
    FOREIGN KEY (TEACHERID) REFERENCES Users(USERNAME) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (CURRENTVERSIONID) REFERENCES QuestionVersions(ID) ON DELETE CASCADE ON UPDATE CASCADE
)''')
database.cursor.execute('''CREATE TABLE IF NOT EXISTS QuizVersions (
    ID CHAR(32) PRIMARY KEY,
    NAME VARCHAR(25) NOT NULL,
    DATE INT NOT NULL,
    DUEDATE INT NOT NULL
)''')
database.cursor.execute('''CREATE TABLE IF NOT EXISTS Quizzes (
    ID CHAR(32) PRIMARY KEY,
    CLASSID CHAR(8) NOT NULL,
    CURRENTVERSIONID CHAR(32) NOT NULL,
    DELETED INT DEFAULT 0,
    FOREIGN KEY (CLASSID) REFERENCES Classes(ID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (CURRENTVERSIONID) REFERENCES QuizVersions(ID) ON DELETE CASCADE ON UPDATE CASCADE
)''')
database.cursor.execute('''CREATE TABLE IF NOT EXISTS QuizVersionsLinkQuestions (
    QUIZVERSIONID CHAR(32) NOT NULL,
    QUESTIONID CHAR(32) NOT NULL,
    FOREIGN KEY (QUIZVERSIONID) REFERENCES QuizVersions(ID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (QUESTIONID) REFERENCES Questions(ID) ON DELETE CASCADE ON UPDATE CASCADE
)''')
database.cursor.execute('''CREATE TABLE IF NOT EXISTS Records (
    ID CHAR(32) PRIMARY KEY,
    QUIZID CHAR(32) NOT NULL,
    QUIZVERSIONID CHAR(32) NOT NULL,
    STUDENTID VARCHAR(20) NOT NULL,
    PERCENTAGE INT NOT NULL,
    DATE INT NOT NULL,
    FOREIGN KEY (QUIZID) REFERENCES Quizzes(ID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (QUIZVERSIONID) REFERENCES QuizVersions(ID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (STUDENTID) REFERENCES Users(USERNAME) ON DELETE CASCADE ON UPDATE CASCADE
)''')
database.cursor.execute('''CREATE TABLE IF NOT EXISTS RecordsLinkQuestionVersions (
    RECORDID CHAR(32) NOT NULL,
    QUESTIONVERSIONID CHAR(32) NOT NULL,
    CHOSENOPTIONINDEX INT NOT NULL,
    FOREIGN KEY (RECORDID) REFERENCES Records(ID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (QUESTIONVERSIONID) REFERENCES QuestionVersions(ID) ON DELETE CASCADE ON UPDATE CASCADE
)''')

''' **** DELETE THIS ****

username = 'student2'
database.cursor.execute('SELECT ID, CURRENTVERSIONID FROM Quizzes WHERE CURRENTVERSIONID IN (SELECT ID FROM QuizVersions WHERE NAME = "dd")')
result = database.cursor.fetchone()
quizId = result[0]
quizVersionId = result[1]

date = datetime.combine(datetime.today(), datetime.min.time()) + relativedelta(days = 1) - relativedelta(microseconds = 1)
timestamp = int(time.mktime(date.timetuple()))

interval = 86400 * 7

count = 10

for i in range(0, count):
    currentDate = str(timestamp - (i * interval))
    score = round(random.uniform(0, 1) * 3)
    
    percentage = round((score / 3) * 100)
    
    InsertData('Records', ['ID', 'QUIZID', 'QUIZVERSIONID', 'STUDENTID', 'PERCENTAGE', 'DATE'], [GenerateCode('Records', 'ID', 32), quizId, quizVersionId, username, percentage, currentDate])

'''

# Set default password for admin account: "adminPass"

database.cursor.execute('SELECT * FROM Users WHERE TYPE = 2')
result = database.cursor.fetchone()
if result is None:
   database.cursor.execute('INSERT INTO Users (USERNAME, FNAME, LNAME, HASH, SALT, TYPE) VALUES ("Admin", "Admin", "Account", "8a5c1f0c5652f6c8db4fc3b6e94984edebbec5a66998dea8b775605fd066c11e", "9161518d1b3341d3850867f658d3bfd0", 2)') 
   database.conn.commit()

database.Close() # Close the database connection

# Functions

def GenerateCode(tableName, fieldName, codeLength):
    string = ''
    characters = 'abcdefghijklmnopqrstuvwxyz0123456789'
    
    for i in range(codeLength):
        # Appends a random character to the string
        randomIndex = random.randint(0, len(characters) - 1)
        string += characters[randomIndex]
    
    # Search the database table for the generated code
    database = NewConnection()
    database.cursor.execute('SELECT COUNT(*) FROM ' + tableName + ' WHERE ' + fieldName + ' = ?', [string])
    result = database.cursor.fetchone()[0]
    database.Close()
    
    # If the generated code already exists in the database table, call the function again
    if result > 0:
        return GenerateCode(tableName, fieldName, codeLength)
    
    # Returns the code string
    return string

def Dialog(title, geometry):
    dialog = Toplevel()
    dialog.title(title) # Sets the title for the window
    dialog.resizable(0, 0) # Ensures that user cannot resize screen
    dialog.configure(bg = fill) # Sets the background colour to white
    dialog.geometry(geometry) # Sets the size of the window
    
    dialog.grid_rowconfigure(0, weight = 1)
    dialog.grid_columnconfigure(0, weight = 1)
    
    return dialog

def MenuFrame(main, text, callback):
    for widget in main.winfo_children():
        widget.destroy()

    returnBtn = Label(main, bg = fill, text = text, font = 'Arial 10 bold underline', cursor = 'hand2')
    returnBtn.grid(row = 0, sticky = 'w')
    returnBtn.bind('<Enter>', lambda value: returnBtn.config(fg = '#888'))
    returnBtn.bind('<Leave>', lambda value: returnBtn.config(fg = '#000'))
    returnBtn.bind('<Button-1>', lambda value: callback())

    frame = Frame(main, bg = fill)
    frame.grid(sticky = 'nesw')

    return frame

# Classes

class ValidationFormInput:
    def __init__(self, element, elementType):
        self.element = element
        self.type = elementType
        self.value = ""
        self.rules = []
        self.valid = False
    
    def UpdateValue(self):
        if self.type == 'Entry':
            self.value = self.element.get().strip()
        elif self.type == 'Text':
            self.value = self.element.get('1.0', END).strip()
    
    def AddRule(self, regexRule, errorMsg):
        self.rules.append([regexRule, errorMsg])
    
    def IsValid(self):
        # Get updated value for element
        self.UpdateValue()
        
        # Loop through all validation rules to check if the field is completely valid
        for i in self.rules:
            regexRule = i[0]
            errorMsg = i[1]
            
            if re.match(regexRule, self.value) == None:
                # If field is invalid return error message to be displayed to the user
                return errorMsg
        
        return True

class ValidationForm:
    def __init__(self):
        self.inputs = []
    
    def NewInput(self, element, elementType):
        newInput = ValidationFormInput(element, elementType)
        self.inputs.append(newInput)
        
        return newInput
    
    def Validate(self, callback):
        # Loop through all inputs to check if they are valid
        
        for i in self.inputs:
            inputValid = i.IsValid()
            if inputValid != True:
                return callback(inputValid)
                
        return callback(True)

class SideOption:
    def __init__(self, frame, text, callback):
        self.callback = callback
        self.btn = Button(frame, bg = fill, text = text, font = 'Arial 10 bold underline', cursor = 'hand2', borderwidth = 0, command = self.callback)
        self.btn.grid(sticky = 'w', pady = (0, 20))
        
        self.Update(False)
    def Update(self, selected):
        if selected == True:
            self.btn.config(fg = '#000', font = 'Arial 10', cursor = '', command = False)
            self.btn.unbind('<Enter>')
            self.btn.unbind('<Leave>')
        else:
            self.btn.config(fg = '#000', font = 'Arial 10 bold underline', cursor = 'hand2', command = self.callback)
            self.btn.bind('<Enter>', lambda value: self.btn.config(fg = '#888'))
            self.btn.bind('<Leave>', lambda value: self.btn.config(fg = '#000'))

class Table:
    def __init__(self, frame, height, *width):
        self.header = Frame(frame, bg = '#DDD')
        self.header.grid(sticky = 'w', ipadx = 11)
        self.headerWidths = []

        self.row = 0
        
        self.noStyle = False
        
        mainframe = Frame(frame)
        mainframe.grid(sticky = 'nesw')
        
        self.canvas = Canvas(mainframe, bg = fill, height = height)
        self.canvas.pack(side = 'left', fill = 'both', expand = True)
        
        scrollbar = Scrollbar(mainframe, orient = 'vertical', command = self.canvas.yview)
        scrollbar.pack(side = 'right', fill = 'both', expand = True)
        
        self.canvas.configure(yscrollcommand = scrollbar.set)
        
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion = self.canvas.bbox('all')))
        
        self.main = Frame(self.canvas, bg = fill)
        
        if width:
            self.canvas.create_window((0, 0), window = self.main, anchor = 'n', width = width)
        else:
            self.canvas.create_window((0, 0), window = self.main, anchor = 'n')
            
    def NewHeaderValue(self, text, width):
        labelFrame = Frame(self.header, bg = '#DDD', width = width, height = 22)
        labelFrame.pack_propagate(0)

        label = Label(labelFrame, bg = '#DDD', text = text, font = 'Arial 11 bold', anchor = 'w')
        label.pack()
        
        labelFrame.pack(side = 'left', fill = 'both', expand = True, padx = (5, 0))

        self.headerWidths.append(width)

        width = 5 * len(self.headerWidths)
        for n in self.headerWidths:
            width += n
        self.canvas.config(width = width)
        
class NewRow:
    def __init__(self, main, *altFill):
        self.column = 0
        self.fill = fill
        self.main = main

        if not main.noStyle:
            if main.row % 2 == 0:
                self.fill = '#EEE'
                
        if altFill:
            self.fill = altFill
                
        self.row = Frame(main.main, bg = self.fill)
        self.row.grid(row = main.row, sticky = 'ew')
        self.row.grid_columnconfigure(0, weight = 1)
            
        main.row += 1
        
    def NewLabel(self, text):
        width = 100
        if self.column < len(self.main.headerWidths):
            width = self.main.headerWidths[self.column]
        
        labelFrame = Frame(self.row, bg = self.fill, width = width, height = 22)
        labelFrame.pack_propagate(0)

        label = Label(labelFrame, bg = self.fill, text = text, font = 'Arial 11', anchor = 'w')
        label.pack()
        
        labelFrame.pack(side = 'left', fill = 'both', expand = True, padx = (5, 0))
            
        self.column += 1
        
        return label
    
    def NewEntry(self):
        width = 100
        if self.column < len(self.main.headerWidths):
            width = self.main.headerWidths[self.column]
        
        entryFrame = Frame(self.row, bg = self.fill, width = width, height = 22)
        entryFrame.pack_propagate(0)

        entry = Entry(entryFrame, bg = self.fill, font = 'Arial 11')
        entry.pack(fill = 'x', expand = True)
        
        entryFrame.pack(side = 'left', fill = 'both', expand = True, padx = (5, 0))
            
        self.column += 1
        
        return entry
    
    def NewBtn(self, text, callback):
        width = 100
        if self.column < len(self.main.headerWidths):
            width = self.main.headerWidths[self.column]
        
        btnFrame = Frame(self.row, bg = self.fill, width = width, height = 22)
        btnFrame.pack_propagate(0)

        btn = Button(btnFrame, bg = '#CCC', text = text, command = lambda: callback(), font='Arial 11 bold')
        btn.pack()
        
        btnFrame.pack(side = 'left', fill = 'both', expand = True, padx = (5, 0))

        self.column += 1
        
        return btn


def ReviewQuiz(pageDetails, quizVersionId, studentId, callbackName, callback):
        titleContentFrame = pageDetails[0]
        mainContentFrame = pageDetails[1]
    
        for widget in titleContentFrame.winfo_children():
            widget.destroy()
            
        for widget in mainContentFrame.winfo_children():
            widget.destroy()
    
        quizFrame = MenuFrame(titleContentFrame, 'Return to "' + callbackName + '"', callback)
                
        database = NewConnection()
        database.cursor.execute('SELECT NAME, DUEDATE FROM QuizVersions WHERE ID = ? ORDER BY DATE DESC', [quizVersionId])
        version = database.cursor.fetchone()
    
        quizName = version[0]
        quizDueDate = datetime.fromtimestamp(version[1]).strftime('Due: %a %d %b')
    
        quizNameLabel = Label(titleContentFrame, bg = fill, text = quizName, font = 'Arial 14 bold')
        quizNameLabel.grid(row = 1, sticky = 'w', pady = (10, 0))
    
        quizDueDateLabel = Label(titleContentFrame, bg = fill, text = quizDueDate, font = 'Arial 12')
        quizDueDateLabel.grid(row = 2, sticky = 'w')
    
        database.cursor.execute('SELECT ID, PERCENTAGE FROM Records WHERE QUIZVERSIONID = ? AND STUDENTID = ? ORDER BY PERCENTAGE DESC', [quizVersionId, studentId])
        record = database.cursor.fetchone()
        
        recordID = record[0]
        percentage = record[1]
        
        database.cursor.execute('SELECT COUNT(*) FROM RecordsLinkQuestionVersions WHERE EXISTS (SELECT 1 FROM QuestionVersions WHERE RecordsLinkQuestionVersions.CHOSENOPTIONINDEX = QuestionVersions.CORRECTOPTIONINDEX AND RecordsLinkQuestionVersions.QUESTIONVERSIONID = QuestionVersions.ID) AND RECORDID = ?', [recordID])
        score = database.cursor.fetchone()[0]
        
        database.cursor.execute('SELECT COUNT(*) FROM RecordsLinkQuestionVersions WHERE RECORDID = ?', [recordID])
        total = database.cursor.fetchone()[0]
    
        quizScoreLabel = Label(titleContentFrame, bg = fill, text = 'Score: ' + str(score) + ' / ' + str(total), font = 'Arial 13')
        quizScoreLabel.grid(row = 1, sticky = 'e')
    
        quizPercentageLabel = Label(titleContentFrame, bg = fill, text = 'Percentage: ' + str(percentage) + '%', font = 'Arial 13')
        quizPercentageLabel.grid(row = 2, sticky = 'e')
        
        database.cursor.execute('SELECT FNAME, LNAME FROM Users WHERE USERNAME = ?', [studentId])
        name = ' '.join(database.cursor.fetchone())
        
        quizDescription = Label(titleContentFrame, bg = fill, text = 'Review for ' + name, font = 'Arial 12 bold')
        quizDescription.grid(pady = (15, 0))
    
        questions = Table(mainContentFrame, 229, 569)
        questions.NewHeaderValue('', 569)
    
        database.cursor.execute('SELECT ID, QUESTION, OPTIONSJSON, CORRECTOPTIONINDEX FROM QuestionVersions WHERE ID IN (SELECT QUESTIONVERSIONID FROM RecordsLinkQuestionVersions WHERE RECORDID = ?)', [record[0]])
        result = database.cursor.fetchall()
    
        for n in range(len(result)):
            options = JSONLoads(result[n][2])
            
            correctIndex = result[n][3]
            
            database.cursor.execute('SELECT CHOSENOPTIONINDEX FROM RecordsLinkQuestionVersions WHERE RECORDID = ? AND QUESTIONVERSIONID = ?', [record[0], result[n][0]])
            chosenIndex = database.cursor.fetchone()[0]
            
            questionFrame = Frame(questions.main, bg = fill, bd = 2, relief = 'solid')
            questionFrame.pack(side = 'top', fill = 'x')
    
            questionTitleFrame = Frame(questionFrame, bg = fill)
            questionTitleFrame.pack(pady = (10, 0))
    
            questionIndexLabel = Label(questionTitleFrame, bg = fill, text = ('Q' + str(n + 1) + ':'), font = 'Arial 11 bold')
            questionIndexLabel.grid(row = 0, column = 0)
            
            questionLabel = Message(questionTitleFrame, bg = fill, text = result[n][1], font = 'Arial 11 bold', justify = 'center', width = 400)
            questionLabel.grid(row = 0, column = 1)
                
            questionAnswerFrame = Frame(questionFrame, bg = fill)
            questionAnswerFrame.pack(pady = (10, 20))
            
            if correctIndex == chosenIndex:
                chosenAnswerLabel = Label(questionAnswerFrame, bg = fill, text = 'Chosen Answer', font = 'Arial 11 bold')
                chosenAnswerLabel.grid(row = 0)
    
                chosenAnswerLabel = Message(questionAnswerFrame, bg = '#0F0', text = options[chosenIndex], font = 'Arial 11', justify = 'center', width = 200)
                chosenAnswerLabel.grid(row = 1, pady = (5, 15), ipadx = 10)
    
                noticeLabel = Label(questionAnswerFrame, bg = fill, fg = '#12A012', text = '✔ Correct', font = 'Arial 11')
                noticeLabel.grid(row = 1, column = 1)
            else:
                chosenAnswerLabel = Label(questionAnswerFrame, bg = fill, text = 'Chosen Answer', font = 'Arial 11 bold')
                chosenAnswerLabel.grid(row = 0)
                
                chosenAnswerLabel = Message(questionAnswerFrame, bg = '#F00', text = options[chosenIndex], font = 'Arial 11', justify = 'center', width = 200)
                chosenAnswerLabel.grid(row = 1, pady = (5, 15), ipadx = 10)
    
                noticeLabel = Label(questionAnswerFrame, bg = fill, fg = '#F00', text = '❌ Incorrect', font = 'Arial 11')
                noticeLabel.grid(row = 1, column = 1, padx = 15)
                
                correctAnswerLabel = Label(questionAnswerFrame, bg = fill, text = 'Correct Answer', font = 'Arial 11 bold')
                correctAnswerLabel.grid(row = 0, column = 2)
                
                correctAnswerLabel = Message(questionAnswerFrame, bg = '#0F0', text = options[correctIndex], font = 'Arial 11', justify = 'center', width = 400)
                correctAnswerLabel.grid(row = 1, column = 2, pady = (5, 15), ipadx = 10)
