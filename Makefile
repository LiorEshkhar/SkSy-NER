.PHONY: default google_cloud le

run = flask --app ner run -h 0.0.0.0 -p 1234 --debug

# Run default configuration
default: google_cloud

# Run google cloud configuration
google_cloud:
	@export NER_DATABASE="google_cloud" &&\
	$(run)

# Run Lior's local configuration
le:
	@export NER_DATABASE="le" &&\
	$(run)