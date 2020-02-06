from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, ScreenManagerException
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty
from kivy.graphics import Line, Color
from warrant import Cognito
import pymysql
from botocore.exceptions import ClientError
import boto3
import base64

# these IDs are needed as global variables in order to be passed for DB
dbreg = ''
dbplate=''
dbmiles=''
carchecks = []
dbnotes = ''
driversig = ''
dbusername = ''

class ScreenManagement(ScreenManager):
    pass

# this class uses

class SigninScreen(Screen, Widget):
    #this variable is the stop using boolean if creds are right will pass true and on to next page
    isAuthenticated = BooleanProperty(False)

    # this function updates the global 'username' to be used for the DB
    def sendglobal(self, username):
        global dbusername
        dbusername = self.ids.username.text

    # this function uses AWS cognito to authenticate the username and pin (can use aws secrets to retrieve the acces key etc)
    def validate_user(self, username, pin,):
        info = self.ids.info
        username = self.ids.username.text
        pin = self.ids.pin.text+self.ids.pin.text
        try:
            #### enter your AWS creds here
            u = Cognito('eu-west-1_#########', '#################', user_pool_region='eu-west-1', username=username, access_key='#############',
                    secret_key='##########################################')
            u.authenticate(password=pin)
            self.isAuthenticated = True
        except:
            info.text = '[color=#FF0000]Invalid Username and/or Password[/color]'


class Tickscreen(Screen):

    # this function saves the instances which have been checked and sends them to a global variable
    def checkbox_confirm(self, instance):
        #self.checks = [print("good" for instance in self.ids.values() if instance.active]
        for instance in self.ids.values():
            global carchecks
            global idname
            idname = (list(self.ids.keys())[list(self.ids.values()).index(instance)])
            if instance.active:
                carchecks += [[idname, 'Yes']]
            else:
                carchecks += [[idname, 'No']]
    pass

class Carreg(Screen, Widget):
    # this functions saves the reg miles and plate variable sends to global variable
    def sendglobal2(self,reg,plate,miles):
        global dbreg
        global dbmiles
        global dbplate
        dbmiles = self.ids.miles.text
        dbplate = self.ids.plate.text
        dbreg = self.ids.reg.text

class Additional(Screen, Widget):
    def appendnotes(self):
        global dbnotes
        dbnotes = self.ids.notes.text

    pass

# this object just holds the functions that 'sign on the screen'
class Signer(Widget):
    def on_touch_down(self, touch):
        with self.canvas:
            Color(.1, .1, .1)
            touch.ud["line"] = Line(points=(touch.x, touch.y),width=2)

    def on_touch_move(self, touch):
        touch.ud["line"].points += [touch.x, touch.y]

# this is the screen that opens a db connection using hidden creds retrieved from AWS secrets and writes all the global variables in to the db including the signature.
class Sigscreen(Screen):
    def savevar(self):
        global driversig
        # test = open("B.png","r+b").read()
        # driversig += str(test)
        client = boto3.client('cognito-identity', region_name='eu-west-1')

        idenid = 'eu-west-1:####################################'
        responsetok = client.get_open_id_token(
            IdentityId=idenid
        )
        webtoken = responsetok['Token']

        client = boto3.client('sts')
        responseRole = client.assume_role_with_web_identity(
            RoleArn='arn:aws:iam::#########098:role/Cognito_an#####appUnauth_Role',
            RoleSessionName='myapp',
            WebIdentityToken=webtoken,
        )

        creds_dic = responseRole['Credentials']
        awsaccesskey = creds_dic['AccessKeyId']
        awsseckey = creds_dic['SecretAccessKey']
        token = creds_dic['SessionToken']

        def get_secret():

            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                region_name='eu-west-1',
                aws_access_key_id=awsaccesskey,
                aws_secret_access_key=awsseckey,
                aws_session_token=token

            )
            secret_name = "RDS_secet"
            response = client.get_secret_value(
                SecretId=secret_name
            )

            try:
                get_secret_value_response = client.get_secret_value(
                    SecretId=secret_name
                )
            except ClientError as e:
                if e.response['Error']['Code'] == 'DecryptionFailureException':
                    raise e
                elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                    raise e
                elif e.response['Error']['Code'] == 'InvalidParameterException':
                    raise e
                elif e.response['Error']['Code'] == 'InvalidRequestException':
                    raise e
                elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                    raise e
            else:
                if 'SecretString' in get_secret_value_response:
                    secrets = get_secret_value_response['SecretString']

                else:
                    decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])

            get_secret.usr = secrets[13:18]
            get_secret.pssw = secrets[32:41]

        get_secret()

        usr = get_secret.usr
        pssw = get_secret.pssw
        conn = pymysql.connect(host='driver######db.#############t.eu-west-1.rds.amazonaws.com',
                               port=3306,
                               user=usr,
                               passwd=pssw,
                               db='Driverchecks')
        cur = conn.cursor()
        cur.execute('''INSERT INTO DriverCarCheck(driver, reg, plate, mileage, carchecks,notes)
         VALUES(%s, %s, %s, %s, %s, %s)''', (dbusername,dbreg,dbplate,dbmiles,str(carchecks),dbnotes))
        conn.commit()
        cur.close()
        pass


# this is the final screen showing process completition
class Final(Screen):
    pass

kivyfiles = Builder.load_file("main.kv")

class SigninApp(App):
    def build(self):
        return kivyfiles

sApp = SigninApp()
sApp.run()