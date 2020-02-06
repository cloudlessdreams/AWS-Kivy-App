import boto3
import base64
import pymysql
from botocore.exceptions import ClientError

# this gets the id token required
client = boto3.client('cognito-identity', region_name= 'ENTER REGION')
responsetoken = client.get_open_id_token(
    IdentityId='ENTER IDENTITY ID FOUND ON COGNITO'
)
# save the token as a variable to use later
webtoken = responsetoken['Token']


client = boto3.client('sts')
responseRole = client.assume_role_with_web_identity(
        ## make sure this ARN has the neccessary permissions

    RoleArn='USE THE ARN WITH RIGHT PERMISSIONS',
    RoleSessionName='myapp',
    WebIdentityToken=webtoken,
)

# these variables save the repsonses required to fetch the AWS secret
credsFullDict = responseRole['Credentials']
awsaccesskey = credsFullDict['AccessKeyId']
awsseckey = credsFullDict['SecretAccessKey']
token = credsFullDict['SessionToken']


#this is the AWS secret function
def get_secret():

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name='eu-west-1',
        aws_access_key_id=awsaccesskey,
        aws_secret_access_key=awsseckey,
        aws_session_token=token

    )
    # this is the name of the secret saved on aws
    secret_name = "RDS_secet"
    response = client.get_secret_value(
        SecretId=secret_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )

    ## these are all the exceptions
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
        ## this saves the response in to secrets
        if 'SecretString' in get_secret_value_response:
            secrets = get_secret_value_response['SecretString']

        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])

    get_secret.usr = secrets[13:18]
    get_secret.pssw = secrets[32:41]

get_secret()


### the secret is tested on a simple SQL db query
usr = get_secret.usr
pssw = get_secret.pssw


conn = pymysql.connect(host='HOST OF DB',
                       port=3306,
                       user=usr,
                       passwd=pssw,
                       db='NAME OF DATABASE')

cursor = conn.cursor()
cursor.execute('THESE ARE THE DB INSTRUCTIONS')
for row in cursor:
    print(row)

cursor.close()
