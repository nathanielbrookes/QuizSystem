from Global import *

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

# Set default password for admin account: "adminPass"

database.cursor.execute('DELETE FROM Users WHERE TYPE = 2')

database.cursor.execute('SELECT * FROM Users WHERE TYPE = 2')
result = database.cursor.fetchone()
if result is None:
   database.cursor.execute('INSERT INTO Users (USERNAME, FNAME, LNAME, HASH, SALT, TYPE) VALUES ("Admin", "Admin", "Account", "8a5c1f0c5652f6c8db4fc3b6e94984edebbec5a66998dea8b775605fd066c11e", "9161518d1b3341d3850867f658d3bfd0", 2)') 
   database.conn.commit()

database.Close() # Close the database connection

# Import local files

from teacher import Teacher_DisplayQuestionBank, Teacher_DisplayClasses
from student import Student_DisplayClasses, Student_DisplayStatistics

main = Tk()
AccountType = IntVar(main)
main.resizable(0, 0)
main.configure(bg = fill)

# User registration

def LoginScreen():
    # Remove every widget from the window
    for widget in main.winfo_children():
        widget.destroy()
    
    form = Frame(main, bg = fill)
    form.pack()
    
    options = Frame(main, bg = fill)
    options.pack(fill = 'both', side = 'bottom', padx = 20, pady = 10)
    
    # Initialise the button to allow the user to navigate to the admin login screen
    adminText = Label(options, bg = fill, font = 'Arial 9 bold underline', cursor = 'hand2', text = 'Admin')
    adminText.pack(side = 'left')
    adminText.bind('<Enter>', lambda value: adminText.config(fg = '#888'))
    adminText.bind('<Leave>', lambda value: adminText.config(fg = '#000'))
    adminText.bind('<Button-1>', lambda value: AdminLoginScreen())
    
    # Initialise the button to allow the user to navigate to the registration screen
    signUpText = Label(options, bg = fill, font = 'Arial 9 bold underline', cursor = 'hand2', text = 'Create an Account')
    signUpText.pack(side = 'right')
    signUpText.bind('<Enter>', lambda value: signUpText.config(fg = '#888'))
    signUpText.bind('<Leave>', lambda value: signUpText.config(fg = '#000'))
    signUpText.bind('<Button-1>', lambda value: SignUpScreen())
    
    appTitle = Label(form, bg = fill, font = 'Arial 15 bold', text = AppName)
    appTitle.grid(pady = (30, 0))
    
    subtitle = Label(form, bg = fill, font = 'Arial 13', text = 'Log In')
    subtitle.grid()
    
    details = Frame(form, bg = fill)
    details.grid(pady = (20, 0))
    
    main.title('Log In - ' + AppName)
    main.geometry('350x300')
    
    loginForm = ValidationForm()
    
    # Displaying the input fields and setting validation rules
    usernameText = Label(details, bg = fill, font = 'Arial 10', text = 'Username:')
    usernameText.grid(row = 2, padx = (0, 5), sticky = 'w')
    
    usernameInput = Entry(details, bg = '#DDD', font = 'Arial 11')
    usernameInput.grid(row = 2, column = 1, padx = (5, 0))
    
    username = loginForm.NewInput(usernameInput, 'Entry')
    username.AddRule('.{1}', 'Username cannot be left empty')
    
    passwordText = Label(details, bg = fill, font = 'Arial 10', text = 'Password:')
    passwordText.grid(row = 3, padx = (0, 5), sticky = 'w')
    
    passwordInput = Entry(details, bg = '#DDD', font = 'Arial 11', show = '•')
    passwordInput.grid(row = 3, column = 1, padx = (5, 0))
    
    password = loginForm.NewInput(passwordInput, 'Entry')
    password.AddRule('.{1}', 'Password cannot be left empty')
    
    # Validation function called after user presses "Log In"
    def Validate(value):
        if value == True:
            # Remove errors - Form is validated (client-side only)
            error.configure(text = '')
            
            # Server-side validation
            database = NewConnection()
            database.cursor.execute('SELECT HASH, SALT, TYPE FROM Users WHERE USERNAME = ? AND TYPE != 2', [username.value])
            result = database.cursor.fetchone()
            database.Close()
            
            if result is None:
                error.configure(text = 'This username doesn\'t exist')
            elif sha256((password.value + result[1]).encode()).hexdigest() != result[0]:
                error.configure(text = 'Incorrect password')
            else:
                # Remove errors - Form is completely validated
                error.configure(text = '')
                
                # Open user's account
                StartLogin(int(result[2]), username.value)
        else:
            # Form is invalid - shown an error
            error.configure(text = value)
    
    # Creates the log in button
    loginBtn = Button(details, bg = '#DDD', text = 'Log In', command = lambda: loginForm.Validate(Validate))
    loginBtn.grid(pady = (10, 0), sticky = 'w')
    
    # Creates the error message text
    error = Label(form, bg = fill, fg = '#F00')
    error.grid(pady = (10, 0))

