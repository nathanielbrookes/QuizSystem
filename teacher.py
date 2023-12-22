from Global import *

def Teacher_DeleteQuestion(pageDetails, versionID):
    titleContentFrame = pageDetails[0]
    mainContentFrame = pageDetails[1]
    username = pageDetails[2]
    accountType = pageDetails[3]
    
    # Finds the question name
    database = NewConnection()
    database.cursor.execute('SELECT QUESTION FROM QuestionVersions WHERE ID = ?', [versionID])
    questionName = database.cursor.fetchone()[0]
    database.Close()
		
    # Displays warning message
    confirm = messagebox.askquestion(title = 'Delete "' + questionName + '"', message = 'This action cannot be undone. Are you sure you want to delete this question?')
    if confirm == 'yes':
        # Updates the deleted state of the record in the Questions table
        database = NewConnection()
        database.cursor.execute('UPDATE Questions SET DELETED = 1 WHERE CURRENTVERSIONID = ?', [versionID])
        database.conn.commit()
        database.Close()
        
        Teacher_DisplayQuestionBank(pageDetails) # Refreshes screen

def Teacher_DisplayQuestionBank(pageDetails):
    titleContentFrame = pageDetails[0]
    mainContentFrame = pageDetails[1]
    username = pageDetails[2]
    accountType = pageDetails[3]
    
    # Delete widgets from the main screen
    for widget in titleContentFrame.winfo_children():
        widget.destroy()
    for widget in mainContentFrame.winfo_children():
        widget.destroy()
      
    # Creates the selected title text
    selectedTitle = Label(titleContentFrame, bg = fill, text = 'Question Bank', font = 'Arial 13 bold', anchor = 'w')
    selectedTitle.grid(sticky = 'nw')
    
    # Creates the create question button
    createQuestionBtn = Button(titleContentFrame, bg = '#DDD', text = 'Create a new question', font = 'Arial 10', command = lambda: Teacher_InitQuestionForm('create', username, lambda: Teacher_DisplayQuestionBank(pageDetails)))
    createQuestionBtn.grid(row = 0, sticky = 'e', pady = (0, 10))
    
    # Creates a new scrollable table for the classes
    questions = Table(mainContentFrame, 305)
    questions.NewHeaderValue('Question', 454) # Column 1 - Question name
    questions.NewHeaderValue('', 40) # Column 2 - Edit button
    questions.NewHeaderValue('', 65) # Column 3 - Delete button
    
    # Searches for all of the questions the user has created
    database = NewConnection()
    database.cursor.execute('SELECT ID, QUESTION, OPTIONSJSON, CORRECTOPTIONINDEX, IMAGEBASE64 FROM QuestionVersions WHERE ID IN (SELECT CURRENTVERSIONID FROM Questions WHERE TEACHERID = ? AND DELETED = 0) ORDER BY DATE DESC', [username])
    result = database.cursor.fetchall()
    
    # Loops through all of the questions
    for question in result:
        row = NewRow(questions)
        
        row.NewLabel(question[1]) # Creates a label containing the question name
    
        # Creates the edit question button
        row.NewBtn('Edit', lambda question = question: Teacher_InitQuestionForm('edit', username, lambda: Teacher_DisplayQuestionBank(pageDetails), {'id': question[0], 'question': question[1], 'options': JSONLoads(question[2]), 'correct': question[3], 'imageData': question[4]}))
    
        # Creates the delete question button
        questionDeleteBtn = row.NewBtn('Delete', lambda question = question: Teacher_DeleteQuestion(pageDetails, question[0]))
        questionDeleteBtn.config(fg = '#F00')
    
    database.Close()
    
def Teacher_CreateClass(pageDetails):
    titleContentFrame = pageDetails[0]
    mainContentFrame = pageDetails[1]
    username = pageDetails[2]
    accountType = pageDetails[3]
    
    # Creates a new window
    dialog = Dialog('Create a new class', '300x170')
    
    classForm = ValidationForm()
    
    dialogFrame = Frame(dialog, bg = fill)
    dialogFrame.grid(sticky = 'nesw', padx = 10, pady = 10)
    dialogFrame.grid_columnconfigure(0, weight = 1)
   
    # Creates the main title text
    mainTitle = Label(dialogFrame, bg = fill, font = 'Arial 11 bold', text = 'Create a new class')
    mainTitle.grid(sticky = 'ew')
    
    details = Frame(dialogFrame, bg = fill)
    details.grid(row = 1, pady = (20, 0))
    
    # Creates the class name text
    classNameText = Label(details, bg = fill, font = 'Arial 10', text = 'Class Name:')
    classNameText.grid(row = 0, padx = (0, 5))
    
    # Creates the class name input
    classNameInput = Entry(details, bg = '#DDD', font = 'Arial 11')
    classNameInput.grid(row = 0, column = 1, padx = (5, 0))
    
    # Adds validation rules to the class name
    className = classForm.NewInput(classNameInput, 'Entry')
    className.AddRule('.{1}', 'Class Name cannot be left empty')
    className.AddRule('^.{,40}$', 'Class Name cannot exceed 40 characters')

    # Validation function called after user presses "Submit"
    def Validate(value):
        if value == True:
            # Remove errors - Form is validated
            error.configure(text = '')
            
            # Generates a unique ID for the class
            classCode = GenerateCode('Classes', 'ID', 8)
            
            # Create new record in Classes table
            InsertData('Classes', ['ID', 'NAME', 'TEACHERID'], [classCode, className.value, username])
            
            dialog.destroy() # Closes the current window
            
            Teacher_DisplayClasses(pageDetails) # Refreshes screen
        else:
            # Form is invalid - shown an error
            error.configure(text = value)

    # Creates the submit button
    submitBtn = Button(dialogFrame, bg = '#DDD', text = 'Submit', command = lambda: classForm.Validate(Validate))
    submitBtn.grid(pady = (25, 0))
    
    # Creates the error message text
    error = Label(dialogFrame, bg = fill, fg = '#F00')
    error.grid(pady = (10, 0))
    
