# 24/02/2022
* openpose
* recopilar fotos de instagram, por ejemplo camino de santiago, y buscar en la red para identificar personas, edad, genero, identificar emociones

APIs de visualización básica de Instagram:
https://github.com/huaying/instagram-crawler	// informacion de perfil
https://github.com/mgleon08/instagram-crawler 	// imagenes webscrapping en base a criterios
https://medium.com/dataseries/easy-way-to-crawl-instagram-using-instalooter-20846d55cc64

Imágenes de valladolid
1. lista de referencia urls imagenes,
2. buscar gente

primera semana: buscar crawler, intentar imagenes con api cloud vision, rango de edad, concretar api y crawler

Objetivo: Tratar de recomendar sitios de valladolid de por edad en base a imagenes descargadas de instagram

Para las reuniones Jueves a las 18:30


# 08/03/2022
Uso de instalooter para descargar imagenes y metadatos con hashtag "valladolid":
```
pip install instaLooter
instalooter login
mkdir output
instalooter hashtag valladolid output -D
instalooter hashtag valladolid output
instalooter logout
```
En este caso usé mi cuenta personal de instagram para descargar imágenes, posiblemente tenga que crearme una nueva para este proyecto

https://github.com/WuJie1010/Facial-Expression-Recognition.Pytorch
https://github.com/serengil/tensorflow-101

api cloud vision -> para "ver" edificios, lugares de interes, emociones, textos, limite 20M al mes
https://www.youtube.com/watch?v=9n1wY7JoU6s

1. Crear cuenta de google con correo de la UVa
2. Registrarse en cloud.google.com, pide direccion de facturacion aunque no la va a usar ya que da 300$ gratis para las pruebas, yo he solicitado una tarjeta virtual para este paso.
3. Un vaz registrado (una odisea), vamos a la pantalla principal de My First Proyect
4. En "IAM y administracion/Cuentas de Servicio" creamos cuenta de servicio con nombre "micuentadeservicio" y rol Propietario.
5. Vamos a la cuenta en la sección "Claves" y agregamos una nueva con Tipo "JSON" y guardamos la clave (sino no se puede recuperar)

Creamos un bucket en google cloud con el id del proyecto "indigo-pod-344620" en la seccion de Cloud Storage, y subimos la imágen happy.jpg, de un señor sonriendo descargada de google.

Usamos como cliente la api de python https://googleapis.dev/python/vision/latest/index.html
En linux descargamos el instalamos el cliente con:
```
pip install virtualenv
mkdir testvisual
virtualenv testvisual
source testvisual/bin/activate
./testvisual/bin/pip install google-cloud-vision
```

Copiamos el json con las credenciales de acceso en la carpeta testvisual y ponemos la variable de entorno GOOGLE_APPLICATION_CREDENTIALS apuntando a este fichero con
```
export GOOGLE_APPLICATION_CREDENTIALS="indigo-pod-344620-5cee76b95a93.json"
```

Creamos un script de prueba en la carpeta testvisual llamado mitest.py con lo siguiente
```python
from google.cloud import vision

client = vision.ImageAnnotatorClient()
response = client.annotate_image({
  'image': {'source': {'image_uri': 'gs://indigo-pod-344620/happy.jpg'}},
  'features': [{'type_': vision.Feature.Type.FACE_DETECTION}]
})

print("response:")
print(response)
```

Ejecutamos el script desde ese directorio con "./bin/python mitest.py"
1. Este script falla con el siguiente error:
```
google.api_core.exceptions.PermissionDenied: 403 Cloud Vision API has not been used in project 736707955357 before or it is disabled. Enable it by visiting https://console.developers.google.com/apis/api/vision.googleapis.com/overview?project=736707955357 then retry. If you enabled this API recently, wait a few minutes for the action to propagate to our systems and retry. [links {
  description: "Google developers console API activation"
  url: "https://console.developers.google.com/apis/api/vision.googleapis.com/overview?project=736707955357"
}
```
Al entrar en la URL especificada permite habilitar cloudvision para el proyecto
2. Al ejecutar de nuevo el script sale el siguiente error porque el proyecto no tiene asociada una cuenta de pago:
```
google.api_core.exceptions.PermissionDenied: 403 This API method requires billing to be enabled. Please enable billing on project #736707955357 by visiting https://console.developers.google.com/billing/enable?project=736707955357 then retry. If you enabled billing for this project recently, wait a few minutes for the action to propagate to our systems and retry. [links {
  description: "Google developers console billing"
  url: "https://console.developers.google.com/billing/enable?project=736707955357"
}
```
Al entrar en la URL especificada permite habilitar la cuenta de pago
3. Después se ejcuta correctamente mostrando información del señor sonriente


# 24/03/2022
TODO:
buscar hashtags por etiquetas en insta
metodos para localizar hashtags en insta a partir de etiquetas.
buscar como subir al bucket de google.cloud
automatizar descarga y subida
filtrar genero edad pero habilitar, localizacion imágen de instagram
gestion de proyecto con github -> hacer repo
mirar github pro -> student
mirar tfm previos formato
MAP-review trabajos previos, criterios para seleccionar trabajos

* github pro hecho, y creado repo privado para el TFM

* Buscador de hashtags:
  * https://postcron.com/es/blog/landings/buscador-de-hashtags/#page-block-he6t7wyxoh
  * https://keywordtool.io/search/keywords/instagram/26108664?category&keyword=valladolid&country=GLB&language=en#hashtags
  Lo hace en base a las sugerencias de instagram

* Subir datos a google cloud:
  * Descargamos el cliente de gcloud para python
  ```
  source testvisualenv/bin/activate
  ./testvisualenv/bin/pip install google-cloud-storage
  export GOOGLE_APPLICATION_CREDENTIALS="../testvisualenv/indigo-pod-344620-5cee76b95a93.json"
  ```
  * Creamos un script para subir un fichero happy.jpg
  ```
  from google.cloud import storage

  source_file_name = "happy.jpg"
  destination_blob_name = source_file_name

  storage_client = storage.Client()
  bucket = storage_client.bucket("indigo-pod-344620")
  blob = bucket.blob(destination_blob_name)

  blob.upload_from_filename(source_file_name)

  print(
      "File {} uploaded to {}.".format(
          source_file_name, destination_blob_name
      )
  )
  ```
  * Ejecutamos el script desde ese directorio con "./bin/python mitest.py"

* Google Cloud CLI:
* Descargar cliente con:
```
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-379.0.0-linux-x86_64.tar.gz
```
* Descomprimir y ejecutar ./google-cloud-sdk/install.sh
* Hacer gcloud init y logearse