def AdminLoginScreen():
    # Remove every widget from the window
    for widget in main.winfo_children():
        widget.destroy()
    
    form = Frame(main, bg = fill)
    form.pack()
    
    options = Frame(main, bg = fill)
    options.pack(fill = 'both', side = 'bottom', padx = 20, pady = 10)
    
    # Initialise the button to allow the user to navigate to the login screen
    goBackText = Label(options, bg = fill, font = 'Arial 9 bold underline', cursor = 'hand2', text = 'Go Back')
    goBackText.pack(side = 'left')
    goBackText.bind('<Enter>', lambda value: goBackText.config(fg = '#888'))
    goBackText.bind('<Leave>', lambda value: goBackText.config(fg = '#000'))
    goBackText.bind('<Button-1>', lambda value: LoginScreen())
    
    appTitle = Label(form, bg = fill, font = 'Arial 15 bold', text = AppName)
    appTitle.grid(pady = (30, 0))
    
    subtitle = Label(form, bg = fill, font = 'Arial 13', text = 'Admin Log In')
    subtitle.grid()
    
    details = Frame(form, bg = fill)
    details.grid(pady = (20, 0))
    
    loginForm = ValidationForm()
    
    main.title('Admin Log In - ' + AppName)
    main.geometry('350x300')
    
    # Displaying the input fields and setting validation rules
    usernameText = Label(details, bg = fill, font = 'Arial 10', text = 'Username:')
    usernameText.grid(row = 2, padx = (0, 5), sticky = 'w')
    
    usernameInput = Entry(details, bg = '#DDD', font = 'Arial 11')
    usernameInput.grid(row = 2, column = 1, padx = (5, 0))
    
    username = loginForm.NewInput(usernameInput, 'Entry')
    username.AddRule('.{1}', 'Username cannot be left empty')
    
    passwordText = Label(details, bg = fill, font = 'Arial 10', text = 'Password:')
    passwordText.grid(row = 3, padx = (0, 5), sticky = 'w')
    
    passwordInput = Entry(details, bg = '#DDD', font = 'Arial 11', show = '•')
    passwordInput.grid(row = 3, column = 1, padx = (5, 0))
    
    password = loginForm.NewInput(passwordInput, 'Entry')
    password.AddRule('.{1}', 'Password cannot be left empty')
    
    # Validation function called after user presses "Log In"
    def Validate(value):
        if value == True:
            # Remove errors - Form is validated (client-side only)
            error.configure(text = '')
            
            # Server-side validation
            database = NewConnection()
            database.cursor.execute('SELECT HASH, SALT FROM Users WHERE USERNAME = ? AND TYPE = 2', [username.value])
            result = database.cursor.fetchone()
            database.Close()
            
            if result is None:
                error.configure(text = 'This username doesn\'t exist')
            elif not sha256((password.value + result[1]).encode()).hexdigest() == result[0]:
                error.configure(text = 'Incorrect password')
            else:
                # Remove errors - Form is completely validated
                error.configure(text = '')
                
                # Open user's account
                StartLogin(2, username.value)
        else:
            # Form is invalid - shown an error
            error.configure(text = value)
    
    # Creates the submit button
    submitBtn = Button(details, bg = '#DDD', text = 'Log In', command = lambda: loginForm.Validate(Validate))
    submitBtn.grid(pady = (10, 0), sticky = 'w')
    
    # Creates the error message text
    error = Label(form, bg = fill, fg = '#F00')
    error.grid(pady = (10, 0))
    