def Teacher_DeleteClass(pageDetails, classID):
    titleContentFrame = pageDetails[0]
    mainContentFrame = pageDetails[1]
    username = pageDetails[2]
    accountType = pageDetails[3]
    
    # Finds the class name
    database = NewConnection()
    database.cursor.execute('SELECT NAME FROM Classes WHERE ID = ?', [classID])
    className = database.cursor.fetchone()[0]
    database.Close()
    
    # Displays warning message
    confirm = messagebox.askquestion(title = 'Delete "' + className + '"', message = 'This action cannot be undone. Are you sure you want to delete this class?')
    if confirm == 'yes':
        # Delete class from Classes table
        database = NewConnection()
        database.cursor.execute('DELETE FROM Classes WHERE ID = ?', [classID])
        database.conn.commit()
        database.Close()

        Teacher_DisplayClasses(pageDetails) # Refreshes screen

def Teacher_DisplayClasses(pageDetails):
    titleContentFrame = pageDetails[0]
    mainContentFrame = pageDetails[1]
    username = pageDetails[2]
    accountType = pageDetails[3]
    
    # Delete widgets from the main screen
    for widget in titleContentFrame.winfo_children():
       widget.destroy()
    for widget in mainContentFrame.winfo_children():
       widget.destroy()
       
    # Creates the selected title text
    selectedTitle = Label(titleContentFrame, bg = fill, text = 'Classes', font = 'Arial 13 bold', anchor = 'w')
    selectedTitle.grid(sticky = 'nw')
    
    # Creates the new class button
    newClassBtn = Button(titleContentFrame, bg = '#DDD', text = 'Create a class', font = 'Arial 10', command = lambda: Teacher_CreateClass(pageDetails))
    newClassBtn.grid(row = 0, sticky = 'e')
    
    # Creates a new scrollable table for the classes
    classes = Table(mainContentFrame, 326)
    classes.NewHeaderValue('Name', 335) # Column 1 - Class name
    classes.NewHeaderValue('Class Code', 100) # Column 2 - Class code
    classes.NewHeaderValue('', 60) # Column 3 - Open class button
    classes.NewHeaderValue('', 60) # Column 4 - Delete class button
    
    # Searches for all of the classes created by the teacher
    database = NewConnection()
    database.cursor.execute('SELECT ID, NAME FROM Classes WHERE TEACHERID = ?', [username])
    result = database.cursor.fetchall()
    database.Close()
    
    # Loops through all the classes
    for i in result:
        row = NewRow(classes)
        
        row.NewLabel(i[1]) # Creates a label containing the class name
        row.NewLabel(i[0]) # Creates a label containing the class code
        
        # Creates the open class button
        row.NewBtn('Open', lambda i = i: Teacher_DisplaySpecificClass(pageDetails, i[0]))
        
        # Creates the delete class button
        deleteClassBtn = row.NewBtn('Delete', lambda i = i: Teacher_DeleteClass(pageDetails, i[0]))
        deleteClassBtn.configure(fg = '#F00')

def Teacher_DeleteQuiz(pageDetails, classID, versionID):
    titleContentFrame = pageDetails[0]
    mainContentFrame = pageDetails[1]
    username = pageDetails[2]
    accountType = pageDetails[3]
    
    # Finds the quiz name
    database = NewConnection()
    database.cursor.execute('SELECT NAME FROM QuizVersions WHERE ID = ?', [versionID])
    quizName = database.cursor.fetchone()[0]
    database.Close()

    # Displays warning message		
    confirm = messagebox.askquestion(title = 'Delete "' + quizName + '"', message = 'This action cannot be undone. Are you sure you want to delete this quiz?')
    if confirm == 'yes':
        # Updates the deleted state of the record in the Quizzes table
        database = NewConnection()
        database.cursor.execute('UPDATE Quizzes SET DELETED = 1 WHERE CURRENTVERSIONID = ?', [versionID])
        database.conn.commit()
        database.Close()
        
        Teacher_DisplaySpecificClass(pageDetails, classID) # Refreshes screen
    
