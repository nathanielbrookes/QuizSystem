from Global import *

def Student_JoinClass(pageDetails):
    titleContentFrame = pageDetails[0]
    mainContentFrame = pageDetails[1]
    username = pageDetails[2]
    accountType = pageDetails[3]
    
    # Creates a new window
    dialog = Dialog('Join a new class', '300x170')

    classForm = ValidationForm()

    dialogFrame = Frame(dialog, bg = fill)
    dialogFrame.grid(sticky = 'nesw', padx = 10, pady = 10)
    dialogFrame.grid_columnconfigure(0, weight = 1)
    
    # Creates the main title text
    mainTitle = Label(dialogFrame, bg = fill, font = 'Arial 11 bold', text = 'Join a new class')
    mainTitle.grid(sticky = 'ew')
    
    details = Frame(dialogFrame, bg = fill)
    details.grid(row = 1, pady = (20, 0))
    
    # Creates the class code text           
    classCodeText = Label(details, bg = fill, font = 'Arial 10', text = 'Class Code:')
    classCodeText.grid(row = 0, padx = (0, 5))
    
    # Creates the class code input  
    classCodeInput = Entry(details, bg = '#DDD', font = 'Arial 11')
    classCodeInput.grid(row = 0, column = 1, padx = (5, 0))
    
    # Adds validation rules to the class code
    classCode = classForm.NewInput(classCodeInput, 'Entry')
    classCode.AddRule('.{1}', 'Class Code cannot be left empty')

    # Validation function called after user presses "Submit"
    def Validate(value):
        if value == True:
            # Remove errors - Form is validated (client-side only)
            error.configure(text = '')
            
            # Server-side validation
            database = NewConnection()
            database.cursor.execute('SELECT * FROM Classes WHERE ID = ?', [classCode.value])
            result = database.cursor.fetchall()
            
            if len(result) == 0:
                # Form is invalid - show an error
                error.configure(text = 'Class Code does not exist')
                database.Close()
                return
            else:
                # Server-side validation
                database.cursor.execute('SELECT COUNT(*) FROM Enrolments WHERE CLASSID = ? AND STUDENTID = ?', [classCode.value, username])
                if database.cursor.fetchone()[0] > 0:
                    # Form is invalid - show an error
                    error.configure(text = 'You have already joined this class')
                    database.Close()
                    return
                else:
                    # Create a new record in the Enrolments table
                    InsertData('Enrolments', ['CLASSID', 'STUDENTID'], [classCode.value, username])
            
            database.Close()
            
            dialog.destroy() # Deletes the current window
            
            Student_DisplayClasses(pageDetails) # Refreshes the screen
        else:
            # Form is invalid - show an error
            error.configure(text = value)

    # Creates the submit button
    submitBtn = Button(dialogFrame, bg = '#DDD', text = 'Submit', command = lambda: classForm.Validate(Validate))
    submitBtn.grid(pady = (25, 0))
    
    # Creates the error message text
    error = Label(dialogFrame, bg = fill, fg = '#F00', text = '')
    error.grid(pady = (10, 0))

def Student_LeaveClass(pageDetails, classID):
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
    confirm = messagebox.askquestion(title = 'Leave "' + className + '"', message = 'Are you sure you want to leave this class?')
    if confirm == 'yes':
        # Deletes record from Enrolments table
        database = NewConnection()
        database.cursor.execute('DELETE FROM Enrolments WHERE CLASSID = ? AND STUDENTID = ?', [classID, username])
        database.conn.commit()
        database.Close()
								
        Student_DisplayClasses(pageDetails) # Refreshes the screen

