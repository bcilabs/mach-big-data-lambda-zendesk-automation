# mach-big-data-lambda-template
Template para crear lambdas para el equipo de bigdata (generalmente se usa para crear "motores").

## Pasos de como usar el template
Supuesto: Como ejemplo para el README, supongamos que la lambda tendrá como uso capturar, procesar y guardar la lógica de KYC (Know Your Customer)

### Archivo index.py
1. En el archivo `index.py` se recibe un evento que puede venir comunmente de un SNS o de API GATEWAY, desde el parámetro `event`. Aquí debemos tener ya definido como se llamará nuestra lambda, para posteriormente cambiar lo siguiente:
-  a) La linea `from src.engine_template_class import TemplateClassLogic` debe renombrarse con el nombre de la clase que corresponse a la definición de la lambda. Por ejemplo, para KYC podría ser algo como `from src.engine_kyc_class import KYCClassLogic`. Además, se debe renombrar el archivo `src/engine_template_class.py` y el nombre de esta clase con el nombre definido aquí (para el caso del ejemplo sería `src/engine_kyc_class.py` y dentro del archivo la clase sería `class KYCClassLogic`).

- b) En el diccionario `tables` deben añadirse todas las tablas que se usarán para extraer y guardar/modificar/eliminar data. Los nombres de las tablas deben ir en los archivos de variables de ambientes de la carpeta `env`. Por ejemplo, si queremos extraer o guardar data en alguna tabla de KYC (por ejemplo `BigData-Compliance-KnowYourCustomer`), y esta tabla existe en dev, entonces en el archivo `env/development.json` se deberia agregar lo siguiente: 
```json
{
  "KYC_TABLE": "BigData-Compliance-KnowYourCustomer"
}
```
Es decir, en un json se debe agregar la tabla asociada como variable a una llave, para luego en el código agregar la tabla al diccionario de tablas, donde los elementos se sacarán desde las variables de ambiente:
```python
tables = {
    'kyc_table': os.environ["KYC_TABLE"]
}
```
En cada ambiente (development, staging y production) se setean las variables de sus respectivos archivos (`env/{ambiente}.json`)

- c) La linea `engine = TemplateClassLogic(tables, path)`  debe cambiarse para importar la clase definida en el punto 1.a. Para KYC por ejemplo quedaría como `engine = KYCClassLogic(tables, path)` 

### Archivo engine_template_class.py

2. En el archivo `src/engine_template_class.py` se tienen 2 funciones claves:
- a) `handle_request`: Esta función se encarga de recibir el evento (y contexto como opcional) y se encarga de devolver una función asociada a un endpoint. Para el ejemplo de KYC, cuando se cumpla la confición `if self.path == "{nombre de la ruta a usar}"`, se procede a extraer los parámetros desde API GATEWAY que pueden venir por la url (`queryStringParameters`), el body, etc. La idea es extraer toda la información que se usará para la lógica del endpoint, y almacenarla en la variable `data`. Finalmente, la función devuelce 2 cosas:
 - La data
 - La función que usará dicha data. Esta función viene desde el archivo `engine_endpoints` que tocaremos mas adelante. 
 
Por ejemplo, si quisieramos guardar data en la tabla de KYC con una función llamada `put_data_in_kyc_table`, entonces el retorno de la función quedaría como: `return data, self.source_engine.put_data_in_kyc_table`.

- b) `handle_request`: Esta función es la que usa `index.py` para procesar la data, usando la función `handle_request` para saber que función y que data usar. Antes de pasar a lógica de los endpoints como tal, debemos explicar el archivo `utils.py`, de donde se exporta la función `respond`.

### utils.py

3. Aquí se encuentran 2 funciones sensillas: 
- a) `respond`: Esta función tiene la respuesta estandar del endpoint, cuya estructura es:
```json
{
    "statusCode": "código del string",
    "body": "data con la respuesta del endpont",
    "headers": {
        "Content-Type": "application/json",
    },
}
```
Donde el campo `body` se crea a partir de la función `log_structure`.

- b) `log_structure`: Esta función busca darle un formato a la respuesta de nuestros logs. Como estandar (similar al backend) se tienen 3 campos obligatorios:
- `msg`: Nombre del mensaje a devolver (por ejemplo `kyc_data_stored_successful` para saber que la data se guardó adecuadamente y  `kyc_data_stored_failed` para saber que falló algo en el endpoint)
- `time`: Fecha cuando se emite este evento.
- `info`: Aquí va la data a enviar para el backend. Este campo importa para saber cuando un endpoint falla, ya que debe contener un mensaje de tipo `Error try to ...`, caso contrario devolverá la data que corresponde.

La idea es rellenar el campo `name_of_lambda` con el nombre de la lambda.

### engine_endpoints.py

