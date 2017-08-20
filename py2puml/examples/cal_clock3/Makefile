PLANTUML=java -jar /usr/local/share/plantuml/plantuml.jar
PY2PUML=../../py2puml.py

all: calendar_clock.png

calendar_clock.puml: clock.py calendar.py calendar_clock.py  $(PY2PUML) py2puml.ini
	$(PY2PUML) -o $@ clock.py calendar.py calendar_clock.py

%.png : %.puml
	$(PLANTUML) $<