def Student_DisplayClasses(pageDetails):
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
    
    joinClassBtn = Button(titleContentFrame, bg = '#DDD', text = 'Join a class', font = 'Arial 10', command = lambda: Student_JoinClass(pageDetails))
    joinClassBtn.grid(row = 0, column = 1, sticky = 'e')
    
    # Creates a new scrollable table for the classes joined by the student
    classes = Table(mainContentFrame, 326)
    classes.NewHeaderValue('Name', 295) # Column 1 - Class name
    classes.NewHeaderValue('Teacher', 140) # Column 2 - Teacher name
    classes.NewHeaderValue('', 60) # Column 3 - Open class button
    classes.NewHeaderValue('', 60) # Column 4 - Leave class button
    
    # Searches for all of the classes joined by the student
    database = NewConnection()
    database.cursor.execute('SELECT ID, NAME FROM Classes WHERE ID IN (SELECT CLASSID FROM Enrolments WHERE STUDENTID = ?)', [username])
    result = database.cursor.fetchall()
    
    # Loops through all the classes joined by the student
    for i in result:
        row = NewRow(classes)
        
        # Finds the name of the teacher who created the class
        database.cursor.execute('SELECT FNAME, LNAME FROM Users WHERE USERNAME = (SELECT TEACHERID FROM Classes WHERE ID = ?)', [i[0]])
        teacherName = ' '.join(database.cursor.fetchone())
        
        row.NewLabel(i[1]) # Creates a label containing the class name
        row.NewLabel(teacherName) # Creates a label containing the name of the teacher who created the class
        
        # Creates the open class button
        row.NewBtn('Open', lambda i = i: Student_DisplaySpecificClass(pageDetails, i[0]))
        
        # Creates the leave class button
        leaveBtn = row.NewBtn('Leave', lambda i = i: Student_LeaveClass(pageDetails, i[0]))
        leaveBtn.configure(fg = '#F00')

    database.Close()
   
