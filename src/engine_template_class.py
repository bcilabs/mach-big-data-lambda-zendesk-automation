from src.engine_endpoints import EngineEndpoints
from logger.engine_logger import get_logger
from src.utils import respond

class TemplateClassLogic:
    def __init__(self, tables, path):
        self.source_engine = EngineEndpoints()
        self.tables = tables
        self.path = path
        self.log = get_logger()

    def handle_request(self, event, context):
        """
        Parses the request received and executes a response accordingly
        the REST API
        """

        event, method = self.parse_event(event)
        if method:
            self.log.info("event_parsed_done", event)
            engine_resp = method(
                self.tables, event
            )
            return respond(engine_resp)
        return respond(event)

    def parse_event(self, event):
        self.log.info("parsing_event_started", event)

        #You have to set the logic from the different paths
        if self.path == "path-of-the-api":
            # You can get the parameters of the url with queryStringParameters format:
            # parameter = event["queryStringParameters"].get("name_of_the_parameter") if 'queryStringParameters' in event else ''

            #If you want to get the body (if your endpoint is POST), you can extract the event from body and loads with json library:
            # body = event['body']
            # body = body.replace("'", "\"")
            # body = json.loads(body)

            #Always return the function associated with the path
            try:
                #In data you have to parse the data you want from event variable
                data = event
                return data, self.source_engine.template_endpoint_function
            except Exception as e:
                self.log.info("parse_event_failed_invalid_endpoint")
                error = "Error try to parse the body: " + str(e)
                return self.source_engine.endpoint_error(error), None

        else:
            self.log.info("parse_event_failed_invalid_endpoint")
            error = "The endpoint of the request doesnt exist"
            return self.source_engine.endpoint_error(error), None