def SignUpScreen():
    # Remove every widget from the window
    for widget in main.winfo_children():
        widget.destroy()
    
    form = Frame(main, bg = fill)
    form.pack()
    
    options = Frame(main, bg = fill)
    options.pack(fill = 'both', side = 'bottom', padx = 20, pady = 10)
    
    # Initialise the button to allow the user to navigate to the admin login screen
    adminText = Label(options, bg = fill, font = 'Arial 9 bold underline', cursor = 'hand2', text = 'Admin')
    adminText.pack(side = 'left')
    adminText.bind('<Enter>', lambda value: adminText.config(fg = '#888'))
    adminText.bind('<Leave>', lambda value: adminText.config(fg = '#000'))
    adminText.bind('<Button-1>', lambda value: AdminLoginScreen())
    
    # Initialise the button to allow the user to navigate to the login screen
    loginText = Label(options, bg = fill, font = 'Arial 9 bold underline', cursor = 'hand2', text = 'Log In')
    loginText.pack(side = 'right')
    loginText.bind('<Enter>', lambda value: loginText.config(fg = '#888'))
    loginText.bind('<Leave>', lambda value: loginText.config(fg = '#000'))
    loginText.bind('<Button-1>', lambda value: LoginScreen())
    
    appTitle = Label(form, bg = fill, font = 'Arial 15 bold', text = AppName)
    appTitle.grid(pady = (30, 0))
    
    subtitle = Label(form, bg = fill, font = 'Arial 13', text = 'Sign Up')
    subtitle.grid()
    
    details = Frame(form, bg = fill)
    details.grid(pady = (20, 0))
       
    main.title('Sign Up - ' + AppName)
    main.geometry('350x390')
    
    signUpForm = ValidationForm()
    
    # Displaying the input fields and setting validation rules
    fnameText = Label(details, bg = fill, font = 'Arial 10', text = 'First Name:')
    fnameText.grid(row = 2, padx = (0, 5), sticky = 'w')
    
    fnameInput = Entry(details, bg = '#DDD', font = 'Arial 11')
    fnameInput.grid(row = 2, column = 1, padx = (5, 0))
    
    fname = signUpForm.NewInput(fnameInput, 'Entry')
    fname.AddRule('.{1}', 'First Name cannot be left empty')
    fname.AddRule('^.{,30}$', 'First Name cannot exceed 30 characters')
    
    lnameText = Label(details, bg = fill, font = 'Arial 10', text = 'Last Name:')
    lnameText.grid(row = 3, padx = (0, 5), sticky = 'w')
    
    lnameInput = Entry(details, bg = '#DDD', font = 'Arial 11')
    lnameInput.grid(row = 3, column = 1, padx = (5, 0))
    
    lname = signUpForm.NewInput(lnameInput, 'Entry')
    lname.AddRule('.{1}', 'Last Name cannot be left empty')
    lname.AddRule('^.{,30}$', 'Last Name cannot exceed 30 characters')
    
    usernameText = Label(details, bg = fill, font = 'Arial 10', text = 'Username:')
    usernameText.grid(row = 4, padx = (0, 5), pady = (10, 0), sticky = 'w')
    
    usernameInput = Entry(details, bg = '#DDD', font = 'Arial 11')
    usernameInput.grid(row = 4, column = 1, padx = (5, 0), pady = (10, 0))
    
    username = signUpForm.NewInput(usernameInput, 'Entry')
    username.AddRule('.{1}', 'Username cannot be left empty')
    username.AddRule('^.{,20}$', 'Last Name cannot exceed 20 characters')
    username.AddRule('^[A-Za-z0-9]+$', 'Username can only contains letters and/or numbers')
    
    passwordText = Label(details, bg = fill, font = 'Arial 10', text = 'Password:')
    passwordText.grid(row = 5, padx = (0, 5), sticky = 'w')
    
    passwordInput = Entry(details, bg = '#DDD', font = 'Arial 11', show = '•')
    passwordInput.grid(row = 5, column = 1, padx = (5, 0))
    
    password = signUpForm.NewInput(passwordInput, 'Entry')
    password.AddRule('.{1}', 'Username cannot be left empty')
    
    # Initialise the value for the radio button
    AccountType.set(0)
    
    accountTypeText = Label(details, bg = fill, font = 'Arial 10', text = 'Account Type:')
    accountTypeText.grid(sticky = 'w', pady = (10, 0))
    
    studentRadio = Radiobutton(details, bg = fill, text = 'Student', value = 0, variable = AccountType)
    studentRadio.grid(column = 1)
    
    teacherRadio = Radiobutton(details, bg = fill, text = 'Teacher', value = 1, variable = AccountType)
    teacherRadio.grid(column = 1)
    
    # Validation function called after user presses "Submit"
    def Validate(value):
        if value == True:
            # Remove errors - Form is validated (client-side only)
            error.configure(text = '')
            
            # Server-side validation
            database = NewConnection()
            database.cursor.execute('SELECT USERNAME FROM Users WHERE USERNAME = ?', [username.value])
            result = database.cursor.fetchone()
            database.Close()
            
            if result is not None:
                error.configure(text = 'This username already exists')
            else:
                # Remove errors - Form is completely validated
                error.configure(text = '')
                
                # Generates a unique salt value
                salt = GenerateCode('Users', 'SALT', 32)
                
                # Generates the password hash
                hash = sha256((password.value + salt).encode()).hexdigest()
                
                # Creates new record in Users table
                InsertData('Users', ['USERNAME', 'FNAME', 'LNAME', 'HASH', 'SALT', 'TYPE'], [username.value, fname.value, lname.value, hash, salt, AccountType.get()])
                
                # Open user's account 
                StartLogin(int(AccountType.get()), username.value)
        else:
            # Form is invalid - shown an error
            error.configure(text = value)
    
    # Creates the submit button
    submitBtn = Button(details, bg = '#DDD', text = 'Submit', command = lambda: signUpForm.Validate(Validate))
    submitBtn.grid(pady = (10, 0), sticky = 'w')
    
    # Creates the error message text
    error = Label(form, bg = fill, fg = '#F00')
    error.grid(pady = (10, 0))