def Student_DisplaySpecificClass(pageDetails, classID):
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
    quizFrame = MenuFrame(titleContentFrame, 'Return to Classes', lambda: Student_DisplayClasses(pageDetails))
    
    database = NewConnection()
    
    # Finds the class name
    database.cursor.execute('SELECT NAME FROM Classes WHERE ID = ?', [classID])
    className = database.cursor.fetchone()[0]
        
    # Creates the leave class button
    leaveClassBtn = Button(titleContentFrame, bg = '#DDD', fg = '#F00', text = 'Leave Class', font = 'Arial 10 bold', command = lambda: Student_LeaveClass(pageDetails, classID))
    leaveClassBtn.grid(row = 0, column = 1, sticky = 'e')
    
    # Creates the class name text
    classNameLabel = Label(titleContentFrame, bg = fill, text = className, font = 'Arial 14 bold')
    classNameLabel.grid(sticky = 'w', pady = (10, 0))
    
    # Creates the class code text
    classCodeLabel = Label(titleContentFrame, bg = fill, text = 'Class code: ' + classID, font = 'Arial 12')
    classCodeLabel.grid(sticky = 'w')
    
    # Searches for all of the quizzes in the class not completed by the student
    database.cursor.execute('SELECT ID, NAME, DUEDATE FROM QuizVersions WHERE ID IN (SELECT CURRENTVERSIONID FROM Quizzes WHERE CLASSID = ? AND ID NOT IN (SELECT DISTINCT QUIZID FROM Records WHERE STUDENTID = ?) AND DELETED = 0) ORDER BY DATE DESC', [classID, username])
    incompleteQuizzes = database.cursor.fetchall()
    
    # Searches for all of the quizzes in the class completed by the student
    database.cursor.execute('SELECT ID, NAME, DUEDATE FROM QuizVersions WHERE ID IN (SELECT CURRENTVERSIONID FROM Quizzes WHERE CLASSID = ? AND ID IN (SELECT DISTINCT QUIZID FROM Records WHERE STUDENTID = ?)) ORDER BY DATE DESC', [classID, username])
    completedQuizzes = database.cursor.fetchall()
    
    # Counts the number of completed and not completed quizzes
    incompleteQuizzesCount = str(len(incompleteQuizzes))
    completedQuizzesCount = str(len(completedQuizzes))
    
    # Creates the tab container
    tabParent = ttk.Notebook(mainContentFrame, height = 254, width = 593)
    tabParent.grid(row = 1, pady = (15, 0))

    # Creates tabs
    tabIncomplete = Frame(tabParent, bg = fill)
    tabCompleted = Frame(tabParent, bg = fill)
    
    # Adds the tabs to the tab container
    tabParent.add(tabIncomplete, text = 'To be done (' + incompleteQuizzesCount + ')')
    tabParent.add(tabCompleted, text = 'Done (' + completedQuizzesCount + ')')

    # Tab for not completed quizzes

    # Creates a new scrollable table for the quizzes not completed by the student
    quizzes = Table(tabIncomplete, 229)
    quizzes.NewHeaderValue('Quiz Name', 276) # Column 1 - Quiz name
    quizzes.NewHeaderValue('Due Date', 120) # Column 2 - Deadline date for the quiz
    quizzes.NewHeaderValue('Length', 100) # Column 3 - Number of questions in the quiz
    quizzes.NewHeaderValue('', 55) # Column 4 - Start quiz button
    
    # Loop through all of the quizzes not completed by the student
    for quiz in incompleteQuizzes:
        row = NewRow(quizzes)
        
        row.NewLabel(quiz[1]) # Creates a label containing the quiz name

        # Formats the due date into a string        
        date = datetime.fromtimestamp(quiz[2])
        dueDate = date.strftime('%a %d %b')
        
        quizDueDate = row.NewLabel(dueDate) # Creates a label containing the deadline for the quiz

        now = mktime(datetime.today().timetuple())
        if now > quiz[2]:
            quizDueDate.config(fg = 'red')
            quizDueDate.config(text = 'Late, ' + dueDate)
        
        # Counts the number of questions in the quiz
        database.cursor.execute('SELECT COUNT(*) FROM QuizVersionsLinkQuestions WHERE QUIZVERSIONID = ?', [quiz[0]])
        questionsCount = str(database.cursor.fetchone()[0])
        
        questionsLength = questionsCount + ' questions'
        if questionsCount == 1:
            questionsLength = questionsCount + ' question'
        row.NewLabel(questionsLength) # Creates a label containing the number of questions in the quiz
        
        # Creates the start quiz button
        row.NewBtn('Start', lambda quiz = quiz: Student_StartQuiz(quiz[0], username, lambda: Student_DisplaySpecificClass(pageDetails, classID)))
    
    # Tab for completed quizzes
    
    # Creates a new scrollable table for the quizzes completed by the student
    quizzes = Table(tabCompleted, 229)
    quizzes.NewHeaderValue('Quiz Name', 196) # Column 1 - Quiz name
    quizzes.NewHeaderValue('Length', 100) # Column 2 - Number of times the student has completed the quiz
    quizzes.NewHeaderValue('Highest Score', 113) # Column 3 - Highest percentage score
    quizzes.NewHeaderValue('', 67) # Column 4 - Review quiz button
    quizzes.NewHeaderValue('', 70) # Column 5 - Try again button

    # Loop through all of the quizzes completed by the student
    for quiz in completedQuizzes:
        # Finds the quiz record data
        database.cursor.execute('SELECT QUIZID, QUIZVERSIONID, PERCENTAGE FROM Records WHERE QUIZID = (SELECT ID FROM Quizzes WHERE CURRENTVERSIONID = ?) AND STUDENTID = ? ORDER BY PERCENTAGE DESC', [quiz[0], username])
        record = database.cursor.fetchone()
        
        row = NewRow(quizzes)
        
        # Finds the name of the quiz
        database.cursor.execute('SELECT NAME FROM QuizVersions WHERE ID = ?', [record[1]])
        quizName = database.cursor.fetchone()[0]
        
        row.NewLabel(quizName) # Creates a label containing the quiz name
        
        # Counts the number of questions in the quiz
        database.cursor.execute('SELECT COUNT(*) FROM QuizVersionsLinkQuestions WHERE QUIZVERSIONID = ?', [record[1]])
        questionCount = str(database.cursor.fetchone()[0])
        
        questionsLength = questionCount + ' questions'
        if questionCount == 1:
            questionsLength = questionCount + ' question'
        
        row.NewLabel(questionsLength) # Creates a label containing the number of questions in the quiz
        
        row.NewLabel(str(record[2]) + '%') # Creates a label containg the highest percentage score

        # Creates the review quiz button
        row.NewBtn('Review', lambda record = record: ReviewQuiz(pageDetails, record[1], username, 'Quizzes', lambda: Student_DisplaySpecificClass(pageDetails, classID)))
        
        database.cursor.execute('SELECT CURRENTVERSIONID FROM Quizzes WHERE ID = ? AND DELETED = 0', [record[0]])
        result = database.cursor.fetchone()
        
        if not result == None:
            # Creates the try again button
            row.NewBtn('Try Again', lambda result = result: Student_StartQuiz(result[0], username, lambda: Student_DisplaySpecificClass(pageDetails, classID)))
        else:  
            row.NewLabel('')
            
    database.Close()

