from flask import Blueprint, request
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from ..application.dto import SearchCommand
from ..application.search_service import SearchService
from .responses import SuccessResponse, ErrorResponse


def create_search_blueprint(search_service: SearchService) -> Blueprint:
    bp = Blueprint("hydro-find", __name__)

    @bp.route("/api/search", methods=["POST"])
    def search():
        data = request.get_json()
        query = data.get("query", "")
        
        
        print(f'{data} - {query}')
        
        try:
            command = SearchCommand(query=query)
            result = search_service.execute(command)

            return SuccessResponse(
                data={"task_id": result.task_id},
                request_id=result.task_id
            ).to_response()

        except ValueError as e:
            return ErrorResponse(
                message=str(e),
                status_code=400
            ).to_response()

        except Exception:
            return ErrorResponse(
                message="Internal server error",
                status_code=500
            ).to_response()

    @bp.route("/api/status/<task_id>", methods=["GET"])
    def get_status(task_id: str):
        try:
            result = search_service.get_status(task_id)

            if result is None:
                return ErrorResponse(
                    message="Task not found",
                    status_code=404
                ).to_response()

            return SuccessResponse(
                data={
                    "status": result.status,
                    "items": [
                        {
                            "article": item.article,
                            "name": item.name,
                            "quantity": item.quantity
                        }
                        for item in result.items
                    ]
                },
                request_id=task_id
            ).to_response()

        except Exception:
            return ErrorResponse(
                message="Internal server error",
                status_code=500
            ).to_response()

    @bp.route("/api/health", methods=["GET"])
    def get_health():
        return SuccessResponse(
            data={"status": "ОК",},
            status_code=200
        ).to_response()

    return bp