def Teacher_DisplaySpecificClass(pageDetails, classID):
    titleContentFrame = pageDetails[0]
    mainContentFrame = pageDetails[1]
    username = pageDetails[2]
    accountType = pageDetails[3]
    
    # Delete widgets from the main screen
    for widget in titleContentFrame.winfo_children():
       widget.destroy()
    for widget in mainContentFrame.winfo_children():
       widget.destroy()
    
    # Creates a button that returns to the classes page
    quizFrame = MenuFrame(titleContentFrame, 'Return to Classes', lambda: Teacher_DisplayClasses(pageDetails))
    
    database = NewConnection()
    
    # Finds the class name
    database.cursor.execute('SELECT NAME FROM Classes WHERE ID = ?', [classID])
    className = database.cursor.fetchone()[0]
    
    # Creates the delete class button
    deleteClassBtn = Button(titleContentFrame, bg = '#DDD', fg = '#F00', text = 'Delete Class', font = 'Arial 10 bold', command = lambda: Teacher_DeleteClass(pageDetails, classID))
    deleteClassBtn.grid(row = 0, column = 1, sticky = 'e')
    
    # Creates the class name text
    classNameLabel = Label(titleContentFrame, bg = fill, text = className, font = 'Arial 14 bold')
    classNameLabel.grid(sticky = 'w', pady = (10, 0))
    
    # Creates the class code text
    classCodeLabel = Label(titleContentFrame, bg = fill, text = 'Class code: ' + classID, font = 'Arial 12')
    classCodeLabel.grid(sticky = 'w')
    
    # Creates the tab container
    tabParent = ttk.Notebook(mainContentFrame, height = 248, width = 593)
    tabParent.grid(row = 1, pady = (15, 0))
    
    # Creates tabs
    tabQuizzes = Frame(tabParent, bg = fill)
    tabStudents = Frame(tabParent, bg = fill)
    
    # Adds the tabs to the tab container
    tabParent.add(tabQuizzes, text = 'Quizzes')
    tabParent.add(tabStudents, text = 'Students')
    
    # Tab for quizzes
    
    # Creates the create quiz button
    createQuizBtn = Button(tabQuizzes, bg = '#DDD', text = 'Create a quiz', font = 'Arial 10', command = lambda: Teacher_InitQuizForm('create', classID, lambda: Teacher_DisplaySpecificClass(pageDetails, classID)))
    createQuizBtn.grid(pady = (10, 10))
    
    # Creates a new scrollable table for the quizzes within the class
    quizzes = Table(tabQuizzes, 176)
    quizzes.NewHeaderValue('Name', 291) # Column 1 - Quiz name
    quizzes.NewHeaderValue('Length', 100) # Column 2 - Number of questions in quiz
    quizzes.NewHeaderValue('', 50) # Column 3 - Open button
    quizzes.NewHeaderValue('', 40) # Column 4 - Edit button
    quizzes.NewHeaderValue('', 65) # Column 5 - Delete button
    
    # Searches for all of the quizzes created by the teacher within the class
    database.cursor.execute('SELECT ID, NAME, DUEDATE FROM QuizVersions WHERE ID IN (SELECT CURRENTVERSIONID FROM Quizzes WHERE CLASSID = ? AND DELETED = 0) ORDER BY DATE DESC', [classID])
    result = database.cursor.fetchall()

    # Loops through all of the quizzes
    for quiz in result:
        # Searches for all the questions within the quiz
        database.cursor.execute('SELECT QUESTIONID FROM QuizVersionsLinkQuestions WHERE QUIZVERSIONID = ?', [quiz[0]])
        questions = database.cursor.fetchall()
        
        row = NewRow(quizzes)
        
        row.NewLabel(quiz[1]) # Creates a label containing the quiz name
        
        questionsLength = str(len(questions)) + ' questions'
        if len(questions) == 1:
            questionsLength = str(len(questions)) + ' question'
        row.NewLabel(questionsLength) # Creates a label containing the number of questions within the quiz
        
        # Creates the open quiz button
        row.NewBtn('Open', lambda quiz = quiz: Teacher_DisplaySpecificQuiz(pageDetails, classID, quiz[0]))

        # Creates the edit quiz button
        row.NewBtn('Edit', lambda quiz = quiz: Teacher_InitQuizForm('edit', classID, lambda: Teacher_DisplaySpecificClass(pageDetails, classID), quiz[0]))
        
        # Creates the delete quiz button
        deleteBtn = row.NewBtn('Delete', lambda quiz = quiz: Teacher_DeleteQuiz(pageDetails, classID, quiz[0]))
        deleteBtn.configure(fg = '#F00')

    database.Close()
    
    # Tab for students
    
    # Creates a new scrollable table for the students in the class
    students = Table(tabStudents, 224)
    students.NewHeaderValue('Name', 566) # Column 1 - Student name
    
    # Searches for all of the students in the class
    database = NewConnection()
    database.cursor.execute('SELECT FNAME, LNAME FROM Users WHERE USERNAME IN (SELECT STUDENTID FROM Enrolments WHERE CLASSID = ?)', [classID])
    result = database.cursor.fetchall()
    database.Close()

     # Loops through all of the students
    for student in result:
        row = NewRow(students)
        
        row.NewLabel(' '.join(student)) # Creates a label containing the student name

