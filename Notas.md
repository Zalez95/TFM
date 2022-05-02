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

Después vamos a crear una VM. Para ello en la pantalla inicial se da a "Lance una máquina virtual con EC2", la llamamos VallTourismInsta y elegimos Debian 10 de 64 bits, por defecto se emplea 1 CPU y 1GB de RAM qeue es la opción gratuita. Creamos claves de acceso "valltourisminsta" de tipo RSA .pem y 30 GBs de almacenamiento SSD (el máximo gratuito) y le damos a crear instancia.

"Nivel gratuito: El primer año incluye 750 horas de uso de instancias t2.micro (o t3.micro en las regiones en las que t2.micro no esté disponible) en las AMI del nivel gratuito al mes, 30 GiB de almacenamiento de EBS, 2 millones de E/S, 1 GB de instantáneas y 100 GB de ancho de banda a Internet"

Nos metemos con ssh mediante
```
sudo chmod 600 valltourisminsta.pem
ssh -i "valltourisminsta.pem" admin@ec2-35-173-128-55.compute-1.amazonaws.com
```

Procedemos a instalar librerías:
```
sudo apt update
sudo apt install python3 python3-dev python3-venv
sudo apt-get install wget
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
sudo apt-get install virtualenv
virtualenv --python=python3 testvisual
source testvisual/bin/activate
pip3 install instaLooter
sudo apt-get install firefox-esr
sudo apt-get install xauth x11-apps
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
| String Búsqueda | Título | Fecha Publicación | URL | Abs Redes Sociales | Abs Análisis Sentimientos | Abs Sis. Recomendación Turismo | No gratuito | No EN/ES | Abs Recopilación | Abs No análisis sentimientos | Abs fuente no redes sociales |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Sentiment Analysis in TripAdvisor | 17/08/2017 | https://ieeexplore.ieee.org/abstract/document/8012330 | N | S | N | N | N | N | N | S |
| 1 | Using Social Media in Tourist Sentiment Analysis: A Case Study of Andalusia during the Covid-19 Pandemic | 2021 | https://www.mdpi.com/2071-1050/13/7/3836 | S | S | N | N | N | N | N | N |
| 1 | Sentiment analysis in hospitality and tourism: a thematic and methodological review | 11/10/2021 | https://www.emerald.com/insight/content/doi/10.1108/IJCHM-02-2021-0132/full/html?utm_source=rss&utm_medium=feed&utm_campaign=rss_journalLatest | N | S | N | S | N | S | N | S |
| 1 | Sentiment Analysis to Measure Quality and Build Sustainability in Tourism Destinations | 26/05/2021 | https://www.mdpi.com/2071-1050/13/11/6015 | S | S | N | N | N | N | N | N |
| 1 | Sentiment analysis of foreign tourists to Bangkok using data mining through online social network | 2017 | https://ieeexplore.ieee.org/abstract/document/8104921 | S | S | N | S | N | N | N | N |
| 1 | A Survey of Sentiment Analysis from Social Media Data | 04/2020 | https://ieeexplore.ieee.org/abstract/document/8951256 | S | S | N | S | N | S | N | N |
| 1 | Multimodal Event-Aware Network for Sentiment Analysis in Tourism | 11/05/2021 | https://ieeexplore.ieee.org/abstract/document/9428534 | S | S | N | S | N | N | N | N |
| 1 | Tourism destination management using sentiment analysis and geo-location information: a deep learning approach | 2021 | https://link.springer.com/article/10.1007/s40558-021-00196-4 | S | S | N | N | N | N | N | N |
| 1 | Multi-Language Sentiment Analysis for Hotel Reviews | 2016 | https://www.matec-conferences.org/articles/matecconf/abs/2016/38/matecconf_icmie2016_03002/matecconf_icmie2016_03002.html | N | N | N | N | N | N | S | S |
| 1 | A survey on sentiment analysis in tourism | 06/2021 | https://journals.ekb.eg/article_106309.html | N | S | N | N | N | S | N | N |
| 1 | A Recommendation Mechanism for Under-Emphasized Tourist Spots Using Topic Modeling and Sentiment Analysis | 34/12/2019 | https://www.mdpi.com/2071-1050/12/1/320 | S | S | S | N | N | N | N | N |
| 1 | Personalized Travel Recommendation Based on Sentiment-Aware Multimodal Topic Model | 13/08/2019 | https://ieeexplore.ieee.org/document/8796367 | S | S | S | N | N | N | N | N |
| 2 | Tourist Recommender Systems Based on Emotion Recognition—A Scientometric Review | 24/12/2020 | https://www.mdpi.com/1999-5903/13/1/2 | N | S | S | N | N | S | N | S |
| 2 | Integrating contextual sentiment analysis in collaborative recommender systems | 22/03/2021 | https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0248695 | N | S | N | N | N | N | N | S |
| 2 | Emotion and Sentiment Analysis using Machine Learning | 2021 | https://www.annalsofrscb.ro/index.php/journal/article/view/307 | N | S | N | N | N | N | N | S |
| 2 | A Sentiment Analysis based Approach to Facebook User Recommendation | ? | https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.682.7321&rep=rep1&type=pdf | S | S | N | N | N | N | N | N |
| 2 | Tweets Classification and Sentiment Analysis for Personalized Tweets Recommendation | 17/12/2020 | https://www.hindawi.com/journals/complexity/2020/8892552/ | S | S | N | N | N | N | N | N |
| 2 | Text-based Emotion Aware Recommender | 2020 | https://arxiv.org/abs/2007.01455 | N | S | N | N | N | N | N | S |
| 2 | IPARS: An Image-based Personalized Advertisement Recommendation System on Social Networks | 2022 | https://www.sciencedirect.com/science/article/pii/S187705092200463X | S | N | N | N | N | N | S | N |
| 2 | Deep Learning based sentiment analysis for recommender system | ? | https://anale-informatica.tibiscus.ro/download/lucrari/16-2-23-P.pdf | N | S | N | N | N | N | N | S |
| 2 | Human Sentiment Analysis on Social Media through Naïve Bayes Classifier | 2022 | https://bhu.ac.in/research_pub/jsr/Volumes/JSR_66_01_2022/37.pdf | S | S | N | N | N | N | N | N |
| 2 | Emotion and Sentiment Analysis from Twitter Text | 11/2018 | https://prism.ucalgary.ca/handle/1880/107533 | S | S | N | N | N | N | N | N |
