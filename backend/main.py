from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pyodbc
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
image_path = './image/'


#               CONNECTION TO DATABASE
def database_connection(server:str='localhost', database:str='Caucheez', username:str='sa', password:str='12345@bcdE'):
    '''
    call this function to connect to database
    this function return pyodbc.connect 
    '''
    return pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};\
                            SERVER='+server+';\
                            DATABASE='+database+';\
                            UID='+username+';PWD='+password+';')

# def database_connection2(server:str='TRONGNHAN', database:str='Plooker'):
#     '''
#     call this function to connect to database
#     this function return pyodbc.connect 
#     '''
#     return pyodbc.connect('DRIVER={SQL Server};\
#                             SERVER='+server+';\
#                             DATABASE='+database+';\
#                             UID='+username+';PWD='+password+';')

def database_connection2(server:str='localhost', database:str='Caucheez'):
    '''
    call this function to connect to database
    this function return pyodbc.connect
    '''
    return pyodbc.connect('DRIVER={SQL Server};\
                            SERVER='+server+';\
                            DATABASE='+database+';\
                            Trusted_Connection=yes;')

'''
class <classname>(BaseModel):
    <variable>: <type> = <value>
'''
#               STRUCTURE DEFINE
class LoginInfo(BaseModel):
    userID: str = '123456'
    username: str = 'ltnhan'
    password: str = 'Nhan123@'
    created_at: str = '1-1-2000'


#               DATABASE COMMAND
class Database:
    def __init__(self):
        self.conn = database_connection2()
        self.cursor = self.conn.cursor()
        pass

    #get data from db
    def getMentorInfo(self, data: MentorInfo) -> list:
        if data.gender:
            gender = 1
        else:
            gender = 0
        command = "EXEC GetMentorInfo '%s', '%s', %f, %f, '%s', '%s', %d" % (data.animalType, data.detailtype, data.weight, data.height, data.color, data.location, gender)
        try:
            self.cursor.execute(command)
        except:
            return 'SOME ERROR OCCUR'
        result = []
        for i in self.cursor:
            result.append([x for x in i])
        return result

    def root(self, data:str) -> list:
        command = 'EXEC findTable \'' + data.lower() + '\''
        self.cursor.execute(command)
        result = []
        for i in self.cursor:
            result.append([x for x in i])
        return result

    def removeUser(self, userid:str):
        command = 'EXEC removeUser \'%s\'' % (userid)
        self.cursor.execute(command)
        self.conn.commit()

    def changeUserInfo(self, user: UserInfo):
        command = "EXEC changeUserInfo '%s', '%s', '%s', '%s', '%s', '%s', %d, '%s', '%s'" % (user.userid, user.Name, user.usename, user.userPhone, user.userMail, user.userPWD, 1 if user.gender else 0, user.dob, user.userAddress)
        try:
            self.cursor.execute(command)
            self.conn.commit()
        except:
            return 'FAIL'
        return 'SUCCESS'

    #sign up
    def signup(self, user: LoginInfo) -> str:
        id = user.userID
        command = 'EXEC sp_AddUsers \''+id+'\', \''+user.Name+'\', \''+user.usename+'\',\''+user.userPhone+'\', \''+user.userMail+'\', \''+user.userPWD+'\','+str(user.gender)+', \''+user.dob+'\', \''+user.userAddress+'\''
        try:
            self.cursor.execute(command)
            self.conn.commit()
        except:
            return 'FAIL TO SIGN UP'
        return 'SUCCESS'

    def login(self, username:str, password:str) -> str:
        '''return username'''
        command = 'EXEC CheckLogIn \''+username+'\', \''+password+'\''
        try:
            result = ''
            self.cursor.execute(command)
            print("hello")
            for i in self.cursor:
                result += i[0]
        except:
            return 'SOME ERRORS OCCUR'
        
        if result != 'None':
            return result
        else: return 'FAIL'

    def all(self):
        command = 'EXEC SearchAll'
        try:
            self.cursor.execute(command)
            result = []
            for i in self.cursor:
                result.append([e for e in i])
            return result
        except:
            return 'FAIL'

    def getUserInfo(self, id:dict):
        id = id['id']
        command = "EXEC getUserInfo '"+id+"'"
        try:
            self.cursor.execute(command)
            result = 0
            for i in self.cursor:
                result = [e for e in i]
            return result
        except:
            return 'NO USER'
###################################################################################################################
#           MAIN PART   
###################################################################################################################
app = FastAPI()
database = Database()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#sign up
@app.get('/')
async def check():
    return ['this note tell you that you successfully connect to the api']

@app.post('/sign_up', tags=['account'])
async def sign_up(account:UserInfo) -> str:
    '''
    RETURN 'SUCCESS' IF SUCCESSFULLY SIGN UP USER
    IF ERROR OCCUR THEN RETURN 'FAIL TO SIGN UP'

    example input:
    {
    "userid": "string",
    "Name": "Name",
    "usename": "testUser",
    "userPhone": "0912345678",
    "userMail": "gmail@gmail.com",
    "userPWD": "123",
    "gender": 0,
    "dob": "1-1-2000",
    "userAddress": "HCMC"
    }
    '''
    return database.signup(account)
    
#login
@app.post('/login', tags=['account'])
async def login(userinput:dict) -> str:
    username = userinput['user_name']
    password = userinput['password']
    return database.login(username,password)