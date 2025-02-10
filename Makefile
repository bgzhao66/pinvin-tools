# generate a list of tables to be converted from prefix 'pinvin_simp_ext' and suffix '2' to '7'
# and the primary table 'pinvin_simp'

PRIMARY_NAME = pinvin_simp
INPUT_TABLES = $(shell seq 2 7 | sed 's/.*/$(PRIMARY_NAME)_ext&/')

.SILENT:
all: primary_table predef_table extra_tables
	echo "All tables converted"

primary_table:
	echo "Converting to table $(PRIMARY_NAME)"
	python3 ./convert_to_pinvin.py --chinese_code --name $(PRIMARY_NAME) --input_tables $(PRIMARY_NAME)_ext $(INPUT_TABLES) > $(PRIMARY_NAME).dict.yaml

predef_table:
	echo "Converting to table $(PRIMARY_NAME)_ext"
	python3 ./convert_to_pinvin.py --name $(PRIMARY_NAME)_ext --pinyin_phrase --fluent > $(PRIMARY_NAME)_ext.dict.yaml

extra_tables:
	for table in $(shell seq 2 7); do \
		echo "Converting to table $(PRIMARY_NAME)_ext$${table}"; \
		python3 ./convert_to_pinvin.py words_$${table}.txt --exclude_pinyin_phrase --fluent --name $(PRIMARY_NAME)_ext$${table}  > $(PRIMARY_NAME)_ext$${table}.dict.yaml; \
	done

.PHONY: clean
clean:
	rm -f $(PRIMARY_NAME).dict.yaml $(PRIMARY_NAME)_ext*.dict.yaml
