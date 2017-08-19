PLANTUML=java -jar /usr/local/share/plantuml/plantuml.jar
PY2PUML=../py2puml.py

DIAGRAMS=person.png calendar_clock.png py2puml.png

all: $(DIAGRAMS)

py2puml.puml:../py2puml.py
	$(PY2PUML) $< $@

py2puml-custom.puml:../py2puml.py
	$(PY2PUML) --config custom.ini $< $@

%.puml: %.py ../py2puml.py
	$(PY2PUML) $< $@

%.png: %.puml
	$(PLANTUML) $<