def Teacher_DisplaySpecificQuiz(pageDetails, classID, quizVersionID):
    titleContentFrame = pageDetails[0]
    mainContentFrame = pageDetails[1]
    username = pageDetails[2]
    accountType = pageDetails[3]
    
    # Delete widgets from the main screen
    for widget in titleContentFrame.winfo_children():
       widget.destroy()
    for widget in mainContentFrame.winfo_children():
       widget.destroy()
    
    database = NewConnection()
    
    # Finds the class name
    database.cursor.execute('SELECT NAME FROM Classes WHERE ID = ?', [classID])
    className = database.cursor.fetchone()[0]
    
    # Creates a button that returns to the specific class
    quizFrame = MenuFrame(titleContentFrame, 'Return to "' + className + '"', lambda: Teacher_DisplaySpecificClass(pageDetails, classID))
    
    # Creates the edit quiz button
    quizEditBtn = Button(titleContentFrame, bg = '#DDD', text = 'Edit Quiz', font = 'Arial 10 bold', command = lambda: Teacher_InitQuizForm('edit', classID, lambda: Teacher_DisplaySpecificClass(pageDetails, classID), quizVersionID))
    quizEditBtn.grid(row = 1, column = 1, sticky = 'e', padx = (0, 10))

    # Creates the delete quiz button
    quizDeleteBtn = Button(titleContentFrame, bg = '#DDD', fg = '#F00', text = 'Delete Quiz', font = 'Arial 10 bold', command = lambda: Teacher_DeleteQuiz(pageDetails, classID, quizVersionID))
    quizDeleteBtn.grid(row = 1, column = 2, sticky = 'e')
    
    # Finds the name and due date for the quiz
    database.cursor.execute('SELECT NAME, DUEDATE FROM QuizVersions WHERE ID = ?', [quizVersionID])
    result = database.cursor.fetchone()

    quizName = result[0]
    dueDate = result[1]
    
    # Formats the due date into a string
    quizDueDate = datetime.fromtimestamp(dueDate).strftime('Due: %a %d %b')

    # Creates the quiz name text
    quizNameLabel = Label(titleContentFrame, bg = fill, text = quizName, font = 'Arial 14 bold')
    quizNameLabel.grid(row = 1, sticky = 'w', pady = (10, 0))

    # Creates the quiz due date text
    quizDueDateLabel = Label(titleContentFrame, bg = fill, text = quizDueDate, font = 'Arial 12')
    quizDueDateLabel.grid(row = 2, sticky = 'w')
    
    # Finds the ID of the quiz
    database.cursor.execute('SELECT ID FROM Quizzes WHERE CURRENTVERSIONID = ?', [quizVersionID])
    quizID = database.cursor.fetchone()[0]
    
    # Searches for all of the students in the class who have not completed the quiz
    database.cursor.execute('SELECT STUDENTID FROM Enrolments WHERE CLASSID = ? AND STUDENTID NOT IN (SELECT DISTINCT STUDENTID FROM Records WHERE QUIZID = ?)', [classID, quizID])
    missingStudents = database.cursor.fetchall()
    
    # Searches for all of the students in the class who have completed the quiz on time
    database.cursor.execute('SELECT STUDENTID, MIN(DATE), COUNT(*) FROM Records WHERE QUIZID = ? AND STUDENTID IN (SELECT STUDENTID FROM Enrolments WHERE CLASSID = ?) AND DATE <= ? GROUP BY STUDENTID', [quizID, classID, dueDate])
    onTimeStudents = database.cursor.fetchall()
    
    # Searches for all of the students in the class who have completed the quiz late
    database.cursor.execute('SELECT * FROM (SELECT STUDENTID, MIN(DATE) AS DATE, COUNT(*) FROM Records WHERE QUIZID = ? AND STUDENTID IN (SELECT STUDENTID FROM Enrolments WHERE CLASSID = ?) GROUP BY STUDENTID) AS t WHERE t.DATE > ?', [quizID, classID, dueDate])
    lateStudents = database.cursor.fetchall()
    
    # Counts the number of students who have and have not completed the quiz
    studentCount = str(len(lateStudents) + len(onTimeStudents))
    missingStudentCount = str(len(missingStudents))
    
    # Creates the tab container
    tabParent = ttk.Notebook(mainContentFrame, height = 250, width = 593)
    tabParent.grid(sticky = 'w', pady = (20, 0))
    
    # Creates tabs
    tabCompleted = Frame(tabParent, bg = fill)
    tabMissing = Frame(tabParent, bg = fill)
    
    # Adds the tabs to the tab container
    tabParent.add(tabCompleted, text = 'Completed (' + studentCount + ')')
    tabParent.add(tabMissing, text = 'Missing (' + missingStudentCount + ')')
    
    # Tab for students who completed the quiz

    # Creates a new scrollable table for the students in the class who completed the quiz
    quizzes = Table(tabCompleted, 226)
    quizzes.NewHeaderValue('Student', 191) # Column 1 - Student name
    quizzes.NewHeaderValue('Highest Score', 120) # Column 2 - Highest percentage score
    quizzes.NewHeaderValue('Attempts', 75) # Column 3 - Number of times the student completed the quiz
    quizzes.NewHeaderValue('Date', 100) # Column 4 - Date that the student completed the quiz for the first time
    quizzes.NewHeaderValue('', 60) # Column 5 - Review quiz button
    
    # Loops through all of the students who completed the quiz late
    for n in lateStudents:
        row = NewRow(quizzes)
        row.fill = '#E9713D'
        row.row.configure(bg = '#E9713D')
        
        # Finds the full name of the student
        database.cursor.execute('SELECT FNAME, LNAME FROM Users WHERE USERNAME = ?', [n[0]])
        name = ' '.join(database.cursor.fetchone())
        
        row.NewLabel(name) # Creates a label containing the student name
        
        # Finds the quiz record of the student
        database.cursor.execute('SELECT QUIZVERSIONID, PERCENTAGE FROM Records WHERE QUIZID = ? AND STUDENTID = ? ORDER BY PERCENTAGE DESC', [quizID, n[0]])
        result = database.cursor.fetchone()
        
        score = str(result[1]) + '%'
        
        row.NewLabel(score) # Creates a label containing the highest score
        row.NewLabel(str(n[2])) # Creates a label containing the number of attempts
        row.NewLabel(datetime.fromtimestamp(n[1]).strftime('Late, %d %b')) # Creates a label containing the date the quiz was first completed
        
        # Creates the quiz review button
        row.NewBtn('Review', lambda result = result, n = n: ReviewQuiz(pageDetails, result[0], n[0], quizName, lambda: Teacher_DisplaySpecificQuiz(pageDetails, classID, quizVersionID)))
    
    # Loops through all of the students who completed the quiz on time
    for n in onTimeStudents:
        row = NewRow(quizzes)
        
        # Finds the full name of the student
        database.cursor.execute('SELECT FNAME, LNAME FROM Users WHERE USERNAME = ?', [n[0]])
        name = ' '.join(database.cursor.fetchone())
        
        row.NewLabel(name) # Creates a label containing the student name
        
        # Finds the quiz record of the student
        database.cursor.execute('SELECT QUIZVERSIONID, PERCENTAGE FROM Records WHERE QUIZID = ? AND STUDENTID = ? ORDER BY PERCENTAGE DESC', [quizID, n[0]])
        result = database.cursor.fetchone()
        
        score = str(result[1]) + '%'
        
        row.NewLabel(score) # Creates a label containing the highest score
        row.NewLabel(str(n[2])) # Creates a label containing the number of attempts
        row.NewLabel(datetime.fromtimestamp(n[1]).strftime('%d %b')) # Creates a label containing the date the quiz was first completed
        
        # Creates the quiz review button
        row.NewBtn('Review', lambda result = result, n = n: ReviewQuiz(pageDetails, result[0], n[0], quizName, lambda: Teacher_DisplaySpecificQuiz(pageDetails, classID, quizVersionID)))

    # Tab for students who haven't completed the quiz

    # Creates a new scrollable table for the students in the class who have not completed the quiz
    quizzes = Table(tabMissing, 226)
    quizzes.NewHeaderValue('Student', 566) # Column 1 - Student name

    # Loops through all of the students who have not completed the quiz 
    for n in missingStudents:
        row = NewRow(quizzes)

        # Finds the full name of the student
        database.cursor.execute('SELECT FNAME, LNAME FROM Users WHERE USERNAME = ?', [n[0]])
        name = ' '.join(database.cursor.fetchone())

        row.NewLabel(name) # Creates a label containing the student name
        
