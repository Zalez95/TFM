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
* Proceso de busqueda -> generar unbos strings de busqueda. palabras clave obtenidas mediante la estrategia PICOC. Una vez obtenidos los strings filtrar tambien por fechas (ej: 2015-2019) y que el acceso sea libre/gratuito
* Seleccion de muestras -> Proceso: 1. eliminar duplicados, 2. eliminar tras leer el abstract basandise en criterios de inclusion y de exclusion (si cumple algun criterio de exclusion o no cumple ningun criterio de inclusion descartar). 3. Leer por completo los articulos y decidir si son relevantes en base a un cuestionario (¿6? preguntas si -1 punto- o no -0 puntos- y sacar minimo un 4) para obtener proximadamente ¿10? muestras
* Extraccion de informacion: Definir que se quieres sacar de los articulos. ej: algoritmo usado, resultados obtenidos, dataset empleado, etc.