# Account management

def ChangePassword(pageDetails):
    titleContentFrame = pageDetails[0]
    mainContentFrame = pageDetails[1]
    username = pageDetails[2]
    accountType = pageDetails[3]
    
    dialog = Dialog('Change your password', '300x200') # Creates a new window

    dialogFrame = Frame(dialog, bg = fill)
    dialogFrame.grid(sticky = 'nesw', padx = 10, pady = 10)

    passwordForm = ValidationForm()

    dialogFrame.grid_columnconfigure(0, weight = 1)
   
    # Creates the main title text         
    mainTitle = Label(dialogFrame, bg = fill, font = 'Arial 11 bold', text = 'Change your password')
    mainTitle.grid(sticky = 'ew')
    
    details = Frame(dialogFrame, bg = fill)
    details.grid(row = 1, pady = (20, 0))
     
    # Creates the current password text           
    currentPasswordText = Label(details, bg = fill, font = 'Arial 10', text = 'Current Password:')
    currentPasswordText.grid(row = 0, padx = (0, 5), sticky = 'w')
    
    # Creates the current password input
    currentPasswordInput = Entry(details, bg = '#DDD', font = 'Arial 11', show = '•')
    currentPasswordInput.grid(row = 0, column = 1, padx = (5, 0))
    
    # Adds validation rules to the current password
    currentPassword = passwordForm.NewInput(currentPasswordInput, 'Entry')
    currentPassword.AddRule('.{1}', 'Current Password cannot be left empty')

    # Creates the new password text
    newPasswordText = Label(details, bg = fill, font = 'Arial 10', text = 'New Password:')
    newPasswordText.grid(row = 1, padx = (0, 5), sticky = 'w')
    
    # Creates the new password input
    newPasswordInput = Entry(details, bg = '#DDD', font = 'Arial 11', show = '•')
    newPasswordInput.grid(row = 1, column = 1, padx = (5, 0))
    
    # Adds validation rules to the new password
    newPassword = passwordForm.NewInput(newPasswordInput, 'Entry')
    newPassword.AddRule('.{1}', 'New Password cannot be left empty')

    # Validation function called after user presses "Submit"
    def Validate(value):
        if value == True:
            if currentPassword.value == newPassword.value:
                # Form is invalid - shown an error
                error.configure(text = 'New password must be different from current')
            else:
                # Remove errors - Form is validated (client-side only)
                error.configure(text = '')
                
                # Server-side validation
                database = NewConnection()
                database.cursor.execute('SELECT HASH, SALT FROM Users WHERE USERNAME = ?', [username])
                result = database.cursor.fetchone()
                database.Close()

                password = result[0]
                salt = result[1]

                compare = sha256((currentPassword.value + salt).encode()).hexdigest()

                if not compare == password: # Does the current password hash match the actual password hash
                    # Form is invalid - shown an error
                    error.configure(text = 'Incorrect password')
                else:
                    hashedPassword = sha256((newPassword.value + salt).encode()).hexdigest()
                    
                    # Update the password hash for the record in the Users table
                    database = NewConnection()
                    database.cursor.execute('UPDATE Users SET HASH = ? WHERE USERNAME = ?', [hashedPassword, username])
                    database.conn.commit()
                    database.Close()
            
                    # Closes the current window
                    dialog.destroy()
        else:
            # Form is invalid - shown an error
            error.configure(text = value)

    # Creates the submit button
    submitBtn = Button(dialogFrame, bg = '#DDD', text = 'Submit', command = lambda: passwordForm.Validate(Validate))
    submitBtn.grid(pady = (25, 0))
    
    # Creates the error message text
    error = Label(dialogFrame, bg = fill, fg = '#F00')
    error.grid(pady = (10, 0))
    