def Teacher_InitQuizForm(mode, classID, callback, *quizVersionID):
    if mode == 'create':
        date = datetime.combine(datetime.today(), datetime.min.time()) + relativedelta(days = 1) - relativedelta(microseconds = 1)
        timestamp = int(mktime(date.timetuple()))
      
        # Generates a unique ID for the quiz
        quizID = GenerateCode('Quizzes', 'ID', 32)
        
        data = [{'id': quizID, 'name': '', 'due': timestamp, 'questions': []}]
        
        dialog = Dialog('Create a new quiz', '540x550')
    elif mode == 'edit':
        quizVersionID = quizVersionID[0]
        
        database = NewConnection()
        
        database.cursor.execute('SELECT NAME, DUEDATE FROM QuizVersions WHERE ID = ?', [quizVersionID])
        result = database.cursor.fetchone()
        
        questions = []
        database.cursor.execute('SELECT QUESTIONID FROM QuizVersionsLinkQuestions WHERE QUIZVERSIONID = ?', [quizVersionID])
        questions = [item[0] for item in database.cursor.fetchall()]
        
        database.Close()
        
        data = [{'id': quizVersionID, 'name': result[0], 'due': result[1], 'questions': questions}]
        
        dialog = Dialog('Edit Quiz', '540x550')
    else:
        return
    
    Teacher_UpdateQuizForm(dialog, mode, classID, callback, data[0])

