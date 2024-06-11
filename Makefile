.PHONY: run local
# Run google cloud configuration
run:
	@export NER_DATABASE="google_cloud" &&\
	flask --app ner run -h 0.0.0.0 -p 1234 --debug

# Run Lior's local configuration
le:
	@export NER_DATABASE="le" &&\
	flask --app ner run -h 0.0.0.0 -p 1234 --debug