def DeleteAccount():
    # Displays warning message
    confirm = messagebox.askquestion(title = 'Delete your account', message = 'This action cannot be undone. Are you sure you want to delete your account?')
    if confirm == 'yes':
        # Deletes the record from the Users table
        database = NewConnection()
        database.cursor.execute('DELETE FROM Users WHERE USERNAME = ?', [username])
        database.conn.commit()
        database.Close()
        
        # Logs out the user
        LoginScreen()

def DisplayAccountDetails(pageDetails):
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
    selectedTitle = Label(titleContentFrame, bg = fill, text = 'Account Details', font = 'Arial 13 bold', anchor = 'w')
    selectedTitle.grid(sticky = 'nw')
    
    # Finds the full name of the user
    database = NewConnection()
    database.cursor.execute('SELECT FNAME, LNAME FROM Users WHERE USERNAME = ?', [username])
    name = ' '.join(database.cursor.fetchone())
    database.Close()

    # Creates the name title text
    nameLabel = Label(mainContentFrame, bg = fill, text = 'Name:')
    nameLabel.grid(row = 1, column = 0, sticky = 'w', pady = (20, 0))
    
    # Creates the name value text
    nameValue = Label(mainContentFrame, bg = fill, text = name)
    nameValue.grid(row = 1, column = 1, sticky = 'w', pady = (20, 0))
    
    # Creates the username title text
    usernameLabel = Label(mainContentFrame, bg = fill, text = 'Username:')
    usernameLabel.grid(row = 2, column = 0, sticky = 'w')
    
    # Creates the username value text
    usernameValue = Label(mainContentFrame, bg = fill, text = username)
    usernameValue.grid(row = 2, column = 1, sticky = 'w')
    
    if accountType == 0:
        accountTypeText = 'Student'
    elif accountType == 1:
        accountTypeText = 'Teacher'
    else:
        accountTypeText = 'Admin'
    
    # Creates the account type title text
    typeLabel = Label(mainContentFrame, bg = fill, text = 'Account Type:')
    typeLabel.grid(row = 3, column = 0, sticky = 'w')
    
    # Creates the account type value text
    typeValue = Label(mainContentFrame, bg = fill, text = accountTypeText)
    typeValue.grid(row = 3, column = 1, sticky = 'w')
    
    # Creates the password title text
    passLabel = Label(mainContentFrame, bg = fill, text = 'Password:')
    passLabel.grid(row = 4, column = 0, sticky = 'w')
    
    # Creates the change password button
    passBtn = Button(mainContentFrame, bg = '#DDD', text = 'Change Password', command = lambda: ChangePassword(pageDetails))
    passBtn.grid(row = 4, column = 1, sticky = 'w')

    if not accountType == 2:
        # Creates the delete account button
        deleteLabel = Label(mainContentFrame, bg = fill, fg = '#F00', text = 'Delete Account', font = 'Arial 9 bold underline', cursor = 'hand2')
        deleteLabel.grid(row = 5, column = 0, sticky = 'w', pady = (100, 0))
        
        deleteLabel.bind('<Enter>', lambda value: deleteLabel.config(fg = '#888'))
        deleteLabel.bind('<Leave>', lambda value: deleteLabel.config(fg = '#F00'))
        deleteLabel.bind('<Button-1>', lambda value: DeleteAccount())

