import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')
s3 = boto3.resource('s3')
#On se connecte au serveur S3

'''for bucket in s3.buckets.all():
        print(bucket.name);

my_session = boto3.session.Session()
my_region = my_session.region_name
print(my_session)'''
#chgt de région pour le bucket
#pb avec la région passage en eu-central cf le fichier texte
#s3.meta.client.upload_file('/Users/jerel/Documents/Cours/2A/Projets/saintgobain/IoT_Mines/sensors/hello.txt', 'sensortag', 'hello.txt')
try :
    with open('hello.txt', 'w') as doc:
        doc.write('Hello, world !')

finally:
    doc.close()
# Upload the file to S3
s3_client.upload_file('hello.txt', 'sensortag','hello.txt')
'''
s3.Object('sensortag', 'hello.txt').put(Body=open('/Users/jerel/Documents/Cours/2A/Projets/saintgobain/IoT_Mines/sensors/hello.txt', 'rb'))
'''