4. Esta clase tiene 3 funciones base:
- a) `_get_table`: Recibe el nombre de una tabla para instanciar el recurso de boto3 con el archivo `handlers/dynamo_hook`. Esta clase contiene todas las funciones necesarias para interactuar con tablas de Dynamo en AWS (los métodos de la clase estan detallados en el mismo archivo).
- b) `endpoint_error`: Es el cuerpo para cuando el endpoint falla en alguna parte del código. Al momento de capturar el error con esta función, se le puede pasar el mach_id o document_number para detectar de forma mas sencilla el error.
- c) `template_endpoint_function`: Esta función debe renombrase con la función que se creo en el punto 2.a .Aquí se crea la lógica que tendrá el endpoint para escritura o lectura con dynamo (por ejemplo extraer data de dynamo, corroborar que campos existan y esten bien nombrados, enviar resultados a algún servicio, etc). Idealmente el retorno de esta función debería contener un diccionario con al menos 2 campos: 
- machId o documentNumber: identificador único del usuario que pasa por el endpoint
- engine_response: Aquí va el cuerpo de la respuesta que se desea devolver.

### config.json
5. Una vez creada nuestra lógica, se debe agregar el nombre del endpoint y de la lambda al archivo `config.json` . En particular se debe cambiar lo siguiente:

- Para el campo `invokerConfiguration`: La esctrucuta varía dependiendo del archivo. El ejemplo esta seteado para usar el recurso `apigateway-v2`, sin embargo las demás configuraciones pueden verse en el README del repo [mach-lambda-pipeline-app](https://github.com/bcilabs/mach-lambda-pipeline-app)

- Para el campo `lambdaConfiguration`: Aquí se encuentra la configuracion de la lambda. El único campo obligatorio a cambiar es el campo `functionName` con el nombre del repositorio. Los demás campos son estandar y opcionales.

## Configurar tests (WIP)
6. Para los test se deben considerar 2 puntos antes de los tests como tal:
- Existe un archivo `env/test.json`que contiene las variables de ambiente para los test (como tablas por ejemplo)
- Los test también tienen su utils.py. En particular, la función `log_structure` tambien tiene el campo name_of_lambda que se debe rellenar con el nombre de la lambda.

Dicho esto, los tests tienen un archivo principal y una carpeta de recursos.

- `test_lambda_handler`: Esta clase contiene la definición del test de cada endpoint a testear. El formato es el siguiente:
```python
@mock_dynamodb
    def test_{nombre del endpoint a probar}_response(self):
        test_return, dynamo_data = test_endpoint_response(
            dynamo_tables.tables, 
            inputs.event 
            # , responses.dynamo_data_list_to_search -> only if endpoint modify a dynamo
        )

        assert test_return == responses.update_item
        # only if endpoint modify a dynamo
        '''
        if dynamo_data:
            for item in dynamo_data:
                print("A: ", item['dynamo_response'])
                print("B: ", item['output'])
                assert item['dynamo_response'] == item['output']
        '''
```

Para ejemplo del KYC, si quisieramos probar la función que escribe en dynamo podríamos llamarla como `test_put_data_in_kyc_table_response`. Esta función contiene otra función llamada test_endpoint_response 3 párametros: tablas de dynamo, input del endpoint y opcionalmente si la dynamo es modificada se le pasa una lista para esto.

Esta función toma estos parámetros, setea las variables de ambiente del archivo `env/test.json` y ejecuta el archivo index.py, retornando lo que devolvería el endpoint en la variable `test_return`. Adicionalmente, si una tabla en dynamo fue modificada, se devuelve la data de la dynamo resultante en la variable `dynamo_data`. Luego, el test compara lo obtenido en la variable test_return con el resultado que realmente debería dar (que se encuentra en el archivo responses) y si la tabla en dynamo es modificada adicionalemnte se debe testear la data de dynamo del endpoint vs lo que realmente debería quedar en la dynamo.

Esta función se basa en el contenido de 3 archivos que se encuentran en la carpeta `resources`y se explicaran a continuación
- `resources/dynamo_tables.py`: Aqui se instancias todas las tablas de dynamo en la lista `tables`. El cuerpo de cada tabla es el siguiente:
```python
{
    'table_name': 'nombre de la tabla',
    'attribute_dict': {
        #Aqui se instancia las primaryKey, SortKey, si la tabla tiene indices, etc.
        'field': ['S', 'primary'],
    },
    'data': [
        # Aquí se instancia la data inicial de dynamo. Cada registro es un diccionario.
        {
            "field": '123',
            "testField": 'testValue'
        }
    ]
}
```

- `resources/inputs.py`: Aquí se instancia la variable `event` que recibirá nuestro `index.py` . Para API GATEWAY Este evento debe contener al menos 4 elementos:
```python
event = {
    "path": "ruta dentro de API GATEWAY.", 
    "httpMethod": "GET, POST, etc", 
    "queryStringParameters": 'Si existen parámetros en la url se deben pasar como diccionario', 
    "body": 'si el input posee un body, se debe parsear el diccionario como string y luego pasar como campo a la variable event'
}
```

- `resources/responses.py`: Aquí van las respuestas de la API. Un ejemplo es el siguiente:
```python
update_item = {
    "statusCode": "código de la respuesta",
    "body": "data que se devolverá en el endpoint",
    "headers": {"Content-Type": "application/json"},
}
```

Adicionalmente, si el endpoint modifica alguna tabla en dynamo, entonces también se debe usar la función `dynamo_data_list_to_search`, que contiene una lista con todas las tablas y variables que se cambiaron y se desean consultar. Para esto, cada diccionario tiene 2 llaves: input y output.

`input`: Aquí va un diccionario con todas las variables que se desean consultar a dynamo. 
```python
{
    "table_name": 'nombre de la tabla',
    "key": 'llave primaria',
    "value": 'valor de la llave primaria a consultar'
}
```
Adicionalmente este diccionario acepta sort keys y global secondary index.

`output`: Lo que realmente deberia contener la dynamo como registro. Por ejemplo, 
```python
dynamo_result = {
    "machId": '123',
    "testField": 'testValue'
}   
```
Es decir, si consulte un registro de una tabla con `machId = 123`, deberia contener otro campo llamado `testField` con valor `testValue`.

#TODO: Falta integrar test para SNS.
## Crear pipeline

7. Una vez configurados los tests, solo falta crear el pipeline asociado a la lambda como tal. Para esto, es necesario crear un pr en el repo [mach-lambda-pipeline-app](https://github.com/bcilabs/mach-lambda-pipeline-app) agregando lo siguiente:

- a) `services.json`. Este es el archivo que maneja y crea los pipelines para las lambdas. En este archivo se debe agregar la lambda de la siguiente forma:

```json
"Nombre de la lambda": {
  "machEnvironment": ["data"],
  "requireTesting": true,
  "runtime": "py"
}
```

- b) roles-manager/index: Este es el indice para las policies que tendrá la lambda. Aquí se debe agregar la lambda de la siguiente forma:
  - En la sección de los import agregar la lambda como `import nombreDeLaLambdaPolicies from './nombre_de_la_lambda';`
  - Dentro de la variable `groupPolicies` agregar la lambda como 'nombre-de-la-lambda': nombreDeLaLambda, 