# Main app

def StartLogin(accountType, accountUsername):
    username = accountUsername
    
    # Remove every widget from the window
    for widget in main.winfo_children():
        widget.destroy()
    
    # Resizes the screen
    main.geometry('800x450')
    
    # Frame layout
    main.rowconfigure(0, weight = 1)
    main.columnconfigure(2, weight = 1)
    
    optionsFrame = Frame(main, bg = fill, width = 150)
    optionsFrame.grid(row = 0, column = 0, sticky = 'nesw')
    optionsFrame.grid_propagate(False)
    
    optionsFrame.rowconfigure(0, weight = 1)
    
    topOptionsFrame = Frame(optionsFrame, bg = fill)
    topOptionsFrame.grid(row = 0, column = 0, sticky = 'nesw', padx = 20, pady = (40, 0))
    
    bottomOptionsFrame = Frame(optionsFrame, bg = fill)
    bottomOptionsFrame.grid(row = 1, column = 0, sticky = 'nesw', padx = 20, pady = 10)
    
    borderFrame = Frame(main, bg = '#000')
    borderFrame.grid(row = 0, column = 1, sticky = 'nsw', ipadx = 1)
    
    contentFrame = Frame(main, bg = fill)
    contentFrame.grid(row = 0, column = 2, sticky = 'nesw')
    
    contentFrame.rowconfigure(1, weight = 1)
    contentFrame.columnconfigure(0, weight = 1)
    
    titleContentFrame = Frame(contentFrame, bg = fill)
    titleContentFrame.grid(row = 0, column = 0, sticky = 'nesw', padx = 25, pady = (40, 15))
    
    titleContentFrame.columnconfigure(0, weight = 1)
    
    mainContentFrame = Frame(contentFrame, bg = fill)
    mainContentFrame.grid(row = 1, column = 0, sticky = 'nesw', padx = 25)
    
    accountDetailsOption = SideOption(bottomOptionsFrame, 'Account Details', lambda: SelectOption(0))
    classesOption = SideOption(topOptionsFrame, 'Classes', lambda: SelectOption(1))
    questionBankOption = SideOption(topOptionsFrame, 'Question Bank', lambda: SelectOption(2))
    statisticsOption = SideOption(topOptionsFrame, 'Statistics', lambda: SelectOption(2))
    usersOption = SideOption(topOptionsFrame, 'Users', lambda: SelectOption(3))
    SideOption(bottomOptionsFrame, 'Log Out', LoginScreen)

    def SelectOption(selectedOption):
        for widget in titleContentFrame.winfo_children():
            widget.destroy()
            
        for widget in mainContentFrame.winfo_children():
            widget.destroy()
        
        accountDetailsOption.Update(False)
        if accountType == 0:
            classesOption.Update(False)
            statisticsOption.Update(False)
            questionBankOption.btn.destroy()
            usersOption.btn.destroy()
        elif accountType == 1:
            classesOption.Update(False)
            questionBankOption.Update(False)
            statisticsOption.btn.destroy()
            usersOption.btn.destroy()
        else:
            usersOption.Update(False)
            classesOption.btn.destroy()
            statisticsOption.btn.destroy()
            questionBankOption.btn.destroy()
        
        pageDetails = [titleContentFrame, mainContentFrame, username, accountType]
        
        if selectedOption == 0: # Selected option: Account Details
            accountDetailsOption.Update(True)

            DisplayAccountDetails(pageDetails)
            
        if accountType == 0:
            if selectedOption == 1: # Selected option: Classes
                classesOption.Update(True)
                
                Student_DisplayClasses(pageDetails)
                
            elif selectedOption == 2: # Selected option: Statistics
                statisticsOption.Update(True)

                Student_DisplayStatistics(pageDetails)
                    
        elif accountType == 1:
            if selectedOption == 1: # Selected option: Classes
                classesOption.Update(True)
                
                Teacher_DisplayClasses(pageDetails)
                    
            elif selectedOption == 2: # Selected option: Question Bank
                questionBankOption.Update(True)
    
                Teacher_DisplayQuestionBank(pageDetails)
                    
        elif selectedOption == 3:
            def DeleteUser(name, username):
                confirm = messagebox.askquestion(title = 'Delete user: "' + name + '"', message = 'This action cannot be undone. Are you sure you want to delete this account?')
                if confirm == 'yes':
                    database = NewConnection()
                    database.cursor.execute('DELETE FROM Users WHERE USERNAME = ?', [username])
                    database.conn.commit()
                    database.Close()
                    SelectOption(selectedOption)
            
            usersOption.Update(True)
            
            selectedTitle = Label(titleContentFrame, bg = fill, font = 'Arial 13 bold', anchor = 'w', text = 'Users')
            selectedTitle.grid(sticky = 'w')
            
            users = Table(mainContentFrame, 326)
            users.NewHeaderValue('Name', 295)
            users.NewHeaderValue('Username', 100)
            users.NewHeaderValue('Account Type', 100)
            users.NewHeaderValue('', 60)
            
            database = NewConnection()
            database.cursor.execute('SELECT FNAME, LNAME, USERNAME, TYPE FROM Users WHERE TYPE != 2')
            result = database.cursor.fetchall()
            database.Close()
            
            for i in result:
                row = NewRow(users)
                
                name = i[0] + ' ' + i[1]
                
                row.NewLabel(name)
                row.NewLabel(i[2])
                
                accountTypeText = 'Student'
                if i[3] == 1:
                    accountTypeText = 'Teacher'
                
                row.NewLabel(accountTypeText)
                row.NewBtn('Delete', lambda name = name, i = i: DeleteUser(name, i[2]))
                
    SelectOption(0)

LoginScreen()

main.mainloop()