def Student_StartQuiz(quizVersionID, studentID, callback):
    # Searches for the questions in the quiz
    database = NewConnection()
    database.cursor.execute('SELECT QUESTIONID FROM QuizVersionsLinkQuestions WHERE QUIZVERSIONID = ?', [quizVersionID])
    result = database.cursor.fetchall()
    database.Close()
    
    # Randomises the order of the questions
    questions = [i[0] for i in result]
    shuffle(questions)
    
    # Creates a new window
    dialog = Dialog('Quiz', '640x640')
    
    # Displays the first question
    Student_DisplayQuestion(dialog, studentID, quizVersionID, questions, [], callback)

def Student_FinishQuiz(dialog, studentID, quizVersionID, recordData, callback):
    # Delete widgets from the screen
    for widget in dialog.winfo_children():
        widget.destroy()
    
    database = NewConnection()
    
    # Find the ID for the quiz
    database.cursor.execute('SELECT ID FROM Quizzes WHERE CURRENTVERSIONID = ?', [quizVersionID])
    quizID = database.cursor.fetchone()[0]
    
    score = sum([i[2] for i in recordData])
    questionsLength = len(recordData)
    percentage = round((score / questionsLength) * 100)
    
    quizFrame = Frame(dialog, bg = fill)
    quizFrame.place(relx=.5, rely=.5, anchor = 'c')
    
    # Creates the percentage score text
    scoreTitle = Label(quizFrame, bg = fill, font = 'Arial 13 bold', text = 'You scored ' + str(percentage) + '%')
    scoreTitle.grid(row = 0)
    
    # Function called after user presses "Retake Quiz"
    def RestartQuiz():
        dialog.destroy()
        
        return Student_StartQuiz(quizVersionID, studentID, callback)
    
    # Creates the retake quiz button
    retakeQuiz = Button(quizFrame, bg = '#DDD', text = 'Retake Quiz', anchor = 'w', command = RestartQuiz)
    retakeQuiz.grid(row = 1)
    
    # Generates a unique ID for the record
    recordID = GenerateCode('Records', 'ID', 32)
    
    currentDate = mktime(datetime.today().timetuple())
    
    # Create new record in Records table
    InsertData('Records', ['ID', 'QUIZID', 'QUIZVERSIONID', 'STUDENTID', 'PERCENTAGE', 'DATE'], [recordID, quizID, quizVersionID, studentID, percentage, currentDate])
    
    # Loops through all of the questions
    for question in recordData:
        questionVersionID = question[0]
        chosenOptionIndex = question[1]
        
        # Create new record in RecordsLinkQuestionVersions table
        InsertData('RecordsLinkQuestionVersions', ['RECORDID', 'QUESTIONVERSIONID', 'CHOSENOPTIONINDEX'], [recordID, questionVersionID, chosenOptionIndex])
    
    database.Close()
    
    return callback()

