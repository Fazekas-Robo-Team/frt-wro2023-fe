export PYTHONPYCACHEPREFIX = /tmp/cpython/

.PHONY: service
service: api gui

.PHONY: api
api:
	uvicorn api.main:api --host 0.0.0.0 --port 8000 --reload

.PHONY: gui
gui:
	npm --prefix gui run dev