Notas: el cliente instalooter permite descargar imagenes nuevas comprobando las ya descargadas, para evitar que se repiten hay que descargar imagenes si o si. Se puede enviar la url a google vision api, pero teniendo en cuenta que ya las tenemos descargadas en local, y que posiblemente haya imágenes a las que google clooud no tenga acceso sin estar logeado, lo mejor es subirlas directamente a google cloud y procesarlas allí


# 04/04/2022
Reunión:
* Crear pool estatico de hashtags
* Añadir am-guerrero al repo
* Empezar mapreview


# 15/04/2022
Se ha añadido al repo la memoria y conectado con overleaf, también se ha añadido al tutor. Del documento "Systematic Mapping of Detection Techniques for Advanced Persistent Threats", David Sobrín-Hidalgo (Robotics Group, University of León) se ha concluido para el map-review que hay varias etapas:
* planificacion de busqueda -> comprobar que ya no hay trabajo previo que resuelva la misma pregunta, si no usar articulos del universo de estudio. Fuentes donde buscar, como: Web of Science, IEEE Digital Library, Scopus. Moreover,
* Proceso de busqueda -> generar unos strings de busqueda. palabras clave obtenidas mediante la estrategia PICOC. Una vez obtenidos los strings filtrar tambien por fechas (ej: 2015-2019) y que el acceso sea libre/gratuito
* Seleccion de muestras -> Proceso: 1. eliminar duplicados, 2. eliminar tras leer el abstract basandise en criterios de inclusion y de exclusion (si cumple algun criterio de exclusion o no cumple ningun criterio de inclusion descartar). 3. Leer por completo los articulos y decidir si son relevantes en base a un cuestionario (¿6? preguntas si -1 punto- o no -0 puntos- y sacar minimo un 4) para obtener proximadamente ¿10? muestras
* Extraccion de informacion: Definir que se quieres sacar de los articulos. ej: algoritmo usado, resultados obtenidos, dataset empleado, etc.