def Student_DisplayQuestion(dialog, studentID, quizVersionID, remainingQuestions, recordData, callback):
    global image
    
    # Delete widgets from the main screen
    for widget in dialog.winfo_children():
        widget.destroy()
    
    questionID = remainingQuestions.pop()
    
    database = NewConnection()
    
    # Finds the version ID of the current question
    database.cursor.execute('SELECT CURRENTVERSIONID FROM Questions WHERE ID = ?', [questionID])
    questionVersionID = database.cursor.fetchone()[0]
    
    # Finds the question data
    database.cursor.execute('SELECT QUESTION, OPTIONSJSON, CORRECTOPTIONINDEX, IMAGEBASE64 FROM QuestionVersions WHERE ID = ?', [questionVersionID])
    result = database.cursor.fetchone()
    
    database.Close()
    
    questionsLength = len(remainingQuestions) + len(recordData) + 1
    questionTitle = result[0]
    questionOptionsJSON = JSONLoads(result[1])
    questionCorrectOptionIndex = result[2]
    questionImageData = result[3]
    
    # Randomises the order of the options
    options = []
    for i in range(len(questionOptionsJSON)):
        options.append([questionOptionsJSON[i], i])
    shuffle(options)
        
    quizFrame = Frame(dialog, bg = fill)
    quizFrame.place(relx=.5, rely=.5, anchor = 'c')
    
    # Creates a label showing the current question number
    questionIndexText = Label(quizFrame, bg = fill, font = 'Arial 13', text = 'Question ' + str(len(recordData) + 1) + ' out of ' + str(questionsLength))
    questionIndexText.grid(row = 0, pady = (0, 10))
    
    # Creates a label for the question text
    questionTitleText = Message(quizFrame, bg = fill, font = 'Arial 14 bold', text = questionTitle, justify = CENTER, width = 400)
    questionTitleText.grid(row = 1, pady = (0, 10))
    
    # If the question contains an image, display it
    if questionImageData is not None:
        containerAspectRatio = 9/16
        containerWidth = 350
        containerHeight = int(containerWidth * containerAspectRatio)
        
        imageContainer = Frame(quizFrame, bg = fill, width = containerWidth, height = containerHeight, highlightbackground = '#000', highlightthickness = 3)
        imageContainer.grid(pady = (0, 20))
        imageContainer.grid_propagate(0)
        imageContainer.grid_rowconfigure(0, weight = 1)
        imageContainer.grid_columnconfigure(0, weight = 1)
        
        image = PhotoImage(data = questionImageData)
        Label(imageContainer, image = image, bd = 0).grid()      
    
    quizOptions = Frame(quizFrame, bg = fill)
    quizOptions.grid()
    
    # Function called after user chooses an option
    def CheckAnswer(index):
        correct = 0
        
        adjustedIndex = options[index][1]
        if adjustedIndex == questionCorrectOptionIndex:
            # The user was correct
            correct = 1
            
            # Updates the status text to inform the user they answered correctly
            questionStatus.configure(text = 'Correct')
            
            # Changes the background colour of every option to red
            for option in optionElements:
                option.configure(bg = 'red')
              
            # Changes the background colour of the selected option to green
            optionElements[index].configure(bg = 'green')
        else:
            # The user was incorrect
            
            # Updates the status text to inform the user they answered incorrectly
            questionStatus.configure(text = 'Incorrect')
            
            # Changes the background colour of the selected option to red
            optionElements[index].configure(bg = 'red')
            
            # Changes the background colour of the correct option to green
            optionElements[[row[1] for row in options].index(questionCorrectOptionIndex)].configure(bg = 'green')
        
        # Updates the record data
        recordData.append([questionVersionID, adjustedIndex, correct])
        
        # Ensures that a user cannot select an option if they have already chosen one
        for option in optionElements:
            option['command'] = 0
            option['relief'] = 'flat'
        
        # Allows the user to proceed to the next question / finish the quiz
        questionSubmit.configure(state = NORMAL)
    
    optionElements = []
    
    # Creates a button for each option in the question        
    for i in range(len(options)):
        questionOption = Button(quizOptions, bg = '#DDD', font = 'Arial 13', text = options[i][0], command = lambda i = i: CheckAnswer(i))
        questionOption.grid(sticky = 'ew', pady = 5, ipadx = 10)
        
        optionElements.append(questionOption)
     
    # Creates a label containing the current status of the question (incomplete / incorrect / correct)
    questionStatus = Label(quizFrame, bg = fill, font = 'Arial 12', text = 'Select the correct answer')
    questionStatus.grid(pady = (10, 0))
    
    # Creates the next question / finish quiz button
    questionSubmit = Button(quizFrame, bg = '#CCC', font = 'Arial 13', text = 'Next Question', state = DISABLED, command = lambda: Student_DisplayQuestion(dialog, studentID, quizVersionID, remainingQuestions, recordData, callback))
    questionSubmit.grid(pady = (20, 0))
    
    # If there are no more questions left 
    if len(remainingQuestions) == 0:
        questionSubmit.configure(text = 'Finish Quiz', command = lambda: Student_FinishQuiz(dialog, studentID, quizVersionID, recordData, callback))
      
