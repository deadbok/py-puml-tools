PLANTUML=java -jar /usr/local/share/plantuml/plantuml.jar
PY2PUML=../py2puml.py
PY2UML_SOURCES = ../py2puml.py ../puml_generator.py ../code_info.py ../ast_visitor.py
DIAGRAMS=person.png py2puml.png py2puml_NS.png py2puml-custom.png cal_clock3
MORE_DIAGRAMS=  dbdia2sql.py.png \
		dbpuml2sql.png \
		dbsql2puml.png
MORE_EXAMPLES=  person.puml \
		example_globals_NS.puml \
		example_globals.puml \
		example.puml

all: $(DIAGRAMS) $(MORE_DIAGRAMS) $(MORE_EXAMPLES)

py2puml.puml:../py2puml.py
	$(PY2PUML) $< -o $@

py2puml_NS.puml:$(PY2UML_SOURCES)
	$(PY2PUML) -r .. -o $@ $^

py2puml-custom.puml:$(PY2UML_SOURCES) custom.ini
	$(PY2PUML) --config custom.ini --root .. -o $@ $(PY2UML_SOURCES)

example_globals.puml: example.py globals.ini
	$(PY2PUML) -c globals.ini  -o $@ $<

example_globals_NS.puml: example.py globals.ini
	$(PY2PUML) -c globals.ini  -r .. -o $@ $<

DBPUML2SQL_SOURCES = ../../dbpuml2sql/dbpuml2sql.py \
                     ../../dbpuml2sql/__init__.py \
                     ../../dbpuml2sql/pumlreader.py \
                     ../../dbpuml2sql/table.py \
                     ../../dbpuml2sql/test_Table.py
DBPUML2SQL_OPTIONS =  # -r ../../dbpuml2sql
dbpuml2sql.puml:$(PY2UML_SOURCES) $(DBPUML2SQL_SOURCES) dbpuml2sql.ini
	$(PY2PUML) -c dbpuml2sql.ini $(DBPUML2SQL_OPTIONS) -o $@ $(DBPUML2SQL_SOURCES)

DBSQL2PUML_SOURCES = ../../dbsql2puml/dbsql2puml.py \
                     ../../dbsql2puml/sql2puml.py \
                     ../../dbsql2puml/sqlparsetables.py
DBSQL2PUML_OPTIONS =  # -r ../../dbsql2puml
dbsql2puml.puml:$(PY2UML_SOURCES) $(DBSQL2PUML_SOURCES) dbsql2puml.ini
	$(PY2PUML) -c dbsql2puml.ini $(DBSQL2PUML_OPTIONS) -o $@ $(DBSQL2PUML_SOURCES)

cal_clock3: $(PY2UML_SOURCES)
	cd $@ && $(MAKE)

%.puml: %.py ../py2puml.py$ (PY2UML_SOURCES)
	$(PY2PUML) $< -o $@

%.png: %.puml
	$(PLANTUML) $<