def Teacher_UpdateQuizForm(dialog, mode, classID, callback, data):
    for widget in dialog.winfo_children():
        widget.destroy()
        
    quizForm = ValidationForm()
    
    dialog.grid_rowconfigure(0, weight = 0)
    
    # Creates the main title text
    dialogTitle = Label(dialog, bg = fill, font = 'Arial 14 bold', text = 'Create a new quiz')
    if mode == 'edit':
        dialogTitle.config(text = 'Edit quiz')
    
    dialogTitle.grid(pady = 20)
    
    # Creates the quiz name header
    quizNameText = Label(dialog, bg = fill, font = 'Arial 12 bold', text = 'Quiz name')
    quizNameText.grid(pady = (0, 10))
    
    # Creates the quiz name input
    quizNameInput = Text(dialog, bg = '#DDD', font = 'Arial 12', width = 30, height = 2)
    quizNameInput.grid(pady = (0, 10))
    quizNameInput.insert(INSERT, data['name'])
    
    # Adds validation rules to the quiz name
    quizName = quizForm.NewInput(quizNameInput, 'Text')
    quizName.AddRule('.{1}', 'Quiz name cannot be left empty')
    quizName.AddRule('^.{,25}$', 'Quiz name cannot exceed 25 characters')
    
    # Creates the questions header
    questionsTitle = Label(dialog, bg = fill, font = 'Arial 12 bold', text = 'Questions')
    questionsTitle.grid(pady = (0, 10))
    
    # Function opens a new window which allows the user to insert a question
    def AddQuestion():
        def ConfirmAddQuestion(questionID):
            data['questions'].append(questionID)
            newQuestionDialog.destroy()
            
            quizName.UpdateValue()
            data['name'] = quizName.value # Saves the updated value for the quiz name
            
            
            return Teacher_UpdateQuizForm(dialog, mode, classID, callback, data)
            
        # Creates a new window
        newQuestionDialog = Dialog('Add a new question', '400x200')
        
        dialogFrame = Frame(newQuestionDialog, bg = fill)
        dialogFrame.grid(sticky = 'nesw', padx = 10, pady = 10)
        
        dialogFrame.grid_columnconfigure(0, weight = 1)
        
        # Creates the question title text
        questionTitle = Label(dialogFrame, bg = fill, font = 'Arial 11 bold', text = 'Add a new question')
        questionTitle.grid(sticky = 'ew', pady = (0, 10))
        
        # Creates a new scrollable table for the questions
        questions = Table(dialogFrame, 140)
        questions.NewHeaderValue('Question', 360) # Column 1 - Question name
        questions.NewHeaderValue('', 40) # Column 2 - Add button
        questions.header.destroy()

        array = ['']
        array = array + data['questions']
        arrayString = '('
        for n in range(len(array)):
            arrayString += '"' + array[n] + '"'
            
            if n < len(array) - 1:
                arrayString += ','
        arrayString += ')'
        
        # Search for questions from the question bank which are not already in the quiz
        database = NewConnection()
        database.cursor.execute('SELECT ID, QUESTION FROM QuestionVersions WHERE ID IN (SELECT CURRENTVERSIONID FROM Questions WHERE TEACHERID = (SELECT TEACHERID FROM Classes WHERE ID = ?) AND ID NOT IN ' + arrayString + ' AND DELETED = 0)', [classID])
        result = database.cursor.fetchall()
        
        # Loops through all of the questions
        for question in result:
            database.cursor.execute('SELECT ID FROM Questions WHERE CURRENTVERSIONID = ?', [question[0]])
            questionID = database.cursor.fetchone()[0]
            
            row = NewRow(questions)
            
            row.NewLabel(question[1]) # Creates a label containing the question title
            
            # Creates the add question button
            row.NewBtn('Add', lambda questionID = questionID: ConfirmAddQuestion(questionID))

        database.Close()
    
    # Creates the add question button
    addQuestionBtn = Button(dialog, bg = '#DDD', font = 'Arial 10 bold', text = 'Add Question', command = AddQuestion)
    addQuestionBtn.grid(pady = (0, 10))
    
    questionsContainer = Frame(dialog, bg = fill)
    questionsContainer.grid()
    
    # Creates a new scrollable table for the questions
    questions = Table(questionsContainer, 200)
    questions.NewHeaderValue('', 25) # Column 1 - Question index
    questions.NewHeaderValue('', 340) # Column 2 - Question title
    questions.NewHeaderValue('', 50) # Column 3 - Delete button
    questions.header.destroy()
    
    # Function removes a specific question from the quiz
    def DeleteQuestion(index):
        data['questions'].pop(index)
        
        quizName.UpdateValue()
        data['name'] = quizName.value # Saves the updated value for the quiz name
        
        return Teacher_UpdateQuizForm(dialog, mode, classID, callback, data)
    
    database = NewConnection()
    
    # Loops through all of the questions in the quiz
    for n in range(len(data['questions'])):
        row = NewRow(questions)
        
        row.NewLabel(n + 1) # Creates a label containing the question index
        
        # Finds the question title for the question
        database.cursor.execute('SELECT QUESTION FROM QuestionVersions WHERE ID = (SELECT CURRENTVERSIONID FROM Questions WHERE ID = ?)', [data['questions'][n]])
        result = database.cursor.fetchone()
        
        row.NewLabel(result[0]) # Creates a label containing the question title
        
        # Creates the delete question button
        questionDelete = Button(row.row, bg = '#DDD', fg = '#F00', font = 'Arial 10 bold', text = 'Delete', command = lambda n = n: DeleteQuestion(n))
        questionDelete.pack(side = 'left')
            
    database.Close()
    
    # Creates the due date header
    quizDueDate = Label(dialog, bg = fill, font = 'Arial 11 bold', text = 'Due Date')
    quizDueDate.grid(pady = (10, 5))

    # Function saves the current value in the calendar
    def UpdateCalendar():
        date = quizCalendar.get_date() + relativedelta(days = 1) - relativedelta(microseconds = 1)
        
        timestamp = int(mktime(date.timetuple()))
        data['due'] = timestamp
    
    # Creates the date selector
    today = datetime.today()
    quizCalendar = DateEntry(dialog, selectmode = 'day', mindate = today, locale = 'en_GB')
    quizCalendar.grid(pady = (0, 10))
    quizCalendar.set_date(datetime.fromtimestamp(data['due']) + relativedelta(microseconds = 1) - relativedelta(days = 1))
    quizCalendar.bind('<<DateEntrySelected>>', lambda value: UpdateCalendar())
    
    questionFooterFrame = Frame(dialog, bg = fill)
    questionFooterFrame.grid(sticky = 'ew', padx = 45)
    
    # Function called when user presses "Cancel"
    def Cancel():
        if mode == 'create':
            confirm = messagebox.askquestion(title = 'Cancel', message = 'This action cannot be undone. Are you sure you want to delete this quiz?')
        elif mode == 'edit':
            confirm = messagebox.askquestion(title = 'Cancel', message = 'This action cannot be undone. Are you sure you want to undo any changes made to this quiz?')
    
        if confirm == 'yes':
            dialog.destroy() # Closes the current window
   
    # Creates the cancel button
    cancelBtn = Button(questionFooterFrame, bg = '#DDD', font = 'Arial 11 bold', text = 'Cancel', command = Cancel)
    cancelBtn.pack(side = 'left', anchor = 's', pady = (0, 10))
    
    # Validation function called after user presses "Finish"
    def Validate(value):
        if value == True:
            if len(data['questions']) < 1:
                # Form is invalid - shown an error
                error.config(text = 'You must have at least one question')
                return False
            
            # Remove errors - Form is validated
            error.configure(text = '')
            
            quizName.UpdateValue()
            data['name'] = quizName.value # Saves the updated value for the quiz name
            
            currentTimestamp = datetime.now().timestamp() # The current time in Unix format
            
            quizVersionID = GenerateCode('QuizVersions', 'ID', 32) # Generates new version ID
            
            # Creates new record in Quiz Versions table
            InsertData('QuizVersions', ['ID', 'NAME', 'DATE', 'DUEDATE'], [quizVersionID, data['name'], currentTimestamp, data['due']])
            
            if mode == 'create':
                # Creates new record in Quizzes table
                InsertData('Quizzes', ['ID', 'CLASSID', 'CURRENTVERSIONID'], [data['id'], classID, quizVersionID])
            
            elif mode == 'edit':
                # Updates current version ID for record in Quizzes table
                database = NewConnection()
                database.cursor.execute('UPDATE Quizzes SET CURRENTVERSIONID = ? WHERE CURRENTVERSIONID = ?', [quizVersionID, data['id']])
                database.conn.commit()
                database.Close()
                
            # Loop through all of the questions in the quiz
            for questionID in data['questions']:
                # Creates new record in Quiz Versions Link Questions table
                InsertData('QuizVersionsLinkQuestions', ['QUIZVERSIONID', 'QUESTIONID'], [quizVersionID, questionID])
            
            dialog.destroy() # Closes the current window
            
            return callback()
        else:
            # Form is invalid - shown an error
            error.configure(text = value)
            
    # Creates the finish button
    finishBtn = Button(questionFooterFrame, bg = '#DDD', font = 'Arial 11 bold', text = 'Finish', command = lambda: quizForm.Validate(Validate))
    finishBtn.pack(side = 'right', anchor = 's', pady = (0, 10))
    
    # Creates the error message text
    error = Label(questionFooterFrame, bg = fill, fg = '#F00', font = 'Arial 11')
    error.pack(anchor = 's', pady = (0, 10))
    
def Teacher_InitQuestionForm(mode, teacherID, callback, *data):
    if mode == 'create':
        # Generates a unique ID for the question
        questionID = GenerateCode('Questions', 'ID', 32)
        
        data = [{'id': questionID, 'question': '', 'options': ['', ''], 'correct': 0, 'imageData': None}]
        dialog = Dialog('Create a new question', '540x640')
    elif mode == 'edit':
        dialog = Dialog('Edit Question', '540x640')
    else:
        return
    
    Teacher_UpdateQuestionForm(dialog, mode, teacherID, callback, data[0])