def Student_DisplayStatistics(pageDetails):
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
    selectedTitle = Label(titleContentFrame, bg = fill, text = 'Statistics', font = 'Arial 13 bold', anchor = 'w')
    selectedTitle.grid(sticky = 'nw')
    
    # Counts the number of different quizzes completed by the student
    database = NewConnection()
    database.cursor.execute('SELECT COUNT(*) FROM QuizVersions WHERE ID IN (SELECT CURRENTVERSIONID FROM Quizzes WHERE ID IN (SELECT DISTINCT QUIZID FROM Records WHERE STUDENTID = ?)) ORDER BY DATE DESC', [username])
    completedQuizzesLength = database.cursor.fetchone()[0]

    if completedQuizzesLength == 0: # Student has not completed any quizzes
        noDataLabel = Label(mainContentFrame, bg = fill, text = 'You have not completed any quizzes yet', font = 'Arial 12 bold')
        noDataLabel.grid()

    else: # Student has completed at least one quiz
    
        # Finds the percentage score and date for each quiz completed by the student
        database.cursor.execute('SELECT PERCENTAGE, DATE FROM Records WHERE STUDENTID = ?', [username])
        graphData = database.cursor.fetchall()
        
        generalStatisticsContainer = Frame(mainContentFrame, bg = fill)
        generalStatisticsContainer.grid(row = 1, sticky = 'new', pady = (30, 0))
        
        generalStatisticsContainer.grid_columnconfigure(0, weight = 1)
        generalStatisticsContainer.grid_rowconfigure(0, weight = 1)
        
        # Completed Quizzes Text
    
        completedQuizzesValueLabel = Label(generalStatisticsContainer, bg = fill, text = str(completedQuizzesLength), font = 'Arial 14 bold')
        completedQuizzesValueLabel.grid() 
        
        completedQuizzesLabel = Label(generalStatisticsContainer, bg = fill, text = 'Quizzes Completed', font = 'Arial 11 bold')
        completedQuizzesLabel.grid()
        
        # Average Score Text
        
        today = datetime.combine(datetime.today(), datetime.min.time())
        startDate = today - relativedelta(days = today.weekday() % 7)
        averageScore = Student_CalculateAverageWeekScore(graphData, startDate)
        
        averageScoreText = 'N/A'
        
        if averageScore != None:
            averageScoreText = str(averageScore) + '%'
        
        averageScoreValueLabel = Label(generalStatisticsContainer, bg = fill, text = averageScoreText, font = 'Arial 14 bold')
        averageScoreValueLabel.grid(pady = (20, 0))
        
        averageScoreLabel = Label(generalStatisticsContainer, bg = fill, text = 'Average score this week', font = 'Arial 11 bold')
        averageScoreLabel.grid()
        
        # Percentage Change Text
        
        percentageChange = Student_CalculateWeekPercentageChange(graphData)
        
        if percentageChange != 0:
            if percentageChange > 0:
                percentageChangeText = ' (up by ' + str(abs(percentageChange)) + '% since last week)'
            else:
                percentageChangeText = ' (down by ' + str(abs(percentageChange)) + '% since last week)'
            
            # Creates a label for the percentage change
            percentageChangeLabel = Label(generalStatisticsContainer, bg = fill, text = percentageChangeText, font = 'Arial 11')
            percentageChangeLabel.grid()
            
        # Graph
        
        graphContainer = Frame(mainContentFrame, bg = fill)
        graphContainer.grid(row = 1, column = 1, sticky = 'e')
        
        # Date range options
        options = ['Overall', 'Last 7 Days', 'Last 3 Weeks', 'Last 6 Months']
        variable = StringVar(mainContentFrame)
        variable.set(options[0])
        
        # Creates the date range text
        optionText = Label(graphContainer, bg = fill, text = 'Date Range', font = 'Arial 10 bold')
        optionText.grid()
        
        # Creates the date range selector
        option = ttk.Combobox(graphContainer, values = tuple(options), textvariable = variable, state = 'readonly')
        option.bind('<<ComboboxSelected>>', lambda value: Student_DrawLineGraph(graphContainer, graphData, options.index(variable.get())))
        option.grid()

        # Draws the line graph
        Student_DrawLineGraph(graphContainer, graphData, 0)

    database.Close()
    
