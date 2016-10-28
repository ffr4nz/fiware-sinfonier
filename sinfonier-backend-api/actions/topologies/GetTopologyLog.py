import falcon

from actions.ApiBase import ApiBase
from apiRequests.ResponsesHandler import ResponsesHandler
from clustering.mongo.MongoHandler import MongodbFactory
from clustering.storm.LogViewer import LogViewer
from error.ErrorHandler import TopologyInvalidId, MissingMandatoryFields, Error
from logger.Logger import logger
from utils.SinfonierConstants import Topology as TopologyConst
from requests.exceptions import HTTPError
class GetTopologyLog(ApiBase):
    @falcon.before(ApiBase.validate_params)
    def on_get(self, req, resp, id):
        topology_id = self.validated_params['id']
        try:
            topology = MongodbFactory.get_topology(topology_id)
            if topology is None:
                return ResponsesHandler.handle_404(resp, 'Topology not found')
            start = self.validated_params['start']
            length = self.validated_params['length']
            texts = LogViewer.get_log(topology[TopologyConst.FIELD_NAME],start=start,length=length)

            return ResponsesHandler.handle_200(resp, {'id': topology_id, 'log': texts})
        except HTTPError as ex:
            logger.error(ex.message)
            if ex.response.status_code == 400:
                return ResponsesHandler.handle_200(resp, {'id': topology_id, 'log': ''})
            else:
                return ResponsesHandler.handle_500(resp)
        except TopologyInvalidId as Ex:
            logger.error(Ex.message)
            return ResponsesHandler.handle_404(resp, Ex.message)
        except MissingMandatoryFields as Ex:
            logger.error(Ex.message)
            return ResponsesHandler.handle_409(resp)
        except Error as Ex:
            logger.critical(Ex.message)
            return ResponsesHandler.handle_500(resp)
        except Exception as Ex:
            logger.critical(Ex.message)
            return ResponsesHandler.handle_500(resp)