# 20/04/2022
Existe el problema de que instaLooter emplea el sistema de archivos para detectar si una imágen ya existe y por tanto, saber si una imágen es nueva o no. Esto es un problema ya que nos obliga a que el equipo que ejecute el script tenga que tener almacenadas todas las imágenes ya descargadas, lo que nos puede limitar ya que tenemos que tener almacenadas las imágenes por duplicado, tanto en este equipo como en Cloud Storage. Revisando el código fuente de instalooter parece que este permite que se le pase una instancia que herede de la interfaz fs.base.FS en vez de una ruta al sistema de archivos local, aunque esto no se encuentra documentado en su página web. Este objeto permite abstrarse del sistema de archivos local, y por ello, tal vez pueda ser ser reemplazado por un objeto que implemente las comunicaciones con Google Storage y así no tener que duplicar las imágenes. Gracias a GitHub he conseguido encontrar un proyecto [GCSFS](https://github.com/Othoz/gcsfs) que hace exactamente lo anterior y tras un pruebas he conseguido enviar una iágen de prueba al bucket de nuestro proyecto:
```
source testvisualenv/bin/activate
./testvisualenv/bin/pip install fs-gcsfs
cd scripts
export GOOGLE_APPLICATION_CREDENTIALS="../testvisualenv/indigo-pod-344620-5cee76b95a93.json"
../testvisualenv/bin/python3 gcsfstest.py
```

# 21/04/2022
* 4 pags de trabajos relacionados
* 2 programas:
  * Descargar imágen y sacar con cloud vision: sexo, edad, likelyhood de sentimiento. Lo guarda en una base de datos que mapea lugares y atributos edad, sexo, etc. Usar mariadb? Usar mongodb (se mete el json directamente sin procesar)?
  * introduciendo edad y sexo, el programa analizaria las imagenes con esas caracteristicas. Usar django para la interfaz?

# 23/04/2022
Tras probar la ejecución mediante scripts en mi PC, se decidió probar a emplear directamente a ejecutarlo en Google Cloud mediante una máquina virtual en su Compute Engine para no tener así que depender tanto de Google Cloud como de un PC Personal que se tuviese que estar ejecutando constantemente.

El primer paso para poder ejecutar scripts python en Google Cloud es ir a la ventana de Compute Engine de nuestro proyecto y habilitar el Compute Engine API. Despues desde Compute Engine > Instancias de VM hay que crear una nueva instancia de máquina virtual. En este caso como se trata tan solo de una prueba de concepto, los valores por defecto de 2 CPUs virtuales y 4GBs de RAM parecen suficientes. Las CPUs por defecto son de Segunda Generación "E2", que escogen el tipo de CPU automáticamente según la disponibilidad, en nuestro caso el tipo de CPU es irrelevante en esta fase del proyecto. Como almacenamiento por defecto se tienen 10 GBs que parecen suficientes para almacenar el SO y las librerías necesarias, que son junto con los sripts lo único que hay qeu almacenar en este disco ya que hay tener en cuenta que se va a emplear Google Storage para guardar las imágenes y las bases de datos que se necesiten. Por último también se dejó por defecto como sistema operativo Debian GNU/Linux 10 (buster) ya que personalmente ya tengo experiencia trabajando con este sistema operativo. El único valor que se modificó finalmente fue la región donde se ubica la máquina, que por defecto estaba localizada en us-west4 (Las Vegas), y en este caso es preferible que los servidores se encuentren en europa occidental, que es desde donde se va a acceder a estos servidores y que además se tienen que ajustar a la normativa europea, por ello este valor se cambió a europe-west1 (Bélgica).

Respecto a los permisos de esta nueva máquina virtual, se dió acceso de lectura y escrituralas APIs de Google Cloud Storage y al Compute Engine para poder acceder a nuestro bucket de almacenamiento.

Una vez creada la VM el siguiente paso es acceder a ella. Para ello se dispone de un cliente SSH Web, aunque también se puede emplear otros clientes SSH se se guarda clave pública del equipo en ~/.ssh/authorized_keys

"ssh daniel_gonzalez_alonso@35.233.99.128".

El siguiente paso es generar la contraseña del superusuario para poder instalar las librerías, para ello se ejecutó desde la consola web SSH
```
sudo passwd
```
Y se introdujo la nueva contraseña

DespEl siguiente paso es instalar el entorno de desarrollo, en nuestro caso hay que instalar python3 mediante:
```
sudo apt update
sudo apt install python3 python3-dev python3-venv
```
Y posteriormente hay que instalar pip para poder instalar las librerías necesarias:
```
sudo apt-get install wget
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
```
También mediante virtualenv se crea un entorno python donde instalar las librerías
```
sudo apt-get install virtualenv
virtualenv --python=python3 testvisual
source testvisual/bin/activate
```
Y procedemos a instalar todas las librerías necesarias:
```
pip install google-cloud-storage
pip install google-cloud-vision
pip install instaLooter
pip install fs-gcsfs
```
Mediante scp se envían los scripts de prueba, imágenes y las credenciales de acceso necesarias:
```
scp testvisualenv/indigo-pod-344620-5cee76b95a93.json  daniel_gonzalez_alonso@35.233.99.128:~/
scp scripts/* daniel_gonzalez_alonso@35.233.99.128:~/
```
Y probamos a ejecutar los scripts de prueba:
```
(testvisual) daniel_gonzalez_alonso@instance-1:~$ export GOOGLE_APPLICATION_CREDENTIALS="indigo-pod-344620-5cee76b95a93.json"
(testvisual) daniel_gonzalez_alonso@instance-1:~$ ./testvisual/bin/python3 gcloudtest.py 
File happy.jpg uploaded to happy.jpg.
(testvisual) daniel_gonzalez_alonso@instance-1:~$ ./testvisual/bin/python3 visiontest.py 
response:
face_annotations {
  bounding_poly {
    vertices {
      x: 118
      y: 6
    }
    vertices {
      x: 168
      y: 6
    }
    vertices {
      x: 168
      y: 64
    }
    vertices {
      x: 118
      y: 64
    }
  }
...
(testvisual) daniel_gonzalez_alonso@instance-1:~$ ./testvisual/bin/python3 gcsfstest.py 
File happy.jpg uploaded to happy.jpg.
```
Los anteriores scripts que emplean las APIs de google funcionan sin problemas, pero instaLooter no funciona. Parece que el problema es que la maquina virtual no tiene ningún navegador instalado, así que se va a proceder a instalar firefox-esr para que instalooter pueda acceder a Instagram.
```
sudo apt-get install firefox-esr
```
Una vez instalado, instalooter sigue sin funcionar, tras investigar un rato parece que el problema es que mientras que en mi equipo me he logeado en mi cuenta anteriormente, en esta maquina virtual no, con lo cual, al entrar a logearse sale una ventana para aceptar las cookies y por ello instalooter no consigue progresar. Para solventar esto se va a proceder a entrar a instagram desde esta maquina virtual:
Para poder acceder a firefox hay que habilitar X11 forwarding. Para ello hay que instalar
```
sudo apt-get install xauth x11-apps
```
Se modifica "/etc/ssh/sshd_config" para habilitar "X11Forwarding yes" y reiniciamos. Después nos conectamos con "ssh -Y daniel_gonzalez_alonso@35.233.99.128" y con ejecutar el comando "firefox" este ya funciona, creando una ventana de firefox en nuestro equipo desde la que se puede entrar a Instagram. Al intentar entrar efectivamente se ve una ventana para aceptar las cookies, además al logearse sale una ventana advirtiendo de que se trata de un intento de logearse inusual, posiblemente para prevenir hackeos de cuentas y que hay que verificar el acceso mediante un código. Tras meter el código ya puedo entrar en la cuenta, y al probar los scripts de instalooter parece que funcionan:
```
(testvisual) daniel_gonzalez_alonso@instance-1:~$ ./testvisual/bin/python3 instalootertest.py valladolid
User: zalez_95
Password: yLPf3O0NuyXa
Logged in? True

Downloaded:	1/1	100.000%
Finished! Downloaded 1 pictures
```
Con esto se podría concluir que estos scripts se pueden ejecutar ya sin problemas en las maquinas virtuales del Compute Engine

# 24/04/2022
Revisando las opciones de la API de Google Vision parece que no es posible extraer información como edad o género ya que han debido de eliminar esa capacidad hace no demasiado. He encontrado la siguiente historia https://web.archive.org/web/20200902214144/https://diversity.google/story/ethics-in-action-removing-gender-labels-from-clouds-vision-api/ en The Wayback Machine (ahora mismo no es accesible, creo que lo han borrado) de los motivos por lo que eliminaron esta capacidad. Revisando alternativas parece Microsoft Azure tiene también una API de Computer Vision que si que extrae ese tipo de características junto con las emociones de acuerdo a su documentación https://docs.microsoft.com/es-es/azure/cognitive-services/face/concepts/face-detection. Parece que Azure ofrece 200 USD para llevar a cabo pruebas en plataforma durante 1 mes, 100 más durante un año si se demuestra que es estudiante. Además:
* Máquina virtual con Linux durante 750 horas
* Azure Database for PostgreSQL durante 750 horas 32 GBs
* Computer Vision durante 5000 transacciones al mes
* Face 30.000 transacciones al mes -> Computer vision que necesitamos?
* Azure Blob Storage 5 GBs
* Azure File Storage 5 GBs
He comprobado que existe una librería para Python fs-azureblob para usar su almacenamiento en la nube del mismo modo que con gcsfs. No sé si conviene hacer el cambio o no.

También existe la alternativa Amazon AWS, mirando su página web https://aws.amazon.com/es/blogs/aws/aws-educate-credits-training-content-and-collaboration-for-students-educators/ parece que ofrece 35 USD de forma gratuita a los estudiantes, aunque no pone durante cuanto tiempo y como la página es antigua puede que esto haya cambiado. Amazon AWS tiene también una API de Computer Vision que permite obtener edad, género y emociones Tambien existe una librería de python https://github.com/PyFilesystem/s3fs para acceder a su sistema de almacenamiento como gcsfs.

Probando con Azure:
* Yendo a Inicio > Servicios Gratuitos > Máquina Virtual con Linux
* Configuracion:
  * Nombre VM: VallTourismInsta
  * Ubuntu Server 16.04 LTS Gen 1
  * Ubicación: West Europe
  * Seguridad: Estándar
  * Sin redundancia
  * Autenticación: Clave pública SSH
  * Nombre Usuario: daniel
  * Nombre par claves SSH: azure_pubkey
  * Puerto de acceso: SSH 22

La Máquina virtual ha de ser B1S para que sea gratuita, pero parece que nodeja seleccionarla dando un error "Tamaño no disponible

Este tamaño no está disponible actualmente en eastus para la suscripción NotAvailableForSubscription."

Segun la respuesta a una duda puede que sea un problema de disponibilidad del servicio
https://docs.microsoft.com/en-us/answers/questions/793359/vm-size-b1s-not-available-in-multiple-regions.html

Se va a intentar probar con Amazon AWS ya que parece que es un problema que sucede habitualmente a ver si esta plataforma es más fiable.

# 25/04/2022
Una vez registrado en AWS, creamos unas credenciales de acceso desde el menu de cuenta superior derecha > credenciales de seguridad > claves de acceso > Crear clave de acceso, y damos a descargar.

Después vamos a crear una VM. Para ello en la pantalla inicial se da a "Lance una máquina virtual con EC2" con región Irlanda (eu-west-1) seleccionada, la llamamos VallTourismInsta y elegimos Debian 11 de 64 bits, por defecto se emplea 1 CPU y 1GB de RAM que es la opción gratuita (t2.micro), también cambiamos el almacenamiento de 8 a 30 GBs de almacenamiento SSD (el máximo gratuito). Le damos a permitir acceso con HTTPS para que genere una IP estática y creamos claves de acceso "VallTourismInsta" de tipo RSA .pem. Finalmente le damos a crear instancia.

"Nivel gratuito: El primer año incluye 750 horas de uso de instancias t2.micro (o t3.micro en las regiones en las que t2.micro no esté disponible) en las AMI del nivel gratuito al mes, 30 GiB de almacenamiento de EBS, 2 millones de E/S, 1 GB de instantáneas y 100 GB de ancho de banda a Internet"

Nos metemos con ssh mediante
```
sudo chmod 600 VallTourismInsta.pem
ssh -i "VallTourismInsta.pem" admin@ec2-3-250-43-138.eu-west-1.compute.amazonaws.com
```

Procedemos a instalar librerías:
```
sudo apt update
sudo apt install python3 python3-dev python3-venv
sudo apt-get install wget
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
sudo apt-get install virtualenv
sudo apt-get install firefox-esr
sudo apt-get install xauth x11-apps
sudo apt-get install git
virtualenv --python=python3 testvisual
source testvisual/bin/activate
pip3 install instaLooter
```
Las de google no puesto que tenemos que usar las de AWS:
```
pip3 install boto3
pip install fs-s3fs
```

Creamos un bucket de almacenamiento desde Servicios > Almacenamiento > S3, desde hay damos a crear bucket
* Nombre: valltourisminstabucket
* Región: UE west-1 (Irlanda)
* ACL deshabilitadas
* Sin control de version
* Sin cifrar

"Al registrarse, los clientes nuevos de AWS reciben 5 GB de almacenamiento de Amazon S3 en la clase de almacenamiento S3 Standard, 20 000 solicitudes GET, 2000 solicitudes PUT, COPY, POST o LIST y 100 GB de transferencia de datos de salida al mes."

Probamos que funciona instalooter, para ello hay que conectarse con "ssh -Y" para poder logearnos por primera vez en instagram y solventar el problema ya visto en google cloud de la pantalla de cookies y del acceso inusual. Una vez logeado por primera vez, probamos todos los scripts creados que reemplazan los servicios de google por los de amazon, y parece que el resultado es satisfactorio:
```
(testvisual) admin@ip-172-31-21-254:~$ ./instalooters3fstest.py valladolid
Insta User: zalez_95
Insta Password: yLPf3O0NuyXa
AWS Access Key ID: AKIA2BIQPL3AKI53QO5K
AWS Access Key Secret: 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
['happy.jpg']
Logged in? True

Downloaded:	50/50	100.000%
Finished! Downloaded 50 pictures

(testvisual) admin@ip-172-31-21-254:~$ ./mainScriptAWS.py mane6
Insta User: zalez_95
Insta Password: yLPf3O0NuyXa
AWS Access Key ID: AKIA2BIQPL3AKI53QO5K
AWS Access Key Secret: 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
Logged in? True

Downloaded:	50/50	100.000%
Finished! Downloaded 50 pictures
2822652856770135681.jpg: {'FaceDetails': [], 'ResponseMetadata': {'RequestId': '167b1fc0-1879-4c38-822c-7bf9642221ba', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '167b1fc0-1879-4c38-822c-7bf9642221ba', 'content-type': 'application/x-amz-json-1.1', 'content-length': '18', 'date': 'Mon, 25 Apr 2022 20:31:49 GMT'}, 'RetryAttempts': 0}}
```

# 27/04/2022
Almacenamiento. alternativas:
* SQL -> parsear JSON y guardar los resultados en alguna tabla
* NoSQL -> guardar el JSON en la base de datos y procesarlo durante la lectura

Ventajas NoSQL -> rendimiento y escalabilidad con grandes conjuntos de datos

En Google Cloud se pueden crear bases de datos SQL con motor de base de datos MySQL, PostgreSQL y SQL Server. Para NoSQL se dispone de bases de datos documentales como Cloud Datastore, Cloud Firestore (siguiente generación de Datastore), MongoDB (varias versiones), Bigtable...

En Amazon AWS se pueden crear bases de datos SQL en RDS (750 horas gratis al mes con la cuenta gratuita) con motor de base de datos MySQL, MariaDB, Oracle, PostgreSQL, SQL Server y Amazon Aurora. Para NoSQL se disponde de DynamoDB (25 GB gratuitos) y DocumentDB (compatible con MongoDB, solo se disponde de 1 mes de prueba).

# 30/04/2022
Prueba MongoDB:
* En Google Cloud parece que no es gratuito, y pagar excedería el presupuesto que da Google Cloud de forma gratuita inicialmente. Esto se haría desde > servicios de google > "MongoDB Virtual Machine". La alternativa gratuita que da Google es emplear Firestore, pero parece que solo da 1 GB de almacenamiento gratuito, lo cual parece muy escaso, aunque para hacer pruebas podría servir teniendo en cuenta que solo almacenaríamos objetos JSON.
* En Amazon AWS como se comentó anteriormente habría que emplear DocumentDB, que parece que es compatible con MongoDB, ya que segun su página web
"Amazon DocumentDB implementa la API de MongoDB 3.6 y 4.0 de código abierto de Apache 2.0 emulando las respuestas que un cliente de MongoDB espera de un servidor de MongoDB"
El problema es que Amazon solo permite usarlo de forma gratuita durante 750 horas el primer mes. La otra base de datos NoSQL que tiene es DynamoDB, que nos da 25GBs "para siempre", pero no es MongoDB. En caso de usar SQL se disponde 20 GBs de almacenamiento durante 12 meses con 750 horas al mes.
* En Microsoft Azure se disponde de MongoDB Atlas. La capa gratuita permite usarlo durante un año pero está limitada a 512MBs. Tambien está la opción "Azure Cosmos DB", donde se puede escoger la API de Mongo DB, pero no me queda claro si está limitado a 1 mes o no. De todos modos a día de hoy sigo sin poder crear una de las MVs gratuitas.

Otra alternativa sería instalarlo directamente en las VMs creadas, pero el almacenamiento en ellas también es bastante limitado.

# 01/05/2022
Trabajos relacionados. Strings de búsqueda:
* (Sentiment Analysis OR Emotion Recognition) AND Social Media AND Tourism
* (Sentiment Analysis OR Emotion Recognition) AND Images AND Recommendation System
Otros filtros: acceso público y entre 2015 y 2022

Resultados:
| String Búsqueda | Título | Fecha Publicación | URL | Abs Redes Sociales | Abs Análisis Sentimientos | Abs Sis. Recomendación Turismo | No gratuito | No EN/ES | Abs Recopilación | Abs No análisis sentimientos | Abs fuente no redes sociales | Leer |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Sentiment Analysis in TripAdvisor | 17/08/2017 | https://ieeexplore.ieee.org/abstract/document/8012330 | N | S | N | N | N | N | N | S | N |
| 1 | Using Social Media in Tourist Sentiment Analysis: A Case Study of Andalusia during the Covid-19 Pandemic | 2021 | https://www.mdpi.com/2071-1050/13/7/3836 | S | S | N | N | N | N | N | N | S |
| 1 | Sentiment analysis in hospitality and tourism: a thematic and methodological review | 11/10/2021 | https://www.emerald.com/insight/content/doi/10.1108/IJCHM-02-2021-0132/full/html?utm_source=rss&utm_medium=feed&utm_campaign=rss_journalLatest | N | S | N | S | N | S | N | S | N |
| 1 | Sentiment Analysis to Measure Quality and Build Sustainability in Tourism Destinations | 26/05/2021 | https://www.mdpi.com/2071-1050/13/11/6015 | S | S | N | N | N | N | N | N | S |
| 1 | Sentiment analysis of foreign tourists to Bangkok using data mining through online social network | 2017 | https://ieeexplore.ieee.org/abstract/document/8104921 | S | S | N | S | N | N | N | N | N |
| 1 | A Survey of Sentiment Analysis from Social Media Data | 04/2020 | https://ieeexplore.ieee.org/abstract/document/8951256 | S | S | N | S | N | S | N | N | N |
| 1 | Multimodal Event-Aware Network for Sentiment Analysis in Tourism | 11/05/2021 | https://ieeexplore.ieee.org/abstract/document/9428534 | S | S | N | S | N | N | N | N | N |
| 1 | Tourism destination management using sentiment analysis and geo-location information: a deep learning approach | 2021 | https://link.springer.com/article/10.1007/s40558-021-00196-4 | S | S | N | N | N | N | N | N | S |
| 1 | Multi-Language Sentiment Analysis for Hotel Reviews | 2016 | https://www.matec-conferences.org/articles/matecconf/abs/2016/38/matecconf_icmie2016_03002/matecconf_icmie2016_03002.html | N | N | N | N | N | N | S | S | N |
| 1 | A survey on sentiment analysis in tourism | 06/2021 | https://journals.ekb.eg/article_106309.html | N | S | N | N | N | S | N | N | N |
| 1 | A Recommendation Mechanism for Under-Emphasized Tourist Spots Using Topic Modeling and Sentiment Analysis | 34/12/2019 | https://www.mdpi.com/2071-1050/12/1/320 | S | S | S | N | N | N | N | N | S |
| 1 | Personalized Travel Recommendation Based on Sentiment-Aware Multimodal Topic Model | 13/08/2019 | https://ieeexplore.ieee.org/document/8796367 | S | S | S | N | N | N | N | N | S |
| 2 | Tourist Recommender Systems Based on Emotion Recognition—A Scientometric Review | 24/12/2020 | https://www.mdpi.com/1999-5903/13/1/2 | N | S | S | N | N | S | N | S | N |
| 2 | Integrating contextual sentiment analysis in collaborative recommender systems | 22/03/2021 | https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0248695 | N | S | N | N | N | N | N | S | N |
| 2 | Emotion and Sentiment Analysis using Machine Learning | 2021 | https://www.annalsofrscb.ro/index.php/journal/article/view/307 | N | S | N | N | N | N | N | S | N |
| 2 | A Sentiment Analysis based Approach to Facebook User Recommendation | ? | https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.682.7321&rep=rep1&type=pdf | S | S | N | N | N | N | N | N | S |
| 2 | Tweets Classification and Sentiment Analysis for Personalized Tweets Recommendation | 17/12/2020 | https://www.hindawi.com/journals/complexity/2020/8892552/ | S | S | N | N | N | N | N | N | S |
| 2 | Text-based Emotion Aware Recommender | 2020 | https://arxiv.org/abs/2007.01455 | N | S | N | N | N | N | N | S | N |
| 2 | IPARS: An Image-based Personalized Advertisement Recommendation System on Social Networks | 2022 | https://www.sciencedirect.com/science/article/pii/S187705092200463X | S | N | N | N | N | N | S | N | N |
| 2 | Deep Learning based sentiment analysis for recommender system | ? | https://anale-informatica.tibiscus.ro/download/lucrari/16-2-23-P.pdf | N | S | N | N | N | N | N | S | N |
| 2 | Human Sentiment Analysis on Social Media through Naïve Bayes Classifier | 2022 | https://bhu.ac.in/research_pub/jsr/Volumes/JSR_66_01_2022/37.pdf | S | S | N | N | N | N | N | N | S |
| 2 | Emotion and Sentiment Analysis from Twitter Text | 11/2018 | https://prism.ucalgary.ca/handle/1880/107533 | S | S | N | N | N | N | N | N | S |

# 05/05/2022
Reunión:
* Usar amazon aws
* Mirar como va dynamodb y que frontends hay para mostrar jsons
* Sacar unos cuantos hashtags como:
    #Valladolid #ValladolidEspaña #ValladolidSpain #ValladolidenFotos #PicoftheDay #IgersValladolid #Estaes_Valladolid #MeGustaValladolid #MeGustaPucela #Pucela #CatedralValladolid
* Almacenar el json de instalooter y rekognition
* Recomendar la publicacion filtrando por genero, edad y sentimiento positivo
* Mirar en base al perfil que informacion se puede sacar: edad, genero y puede que más cosas

# 14/05/2022
Sobre sacar la información del usuario: Parece que instalooter no puede sacar ese tipo de metadatos, tal vez esa información sea privada, cuando entras en el perfil de instagram del alguien no puedes ver su edad/genero. Tal vez puedan analizarse las ultimas X fotos del perfil del usuario y analizarlas con rekognition, sacando la moda del genero de las fotos y edad y tirar con eso. Problema: probando parece que instalooter peta, parece que en github le pasa a mas gente, posiblemente porque la web haya cambiado. Tal vez se podría hacer un fork para corregirlo si fuese necesario.

Sobre Dynamo DB: es servicio de base de datos NoSQL escalable horizontalmente de Amazon AWS. De acuerdo con ¿Amazon? un servicio de alta disponibilidad. Es ideal para ciertos patrones de acceso. El documento "Dynamo: Amazon’s Highly Available Key-value Store" explica los motivos y las características de DynamoDB, interesante lectura para la memoria.

Para usar DynamoDB existe un cliente python al igual que con el resto de servicios, un ejemplo de uso se encuentra en: https://docs.aws.amazon.com/es_es/amazondynamodb/latest/developerguide/GettingStarted.Python.01.html

Se ha creado un ejemplo que crea una tabla e introduce un item con un json entero

# 18/05/2022
Hashtags posibles:
Naturaleza_valladolid, estaes_valladolid, valladolidturismooficial, turismovalladolid, valladolidturismo, turismovalladolid, valladolidspain, valladolidfotos, valladolidenfotos, valladolid, todo_valladolid, total_valladolid, igersvalladolid, igervalladolid, catedraldevalladolid, paseandoporvalladolid, valladolidgram, instavalladolid, valladolidlove, valladolidlife, valladolidmola, megustavalladolid, fotosdevalladolid, valladolidhoy, vallafotos, valladolidinquieta, love_valladolid, visitvalladolid, look_valladolid, ok_valladolid, megustavalladolid, asi_es_valladolid, pucela, megustapucela, arquitecturavalladolid, valladolidespaña, culturavalladolid, valladolidcapital, valladolidcampogrande, valladolidpaseozorrilla, iglesiadelaantiguavalladolid, igerspucela, rinconesdevalladolid, megustapucela

Amazon Lightsail para hosting web

# 19/05/2022
Reunión:
preparar ejemplo para la siguiente sesion
herramientas de Business Intelligence
Quick Sight

# 27/05/2022
Tras evaluar las alternativas se decide alojar la BBDD en DynamoDB ya que se están empleando los servicios de AWS, y la alternativa de DocumentDB que sería útil para almacenar JSONs sin tener que preprocesarlos y que es compatible con MongoDB tiene un periodo de prueba de sólo 30 días, insuficiente para nosotros.

Para crear la BBDD en DynamoDB solo hay que crear las tablas con el nombre que queramos. La idea inicial es tener 2 tablas, la primera para el json de instalooter a la que llamaríamos "looter". En esta introduciremos los siguientes atributos sacados del JSON original de instalooter:
  * id
  * timestamp
  * shortCode
  * displayUrl
  * description
  * likesCount
  * commentsCount
El atributo id se corresponde con el mismo id del JSON y que a su vez se corresponde con el nombre del JSON descargado. La idea es usar este string como una partition key. Por otro lado tendríamos la tabla con el JSON generado al procesar la imágen de instalooter mediante el servicio de Rekognition a la que llamríamos "rekognition". Este JSON tiene un array de "caras", de cada cara se pretende introducir la siguiente información sacada del JSON:
  * confidence
  * ageLow
  * ageHigh
  * gender
  * eyeglasses
  * sunglasses
  * beard
  * moustache
  * happyConfidence
  * surprisedConfidence
  * fearConfidence
  * sadConfidence
  * angryConfidence
  * disgustedConfidence
  * confusedConfidence
  * calmConfidence
Además para indexar se pretende emplear el mismo id empleado en la tabla de "looter" como partition key, pero como el json tiene un array es posible que se de la situación de tener que introducir varios items en la tabla por cada json, con lo cual usar solo este valor como clave no funcionaría, habría que crear una clave compuesta con otro valor, en este caso se podría usar el indice en el array como sort key para generar la clave compuesta junto con el "id" anterior. El problema que tenemos al almacenar los datos de esta manera es que en DynamoDB no se pueden hacer Joins de tablas en las consultas tal y como haríamos en SQL de darse esta misma situación. Para solventar esta relación de one-to-many en DyanmoDB tenemos varias opciones (https://www.alexdebrie.com/posts/dynamodb-one-to-many/):
* Duplicar los datos del json instalooter para cada cara obtenida mediante rekognition
* Duplicar los datos del json instalooter para cada cara obtenida mediante rekognition, pero metiendo el json entero en un atributo en vez de generar atributos a partir de él
* Generar una clave compuesta usando algún tipo de prefijo en el sort key

Se ha decidido emplear la primera opción ya que permite sacar toda la información en una única consulta, pudiendo filtrar por todos los atributos si fuese necesario a diferencia de la segunda. El problema de la tercera opción es que DynamoDB tampoco soporta agregación de items, con lo cual si quisieramos sacar los datos de instalooter de cada cara, por ejemplo, tendríamos que hacer otra query por cada valor lo cual implicaría muchas consultas, pudiendo pudiendo ser un proceso extremadamente lento.

Por lo tanto, para implementar la implementación de la base de datos se emplea una única tabla llamada "valltourisminsta" con clave de partición "id" cuyo valor es el id/nombre de fichero generado por instalooter, y como sort-key un valor númerico "faceIndex" que es el índice de la cara en el array de caras. De esta forma tenemos un índice compuesto que permite diferenciar entre las caras de rekognition, garantizando así que las entradas en la tabla sean únicas, pero además tambien podemos sacar todas las caras si en la consulta solo preguntamos por el id, y además podemos obtener la información de instalooter almacenada junto a las caras.

Una vez creado la tabla y poblada con los datos de S3, se puede buscar en ellas desde el menu de explorar elementos usando filtros, o hacer consultas similares a SQL con el editor PartiQL de DynamoDB. Por ejemplo:
```SQL
SELECT *
FROM valltourisminsta
WHERE "moustache"=false AND "gender"='Male'
```

También se puede emplear boto3 para hacer queries sobre nuestra tabla, pero estos solo funcionan buscando por las claves de particion u ordenación, si se quiere emplear otro atributo hay que generar nuevos índices secundarios. Estos indices secundarios pueden ser globales o locales, los locales hay que hacerlos en el momento de crear la tabla mientras que los globales pueden crearse en cualquier momento. En ambos casos se pueden tener items repetidos para una misma clave secundaria. Otra opción es usar la función scan e ir filtrando por los atributos, pero esta funcion itera cada item con lo cual el rendimiento puede ser malo, aunque ahora con pocos datos puede dar igual.

Ejemplo de creación de indice local secundario en python:
```python
					...
					LocalSecondaryIndexes=[
						{
							"IndexName" : "gender",
							"KeySchema" : [
								{
									"AttributeName" : "id",
									"KeyType" : "HASH"
								},
								{
									"AttributeName": "gender",
									"KeyType": "RANGE"
								},
							],
							"Projection" : { "ProjectionType": "ALL" }
						}
					],
					AttributeDefinitions=[
						...
						{
							"AttributeName" : "gender",
							"AttributeType" : "S"
						}
					],
					...
```

# 29/05/2022
Sobre los DashBoards:

QuickSight solo es gratuito durante los primeros 30 días, después hay que pagar, además no se puede utilizar directamente contra una base de datos DynamoDB aunque el servicio también se de Amazon, sino que hay que emplear un conector para que pueda hacer consultas a DynamodDB traves de Amazon S3 con el otro servicio conocido como Amazon Athena y que no se encuentra en la capa gratuita de AWS.

Otras alternativas que se han evaluado han sido:
  * QLik -> lo conozco por la asignatura de Inteligencia de Negocio, parece que tampoco se puede usar directamente con DynamoDB, sino que hay que usar un conector ODBC de la empresa Simba que no es gratuito
  * PowerBI, de microsoft. Al igual que el anterior, ofrece un periodo gratuito de prueba pero no tiene conectores con dynamodb, habría que usar el conector ODBC de Simba anteriormente comentado
  * Tableau -> tiene un trial de 3 meses, existe version public gratuita. Para usar dynamodb habría que usar un conecto JDBC de Rockset o de algun otro tipo
  * Viendo las opciones de software libre he encontrado Grafana, pero no tiene conector gratuito con DynamoDB

Otra opción: Hacerlo a mano en una web estática haciendo peticiones a DynamoDB a través de Javascript y la API de AWS, y mostrarlo en tablas y gráficos con una librería como Chart.js como hacen en: https://medium.com/@rfreeman/serverless-dynamic-real-time-dashboard-with-aws-dynamodb-a1a7f8d3bc01  

# 30/05/2022
Prueba de la opción de Chart.js:

Creamos un nuevo bucket en AWS S3 llamadao webvalltourisminstabucket (ubicación irlanda). En propiedades del bucket entramos en "Editar alojamiento de sitios web estáticos" y habilitamos el alojamiento web estático. Los documentos de índice y error serán index.html y error.html respectivamente. Después vamos a permisos del bucket y en "Editar el bloqueo de acceso público (configuración del bucket)" deshabilitamos "bloquear todo el acceso público", y en "Editar la propiedad del objeto" habilitamos las listas ACL.

Subimos el index.html al bucket y los scripts de Chart.js (descargado de https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.8.0/chart.min.js) y valltourisminsta-chart-dashboard.js. Una vez subidos, vamos a permisos y en "Editar lista de control de acceso" habilitamos lectura del Objeto a "Todo el mundo" en cada uno de los ficheros.

Una vez guardado, el acceso a la web estática se hará a través de la url http://webvalltourisminstabucket.s3-website-eu-west-1.amazonaws.com/

Deberíamos ver el html con el navegador a lentrar a esa url.

Ahora hay que configurar el acceso desde JS a la base de datos de DynamoDB. para ello vamos a usar AWS Cognito, servicio que se incluye dentro de la capa gratuita de AWS hasta 50K MAU. Para ello en la consola de AWS buscamos Cognito y damos a "Administrar grupos de identidades" y creamos uno nuevo llamado "VallTourismInsta" y le damos a "Habilitar el acceso a identidades sin autenticar". Creamos el grupo y después sale una página para identificar los roles IAM del nuevo grupo de identidades, en los roles permitidos a las identidades sin autenticar le damos los siguientes roles para que puedan leer de las tablas:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "mobileanalytics:PutEvents",
                "cognito-sync:*"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "DynamoDBAccess",
            "Effect": "Allow",
            "Action": [
                "dynamodb:BatchGetItem",
                "dynamodb:DescribeStream",
                "dynamodb:DescribeTable",
                "dynamodb:GetItem",
                "dynamodb:GetRecords",
                "dynamodb:GetShardIterator",
                "dynamodb:ListStreams",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": [
                "arn:aws:dynamodb:eu-west-1:689913683648:table/valltourisminsta"
            ]
        }
    ]
}
```
Después aceptamos y podemos generar un "código de muestra" JS con el que poder acceder a las tablas. Al darle muestra:
```javascript
// Inicializar el proveedor de credenciales de Amazon Cognito
AWS.config.region = 'eu-west-1'; // Región
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'eu-west-1:bda8761f-9ad7-41b2-aa1d-8c09e00dfa22',
});
```

Que se puede meter en nuestro código javascript para acceder a nuestras tablas de dynamodb.


# 07/06/2022
Durante la demo con el tutor el script creado falló, parece que no se podía logear en instagram con Instalooter. Tras revisar el error y el código del login de instaloader, parece que ha debido de haber algún cambio en la web de instagram que hace que haya empezado a fallar. Como no se sabe cuando esta librería se actualizará para arreglar este error, y viendo que los últimos commits tienen unos meses, empecé a mirar la alternativa de usar otra librería llamada Instaloader a pesar de haber implementado ya el script empleando la otra librería. Tras unas pruebas se pudo ver que la forma en que trabaja es bastante distinta, y no puedo emplearla directamente con Amazon S3 para comprobar si un post de instagram ya ha sido procesado y guardar directamente allí las nuevas imágenes/jsons. Por ello tras revisar el código del login decidí corregir el error de instalooter en un fork de la librería. Parece que el error consiste en un cambio en las urls y en como se gestionan las cookies donde se guarda el token para indicar que se está logeado o no en la página web. Tras implementar los cambios de forma similar a como lo hace instaloader, instalooter volvió a poder logearse en instagram (se ha hecho un pull requests de estos cambios, aunque todavía no se ha aceptado).

Después del cambio anterior, se probó a usar este fork con mi script y este volvió a funcionar. Se grabo la demo para que la pudiera visualizar el tutor tal y como se quedó en la anterior reunión.

Para instalar este fork hay que ejecutar
```
pip3 install git+https://github.com/Zalez95/InstaLooter.git
```


# 11/06/2022
Se quedó con el tutor en probar a usar algun dashboard a pesar de que tras revisar las alternativas anteriormente no parecía que hubiese algun candidato gratuito o libre debido a la falta de conectores con dynamodb. Tras revisar en la web he dado con el siguiente link:
https://www.linkedin.com/pulse/using-aws-lambda-api-gateway-server-less-grafana-adapters-jonas-birm%C3%A9
donde en resumidas cuentas, se usa AWS lambda para implementar un conector para grafana, creando básicamente un servidor REST en este servicio de AWS. Revisando la capa gratuita de AWS, Grafana no es gratuito en AWS, pero como Grafana es software libre, nada me impide instalarlo en la maquina virtual que se ha creado. También parece que lambda está incluido con hasta 1000000 de solicitudes al mes por si fuera necesario.

Instalación de Grafana:
```
sudo apt-get install -y adduser libfontconfig1
wget https://dl.grafana.com/enterprise/release/grafana-enterprise_9.0.0_amd64.deb
sudo dpkg -i grafana-enterprise_9.0.0_amd64.deb
sudo service grafana-server start
```

Grafana se ejecuta por defector en el puerto 3000, si se quiere entrar desde fuera hay que abrir el puerto. En el caso de una instancia EC2 como la que se está usando, hay que hacer lo siguiente:
  Ir a EC2 > Grupos de Seguridad > pinchar en el grupo de seguridad de nuestra instancia > Editar Regla
  Ahí añadimos una regla desde "Agregar regla", de tipo TCP personalizado con puerto 3000 y origen 0.0.0.0/0

Despues podemos entrar desde http://3.250.43.138:3000/login con user: admin; pass: admin

En el articulo se comentaba usar Grafana con un Web Service REST con el plugin SimpleJson, parece que este plugin está deprecado, pero existe otro conocido como JSON que parece que lo ha reemplazado.

Para las pruebas iniciales se ha decidido levantar un servidor REST local en python empleando la API Bottle.
```
pip3 install bottle
```

Este servidor implementa las APIs REST: Get /, POST search, POST query, POST tagKeys, POST tagValues para poder recuperar los datos de DynamoDB tal y como se indica en la documentación del plugin https://github.com/simPod/GrafanaJsonDatasource

Se ha apuntado a este servidor local y el plugin se ha conectado con éxito. Para conectarse tan solo ha habido que añadir un Data Sources con nombre VallTourismInstaREST, URL localhost:8080 y timeout 60secs. Si le damos a "Save & test" deberia salir un tick diciendo que el data source funciona.

Vamos a Create>Dashboard. En configuracion ponemos el nombre "VallTourismInstaDashboard", y empezamos a crearlo.

Para poder filtrar se ha añadido un filtro desde Settings > Variables, llamado filter1, label "Filter 1", descripción "The Filter 1", tipo "Ad hoc filters" y "Data source" a "VallTourismInstaREST".


https://www.youtube.com/watch?v=ijyeE-pXFk0
https://play.grafana.org/d/OhR1ID6Mk/3-table?orgId=1


# 16/06/2022
Reunión:
* Llenar BBDD
* Dashboard está ok, mirar qué añadir más cuando haya más datos
* Memoria:
  * Enviar lo antes posible Estado del Arte para que vaya corrigiendo
  * Añadir en "aportes" el hecho de haber hecho un fork/corrección de Instalooter
  * Explicar el "conector" de Grafana con DynamoDB


# 18/06/2022
Se han movido las peticiones de usuario del script principal a variables de entorno declaradas en .bashrc
```
# ENV VARS
export INSTA_USER="..."
export INSTA_PASS="..."
export AWS_AKEY_ID="..."
export AWS_AKEY_SECRET="..."
```

También se ha puesto un límite para el número de imagenes que se pueden procesar con rekognition, de forma que no se supere las 5000 peticiones mensuales permitidas de forma gratuita. Este contador se mantiene en un fichero "rekognitionImgCount.txt" en Amazon S3, de forma que el script se pueda ejecutar multiples veces sin que se pierda este contador. Mensualmente este contador tendría que ser puesto a 0 ya sea cambiando su valor en el fichero o borrandolo, algo que podría ser implementado sencillamente con algun cron.

Se ha empezado a llenar la BBDD


# 26/06/2022
Movemos el servidor REST creado para el plugin de Grafana JSON a AWS API Gateway para obtener mejor rendimiento. Para ello vamos primero a crear las funciones lambda.

En AWS Lambda vamos a Funciones > Crear Funcion
La llamamos grafana_query con entorno x86_64 y Python 3.8, le damos a crear y pegamos el código de query. Después vamos a configuración > Variables de Entorno y pegamos las claves de AWS AWS_AKEY_ID y AWS_AKEY_SECRET, y tambien en la "Configuración general" modificamos el "Tiempo de espera" de 3sec a 1min. Le damos a deploy. Hacemos lo mismo con las funciones search, tag-keys y tag-values, y también añadimos una función grafana_helloworld con el código python por defecto


Después vamos a crear las APIs REST
Vamos Amazon API Gateway y creamos una API REST con nombre "valltourisminsta" y con descripción "Grafana API REST"

Creamos los recursos query, search, tag-keys y tag-values que tendrán las rutas /query, /search, /tag-keys y /tag-values respectivamente. A cada recurso le añadimos un método POST que apunta a su correspondiente función de AWS Lambda. Por último añadimos un método GET a la ruta raíz / y apuntamos a la función lambda por grafana_helloworld

Finalmente en Acciones le damos a "Implementar la API", en una nueva etapa que llamaremos "demo". Al aceptar nos devuelve el endpoint que tendremos que usar para acceder a las APIs: https://4233qyeevj.execute-api.eu-west-1.amazonaws.com/demo

En Grafana cambiamos la URL de nuestro data source a "https://4233qyeevj.execute-api.eu-west-1.amazonaws.com/demo/"


# 30/06/2022
Reunión
* Continuar con la memoria
* Titulo: Héctor avisara
* Motivación: intereses similares a los mios, turismo...


# 30/06/2022
Prácticamente se han acabado los primero 5 apartados de la memoria, hay que empezar con el trabajo principal. Existen problemas de rendimiento en lambda cuando se hacen muchas búsquedas, posiblemente consecuencia de usar scan en vez de queries -> se aumentan las RCUs.

Link: http://3.250.43.138:3000/d/K0aCHsjnk/valltourisminstadashboard?orgId=1&var-filter1=ageLow%7C%3E%7C18&var-filter1=gender%7C%3D%7CMale