# Function to calculate the average percentage score for a specific week       
def Student_CalculateAverageWeekScore(data, startDate):
    # Calculates the end date of the week
    endDate = startDate + relativedelta(days = 7)
    
    startTimestamp = mktime(startDate.timetuple())
    endTimestamp = mktime(endDate.timetuple())
    
    # Searches for the values that are in the week
    data = [x[0] for x in data if (startTimestamp <= x[1] < endTimestamp)]
    
    # If there are no values in the week, return None
    if len(data) == 0:
        return None
    
    # Returns the average percentage score for the week
    return round(sum(data) / len(data))

# Function to calculate percentage change of scores between last week and this week
def Student_CalculateWeekPercentageChange(data):
    today = datetime.combine(datetime.today(), datetime.min.time())
    
    # Calculate average score for the current week
    startDateWeek1 = today - relativedelta(days = today.weekday() % 7)
    averageScoreWeek1 = Student_CalculateAverageWeekScore(data, startDateWeek1)
    
    # Calculate average score for the previous week
    startDateWeek2 = startDateWeek1 - relativedelta(weeks = 1)
    averageScoreWeek2 = Student_CalculateAverageWeekScore(data, startDateWeek2)
    
    # Calculate the percentage change
    change = 0
    if averageScoreWeek2 != 0 and averageScoreWeek1 != None and averageScoreWeek2 != None:
        change = int(((averageScoreWeek1 - averageScoreWeek2) / averageScoreWeek2) * 100)
    
    return change

# Function to draw the line graph
def Student_DrawLineGraph(main, data, type):
    fig = Figure()
    fig.autofmt_xdate()    
    ax = fig.add_subplot(111)
    df = pd.DataFrame()
    
    timestamps = [row[1] for row in data]
    
    # X and y values for the graph
    x = [datetime.fromtimestamp(d) for d in timestamps]
    y = [row[0] for row in data]
    
    # Default values for the start and end date 
    startDate = datetime.fromtimestamp(numpy.min(timestamps))
    endDate = datetime.now()
    
    meanGrouping = '1W'
    
    if type == 0: # Selected option: Overall
        difference = datetime.timestamp(endDate) - datetime.timestamp(startDate)
        
        if difference < 7 * 3600 * 24:
           meanGrouping = '1D'
        elif difference < 28 * 3600 * 24:
           meanGrouping = '1W'
        else:
           meanGrouping = '1M'
           
    elif type == 1: # Selected option: Last 7 Days
        startDate = endDate - relativedelta(days = 7)
        meanGrouping = '1D'
        
    elif type == 2: # Selected option: Last 3 Weeks
        startDate = endDate - relativedelta(weeks = 3)
        meanGrouping = '1W'
        
    else: # Selected option: Last 3 Months
        startDate = endDate - relativedelta(months = 6)
        meanGrouping = '1M'
    
    x.append(endDate)
    y.append(y[len(y) - 1])
    
    # Creates the x and y axis
    df['Time'] = x
    df['Time'] = pd.to_datetime(df['Time'])
    df.index = df['Time'] 
    df['Score'] = y
    
    # (NOT USED) Averaging the data across the selected time range
    # df = df.resample(meanGrouping).mean()
    
    # Replaces missing values with the previous value to ensure the line graph is continuous
    for n in range(len(df['Score'])):
        if MathIsnan(df['Score'][n]) and n > 0:
            df['Score'][n] = df['Score'][n - 1]
    df.update(df)
    
    # Sets the range of values displayed along the x-axis
    ax.set_xlim(startDate, endDate)
    
    # Configures the size and layout of the graph
    df.plot(kind='line', x='Time', y='Score', ylim = (0, 105), ax = ax, figsize = (5, 4))
    x_axis = ax.axes.get_xaxis()
    x_label = x_axis.get_label()
    x_label.set_visible(False)
    plt.show()
    plt.close()
    
    # Creates the graph title
    fig.suptitle('Quiz Percentage')
    
    # Draws the line graph on the canvas
    canvas = FigureCanvasTkAgg(fig, master = main)
    canvas.draw()
    canvas.get_tk_widget().grid(row = 0, column = 0)