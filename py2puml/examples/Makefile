PLANTUML=java -jar /usr/local/share/plantuml/plantuml.jar
PY2PUML=../py2puml.py
PY2UML_SOURCES = ../py2puml.py ../puml_generator.py ../code_info.py ../ast_visitor.py
DIAGRAMS=person.png py2puml.png py2puml_NS.png py2puml-custom.png cal_clock3

all: $(DIAGRAMS)

py2puml.puml:../py2puml.py
	$(PY2PUML) $< -o $@

py2puml_NS.puml:$(PY2UML_SOURCES)
	$(PY2PUML) -r .. -o $@ $^

py2puml-custom.puml:$(PY2UML_SOURCES)
	$(PY2PUML) --config custom.ini --root .. -o $@ $^

cal_clock3:
	cd $@ && $(MAKE)

%.puml: %.py ../py2puml.py
	$(PY2PUML) $< -o $@

%.png: %.puml
	$(PLANTUML) $<