- c) roles-manager/nombre_de_la_lambda.json: Este es el archivo que contiene las policies de nuestra la lambda, es decir, a que recursos tendrá acceso nuestra lambda. Aquí se debe crear un archivo con el nombre de la lambda (en formato json) y agregar lo siguiente:

```ts
/* eslint-disable max-len, no-template-curly-in-string */
/**
 * This file defines the statements for the role of the lambda
 * Nombre de la lambda
 */
import { Fn } from 'aws-cdk-lib';
import {
  Effect,
  PolicyStatement,
} from 'aws-cdk-lib/aws-iam';

const nombreDeLaLambdaPolicies: PolicyStatement[] = [
  new PolicyStatement({
    actions: [
      ... /* --> Aqui van los recursos a los cuales queremos acceder, y que acciones queremos realizar dentro de dicho recurso, por ejemplo dynamodb:GetItem'*/
    ],
    effect: Effect.ALLOW,
    resources: [
      ... /* --> Aquí va el recurso como tal al cual queremos acceder, por ejemplo, Fn.sub('arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/BigData-Fraud-KnowYourCustomer'),*/
    ],
  }),
];

export default nombreDeLaLambdaPolicies;
```
Por ejemplo, en los comentarios del archivo typescript de arriba, en los comentarios se quiere hacer un getItem del recurso Dynamo a la tabla `BigData-Fraud-KnowYourCustomer`. 

Con esto, basta con enviar dicho pr al canal tech-clouds y esperar a que lo revisen y aprueben. 

Una vez listo, en el [CDK del mismo repo](https://github.com/bcilabs/mach-lambda-pipeline-app/actions/workflows/deploy-service.yml) se debe pinchar en el recuadro Run workflow y completar los campos que se piden, los cuales son
- `Name of lambda repository`: nombre del repositorio
- `Account group to deploy (eco, data or mach)`: para nuestro caso, el team es `data`.

![alt text](https://user-images.githubusercontent.com/92398641/211366579-fcf4ed25-418a-4531-a051-736156f0443c.png)

Una vez listo el paso 7, basta con probar en dev el endpoint (ya sea por APIGATEWAY, publicando un mensaje con SNS, etc) y viendo el resultado en CloudWatch.