def Teacher_UpdateQuestionForm(dialog, mode, teacherID, callback, data):
    for widget in dialog.winfo_children():
        widget.destroy()
    
    def UploadImage():
        # Opens image file dialog
        filename = filedialog.askopenfilename(
            title = 'Choose an image',
            filetypes = [
               ('Images', '*.png;*.jpg'),
        ])
    
        if filename is not None and len(filename) > 0: # Has the user chosen an image
            size = int(OSPath.getsize(filename))
            sizeInMB = size / (1 * 10**6)
                    
            if sizeInMB > 5: # Invalid - Filesize exceeds 5MB
                messagebox.showerror('Upload Error', 'Image exceeds 5MB')
            else: # Valid file
                newImage = PILImage.open(filename)
                
                # Convert the image to base 64 string
                buffered = BytesIO()
                newImage.save(buffered, format = 'PNG')
                data['imageData'] = b64encode(buffered.getvalue()).decode('ascii')
               
                return Teacher_UpdateQuestionForm(dialog, mode, teacherID, callback, data)
    
    def RemoveImage():
        data['imageData'] = None
        
        return Teacher_UpdateQuestionForm(dialog, mode, teacherID, callback, data)
    
    def DisplayImage():
        global image
        
        if data['imageData'] is not None: # Is there an uploaded image
            image = PhotoImage(data = data['imageData'])
            msg = b64decode(data['imageData'])
            with BytesIO(msg) as buffer:
                with PILImage.open(buffer) as tempImg:
                    # Resizing the image to reduce the filesize
                    imageAspectRatio = image.height() / image.width()
                    
                    largerContainerWidth = 350
                    largerContainerHeight = int(largerContainerWidth * containerAspectRatio)
                    
                    if containerAspectRatio < imageAspectRatio:
                        newImg1 = tempImg.resize((int(largerContainerHeight * 1 / imageAspectRatio), largerContainerHeight), PILImage.ANTIALIAS)
                    else:
                        newImg1 = tempImg.resize((largerContainerWidth, int(largerContainerWidth * imageAspectRatio)), PILImage.ANTIALIAS)
                    
                    newBuffer = BytesIO()
                    newImg1.save(newBuffer, format = 'PNG')
                    newBuffer.seek(0)
                    
                    newImageData = b64encode(newBuffer.read()).decode('ascii')
                    
                    data['imageData'] = newImageData
                    
                    # Resizing the image to fit to the container
                    if containerAspectRatio < imageAspectRatio:
                        newImg1 = tempImg.resize((int(containerHeight * 1 / imageAspectRatio), containerHeight), PILImage.ANTIALIAS)
                    else:
                        newImg1 = tempImg.resize((containerWidth, int(containerWidth * imageAspectRatio)), PILImage.ANTIALIAS)
                    
                    newBuffer = BytesIO()
                    newImg1.save(newBuffer, format = 'PNG')
                    newBuffer.seek(0)
                    
                    newImageData = b64encode(newBuffer.read()).decode('ascii')
                    
                    # Displays the image
                    image = PhotoImage(data = newImageData)
                    Label(imageContainer, image = image, bd = 0).grid()
                    
                    # Text changes because the UploadImage() function can be used to upload a different image
                    imageUploadBtn.configure(text = 'Replace Image (Max 5MB)')
                    
                    # Creates the image delete button
                    imageDeleteBtn = Button(imageOptionsFrame, fg = '#F00', text = 'Remove Image', command = RemoveImage)
                    imageDeleteBtn.grid(row = 0, column = 1, padx = (10, 0), sticky = 'w')
    
    questionForm = ValidationForm()
    
    dialog.grid_rowconfigure(0, weight = 0)
    
    # Creates the main title text
    dialogTitle = Label(dialog, bg = fill, font = 'Arial 14 bold', text = 'Create a new question')
    if mode == 'edit':
        dialogTitle.config(text = 'Edit question')
    
    dialogTitle.grid(pady = 20)
    
    # Creates the question title header
    questionTitleText = Label(dialog, bg = fill, font = 'Arial 12 bold', text = 'Question')
    questionTitleText.grid(pady = (0, 10))
    
    # Creates the question title input
    questionTitleInput = Text(dialog, bg = '#DDD', font = 'Arial 12', width = 50, height = 3)
    questionTitleInput.grid(pady = (0, 10))
    questionTitleInput.insert(INSERT, data['question'])
    
    # Adds validation rules to the question title
    questionTitle = questionForm.NewInput(questionTitleInput, 'Text')
    questionTitle.AddRule('.{1}', 'Question cannot be left empty')
    questionTitle.AddRule('^.{,150}$', 'Question cannot exceed 150 characters')
    
    # Creates the options header
    optionsTitle = Label(dialog, bg = fill, font = 'Arial 12 bold', text = 'Options')
    optionsTitle.grid()
    
    # Creates the options information subheader
    optionsInfo = Label(dialog, bg = fill, font = 'Arial 10', text = 'Use the radio buttons to select the correct answer')
    optionsInfo.grid(pady = (0, 10))
    
    # Function saves the current values in the inputs
    def UpdateValues():
        questionTitle.UpdateValue()
        data['question'] = questionTitle.value
        
        for n in range(1, len(questionForm.inputs)):
            questionForm.inputs[n].UpdateValue()
            data['options'][n - 1] = questionForm.inputs[n].value

    # Function adds a new option
    def NewOption():
        data['options'].append('')
        UpdateValues()
        
        return Teacher_UpdateQuestionForm(dialog, mode, teacherID, callback, data)

    # Creates the new option button
    newOptionBtn = Button(dialog, bg = '#DDD', font = 'Arial 10 bold', text = 'Add Option', command = NewOption)
    newOptionBtn.grid(pady = (0, 10))
    
    optionsContainer = Frame(dialog, bg = fill)
    optionsContainer.grid()
    
    # Creates a new scrollable table for the options
    options = Table(optionsContainer, 85)
    options.noStyle = True
    options.NewHeaderValue('', 25) # Column 1 - Option index
    options.NewHeaderValue('', 320) # Column 2 - Option input field
    options.NewHeaderValue('', 50) # Column 3 - Option delete button
    options.NewHeaderValue('', 20) # Column 4 - Radio button to select option
    options.header.destroy()
    
    # Function deletes a specific option
    def DeleteOption(n):
        UpdateValues()
        
        del data['options'][n]
        del questionForm.inputs[n - 1]

        if n < data['correct']:
            data['correct'] = data['correct'] - 1
        elif n == data['correct']:
            data['correct'] = 0
        
        return Teacher_UpdateQuestionForm(dialog, mode, teacherID, callback, data)
    
    # Function called when user presses radio button next to option
    def UpdateSelection(n):
        for a in range(1, len(questionForm.inputs)):
            questionForm.inputs[a].element.configure(bg = '#DDD')
        
        questionForm.inputs[n + 1].element.configure(bg = '#62CA6D') 
        
        data['correct'] = n
    
    # Loops through all the options
    for n in range(len(data['options'])):
        row = NewRow(options)
        row.NewLabel(n + 1)
        
        # Creates the option input
        optionInput = row.NewEntry()
        optionInput.configure(bg = '#DDD')
        optionInput.insert(INSERT, data['options'][n])
        
        # Adds validation rules to the option input
        option = questionForm.NewInput(optionInput, 'Entry')
        option.AddRule('.{1}', 'Options cannot be left empty')
        option.AddRule('^.{,100}$', 'Options cannot exceed 100 characters')
        
        # Creates the delete option button
        optionDelete = Button(row.row, bg = '#DDD', fg = '#F00', font = 'Arial 10 bold', text = 'Delete', command = lambda n = n: DeleteOption(n))
        optionDelete.pack(side = 'left')

        # Creates the radio button that allows the user to select the correct option
        optionSelection = Radiobutton(row.row, bg = '#DDD', value = (n + 1), command = lambda n = n: UpdateSelection(n))
        optionSelection.pack(side = 'left')
        
        if n == data['correct']:
            optionSelection.select()
            optionInput.configure(bg = '#62CA6D')
            
        # Disables the delete option button if there is only 2 options
        if len(data['options']) <= 2:
            optionDelete.config(state = 'disabled')
        
        # Disables the new option button if there are 5 options
        if len(data['options']) >= 5:
            newOptionBtn.config(state = 'disabled')
    
    # Creates the image header
    imageTitle = Label(dialog, bg = fill, font = 'Arial 12 bold', text = 'Image')
    imageTitle.grid(pady = 10)
    
    imageOptionsFrame = Frame(dialog, bg = fill)
    imageOptionsFrame.grid(pady = (0, 10))
    
    # Creates the image upload button
    imageUploadBtn = Button(imageOptionsFrame, bg = '#DDD', text = 'Upload Image (Max 5MB)', command = UploadImage)
    imageUploadBtn.grid(row = 0, column = 0, sticky = 'w')
    
    # Specifies the dimensions of the displayed image
    containerAspectRatio = 9/16
    containerWidth = 200
    containerHeight = int(containerWidth * containerAspectRatio)
    
    imageContainer = Frame(dialog, bg = fill, width = containerWidth, height = containerHeight, highlightbackground = '#000', highlightthickness = 3)
    imageContainer.grid(pady = (0, 40))
    imageContainer.grid_propagate(0)
    imageContainer.grid_rowconfigure(0, weight = 1)
    imageContainer.grid_columnconfigure(0, weight = 1)
    
    questionFooterFrame = Frame(dialog, bg = fill)
    questionFooterFrame.grid(sticky = 'ew', padx = 45)
    
    # Function called after user presses "Cancel"
    def Cancel():
        if mode == 'create':
            confirm = messagebox.askquestion(title = 'Cancel', message = 'This action cannot be undone. Are you sure you want to delete this question?')
        elif mode == 'edit':
            confirm = messagebox.askquestion(title = 'Cancel', message = 'This action cannot be undone. Are you sure you want to undo any changes made to this question?')
    
        if confirm == 'yes':
            dialog.destroy()
    
    # Validation function called after user presses "Finish"
    def Validate(value):
        if value == True:
            # Remove errors - Form is validated
            error.configure(text = '')
            
            UpdateValues()
            
            timestamp = datetime.now().timestamp() # The current time in Unix format
            
            questionVersionID = GenerateCode('QuestionVersions', 'ID', 32) # Generates new version ID
            
            # Creates new record in Question Versions table
            InsertData('QuestionVersions', ['ID', 'QUESTION', 'OPTIONSJSON', 'CORRECTOPTIONINDEX', 'IMAGEBASE64', 'DATE'], [questionVersionID, data['question'], JSONDumps(data['options']), data['correct'], data['imageData'], timestamp])
            
            if mode == 'create':
                # Creates new record in Questions table
                InsertData('Questions', ['ID', 'TEACHERID', 'CURRENTVERSIONID'], [data['id'], teacherID, questionVersionID])
                
            elif mode == 'edit':
                # Updates current version ID for record in Questions table
                database = NewConnection()
                database.cursor.execute('UPDATE Questions SET CURRENTVERSIONID = ? WHERE CURRENTVERSIONID = ?', [questionVersionID, data['id']])
                database.conn.commit()
                database.Close()
            
            # Closes the current window
            dialog.destroy()
            
            return callback()
        else:
            # Form is invalid - shown an error
            error.configure(text = value)
    
    # Creates the cancel button
    cancelBtn = Button(questionFooterFrame, bg = '#DDD', font = 'Arial 11 bold', text = 'Cancel', command = Cancel)
    cancelBtn.pack(side = 'left', anchor = 's', pady = (0, 10))
    
    # Creates the finish button
    finishBtn = Button(questionFooterFrame, bg = '#DDD', font = 'Arial 11 bold', text = 'Finish', command = lambda: questionForm.Validate(Validate))
    finishBtn.pack(side = 'right', anchor = 's', pady = (0, 10))
    
    # Creates the error message text
    error = Label(questionFooterFrame, bg = fill, fg = '#F00', font = 'Arial 11')
    error.pack(anchor = 's', pady = (0, 10))

    DisplayImage()